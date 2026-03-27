import os
import json
import requests

from gemini_helper import get_chat_model
import google.generativeai as genai

def infer_edges_with_gemini(micro_nodes):
    """Gọi Gemini để dò tìm mối quan hệ tiên quyết (Prerequisite Edges) giữa các bài học"""
    
    # Rút gọn data gửi lên LLM để tiết kiệm token, chỉ gửi id và title
    nodes_summary = [{"id": n["id"], "title": n["title"]} for n in micro_nodes]
    nodes_json_str = json.dumps(nodes_summary, ensure_ascii=False, indent=2)

    prompt = f"""
    Bạn là một chuyên gia thiết kế lộ trình học tập. Tôi có danh sách các bài học (nodes) của một môn học như sau:
    {nodes_json_str}

    Nhiệm vụ của bạn: 
    Hãy xác định các mối quan hệ tiên quyết (Prerequisite) BẮT BUỘC giữa các bài học này.
    Bài học nào (source) bắt buộc phải học trước để có thể hiểu được bài học kia (target)?
    (Lưu ý: Không tạo chu trình lặp vòng, đồ thị phải có hướng đi tới).

    Hãy trả về KẾT QUẢ ĐÚNG CHUẨN ĐỊNH DẠNG JSON. Không giải thích thêm.
    Cấu trúc JSON yêu cầu:
    {{
      "edges": [
        {{
          "source": "id_bài_phải_học_trước",
          "target": "id_bài_học_sau",
          "reason": "Lý do ngắn gọn (1 câu) tại sao lại có sự phụ thuộc này"
        }}
      ]
    }}
    """

    print("🤖 Đang nhờ Gemini phân tích logic tiên quyết (Prerequisite Logic)...")
    model = get_chat_model()
    if not model:
        print("Lỗi: Không tìm thấy API Key Gemini.")
        return None

    try:
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
        )
        response = model.generate_content(prompt, generation_config=generation_config)
        if not response.parts:
            print("Lỗi: Gemini API trả về kết quả rỗng.")
            return None
            
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())
    except json.JSONDecodeError as je:
        print(f"Lỗi parse JSON: {je}\nNội dung trả về: {response.text}")
        return None
    except Exception as e:
        print(f"Lỗi khi gọi Gemini: {e}")
        return None

def build_edges_for_user(user_id):
    """Đọc file JSON cũ -> Suy luận Edges -> Cập nhật JSON"""
    
    # 1. Đọc file JSON đã tạo ở Step 1
    json_path = f"user_data/{user_id}/{user_id}_knowledge_tree.json"
    if not os.path.exists(json_path):
        print(f"❌ Không tìm thấy file {json_path}. Vui lòng chạy step1_build_tree.py trước!")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        tree_data = json.load(f)

    micro_nodes = tree_data.get("micro_nodes", [])
    if not micro_nodes:
        print("❌ Cây tri thức không có micro_nodes nào để phân tích.")
        return

    # 2. Gọi AI suy luận Edges
    edges_data = infer_edges_with_gemini(micro_nodes)

    if edges_data and "edges" in edges_data:
        # 3. Cập nhật vào tree_data
        tree_data["edges"] = edges_data["edges"]
        
        # 4. Lưu đè lại file JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(tree_data, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Đã tạo Cạnh (Edges) thành công! Cập nhật dữ liệu tại: {json_path}")
        print(f"📊 Thống kê: Tạo được {len(tree_data['edges'])} mối quan hệ tiên quyết.")
    else:
        print("❌ Quá trình tạo Cạnh thất bại.")

# --- CHẠY THỬ NGHIỆM ---
if __name__ == "__main__":
    build_edges_for_user(user_id="sv01")