import os
import json
import google.generativeai as genai

from gemini_helper import get_chat_model

def extract_nodes_with_gemini(document_text):
    """Gọi Gemini để trích xuất cấu trúc Cây tri thức từ văn bản"""
    
    prompt = f"""
    Bạn là một chuyên gia Khoa học Dữ liệu Giáo dục. Tôi có một tài liệu học tập dưới đây.
    Hãy phân rã tài liệu này thành một Cây Tri Thức và trả về kết quả ĐÚNG CHUẨN ĐỊNH DẠNG JSON. Không giải thích gì thêm, chỉ trả về JSON.
    
    Yêu cầu JSON có các trường sau:
    1. "course_name": Tên môn học
    2. "macro_nodes": Mảng các chương lớn. Mỗi phần tử gồm "id" (vd: m1, m2) và "title".
    3. "micro_nodes": Mảng các bài học nhỏ/khái niệm. Mỗi phần tử gồm:
       - "id": vd c1.1, c1.2
       - "parent_macro": id của macro_node chứa nó.
       - "title": Tên bài học.
       - "content": Tóm tắt nội dung bài học đó (khoảng 3-4 câu).
       - "alpha_base": Độ khó sinh học (từ 10 đến 30). Nếu là khái niệm dễ/lý thuyết thì cho 10-15. Nếu là phân tích/bài tập/ứng dụng thì cho 20-30.
    4. "assess_nodes": Mảng các bài kiểm tra chốt chặn. Mỗi phần tử gồm:
       - "id": vd a1.1, a1.2 (tương ứng với micro_node)
       - "target_micro": id của micro_node mà nó kiểm tra.
       - "theta_pass": 0.6 (mặc định)
       - "questions": Mảng gồm 2 câu hỏi trắc nghiệm khách quan để kiểm tra. Mỗi câu có "question", "options" (mảng 4 lựa chọn), và "answer" (đáp án đúng, vd "A").

    NỘI DUNG TÀI LIỆU:
    -------------------
    {document_text}
    -------------------
    """

    print("🤖 Đang nhờ Gemini phân rã tài liệu thành các Đỉnh (Nodes)...")
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
            print("Lỗi: Gemini API trả về kết quả rỗng (có thể bị chặn bởi an toàn).")
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

def build_tree_for_user(user_id, document_text):
    """Luồng xử lý chính: Đọc nội dung -> Gọi AI -> Lưu JSON cho User"""
    
    # 1. Gọi AI trích xuất
    tree_data = extract_nodes_with_gemini(document_text)
    
    if tree_data:
        # Gắn thêm user_id vào hệ thống
        tree_data["user_id"] = user_id
        
        # 2. Lưu thành file JSON cục bộ
        save_dir = os.path.join(os.getcwd(), "user_data", user_id)
        os.makedirs(save_dir, exist_ok=True)
        
        save_path = os.path.join(save_dir, f"{user_id}_knowledge_tree.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(tree_data, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Đã tạo Cây Tri Thức thành công! Dữ liệu lưu tại: {save_path}")
        print(f"📊 Thống kê: {len(tree_data.get('macro_nodes', []))} Chương lớn, {len(tree_data.get('micro_nodes', []))} Bài học nhỏ.")
        return save_path, tree_data
    else:
        print("❌ Quá trình tạo cây thất bại.")
        return None, None

if __name__ == "__main__":
    test_doc_path = "test_doc.txt"
    if os.path.exists(test_doc_path):
        with open(test_doc_path, "r", encoding="utf-8") as f:
            text = f.read()[:5000]
        build_tree_for_user(user_id="sv01", document_text=text)
    else:
        print(f"Không tìm thấy file {test_doc_path} để test. Tạo 1 file test_doc.txt để thử nghiệm độc lập.")
