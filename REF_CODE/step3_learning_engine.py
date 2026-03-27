import os
import json
from datetime import datetime

# --- CÁC THAM SỐ TOÁN HỌC TỪ BÀI BÁO BIO-PKT ---
THETA_PASS = 0.6        # Ngưỡng qua môn
LAMBDA_PENALTY = 2.0    # Hệ số phạt nếu hổng kiến thức nền (lambda)
GAMMA_LEARN = 0.5       # Hệ số cập nhật điểm (EMA)

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def init_user_state(user_id, tree_data):
    """Khởi tạo trạng thái ban đầu cho người học nếu chưa có"""
    state_path = f"user_data/{user_id}/{user_id}_state.json"
    
    if os.path.exists(state_path):
        return load_json(state_path)
    
    print(f"🌱 Khởi tạo trạng thái ban đầu cho {user_id}...")
    state = {
        "user_id": user_id,
        "current_energy": 100.0,  # Bắt đầu với 100% năng lượng
        "knowledge_states": {}
    }
    
    # Khởi tạo điểm 0 cho tất cả micro_nodes
    for node in tree_data.get("micro_nodes", []):
        state["knowledge_states"][node["id"]] = {
            "k_score": 0.0,
            "last_updated": None
        }
        
    save_json(state_path, state)
    return state

def calculate_alpha_cost(node_id, tree_data, user_state):
    """
    Toán học hóa công thức: 
    alpha_t = alpha_base * (1 + lambda * sum(max(0, theta - k[parent])))
    """
    # 1. Lấy alpha_base của nút hiện tại
    micro_nodes = {n["id"]: n for n in tree_data["micro_nodes"]}
    target_node = micro_nodes.get(node_id)
    if not target_node:
        return 0
    
    alpha_base = target_node.get("alpha_base", 10)
    
    # 2. Tìm các nút cha (Prerequisite Parents) từ tập edges
    edges = tree_data.get("edges", [])
    parent_ids = [edge["source"] for edge in edges if edge["target"] == node_id]
    
    # 3. Tính hàm phạt (Penalty)
    penalty_sum = 0.0
    for pid in parent_ids:
        k_score = user_state["knowledge_states"][pid]["k_score"]
        # Nếu điểm cha < 0.6 => Phát sinh lỗ hổng dương => Phạt!
        gap = max(0, THETA_PASS - k_score)
        penalty_sum += gap
        
    alpha_t = alpha_base * (1 + LAMBDA_PENALTY * penalty_sum)
    return round(alpha_t, 2)

def simulate_learning(user_id, target_node_id, quiz_score):
    """Mô phỏng 1 lượt học: Tính năng lượng tiêu hao -> Làm Quiz -> Cập nhật trạng thái"""
    
    tree_path = f"user_data/{user_id}/{user_id}_knowledge_tree.json"
    state_path = f"user_data/{user_id}/{user_id}_state.json"
    
    tree_data = load_json(tree_path)
    if not tree_data:
        print("❌ Lỗi: Không tìm thấy Knowledge Tree.")
        return
        
    user_state = init_user_state(user_id, tree_data)
    
    print(f"\n--- 🚀 MÔ PHỎNG HỌC BÀI: {target_node_id} ---")
    print(f"Năng lượng hiện tại: {round(user_state['current_energy'], 2)} / 100")
    
    # 1. Tính mức tiêu hao năng lượng alpha
    alpha_t = calculate_alpha_cost(target_node_id, tree_data, user_state)
    print(f"⚡ Mức tiêu hao dự kiến (alpha_t): {alpha_t}")
    
    # Kích hoạt chặn an toàn (Hard-Constraint của MPC)
    if user_state["current_energy"] - alpha_t < 0:
        print(f"🚨 CẢNH BÁO: Năng lượng không đủ để học bài này. Hệ thống yêu cầu bạn nghỉ ngơi hoặc ôn lại bài cũ (Restorative Mode)!")
        return
        
    # 2. Trừ năng lượng
    user_state["current_energy"] -= alpha_t
    
    # 3. Cập nhật điểm k_t bằng EMA
    old_k = user_state["knowledge_states"][target_node_id]["k_score"]
    new_k = (1 - GAMMA_LEARN) * old_k + GAMMA_LEARN * quiz_score
    user_state["knowledge_states"][target_node_id]["k_score"] = round(new_k, 2)
    user_state["knowledge_states"][target_node_id]["last_updated"] = datetime.now().isoformat()
    
    # 4. Lưu lại
    save_json(state_path, user_state)
    
    print(f"✅ Đã học xong! Năng lượng còn lại: {round(user_state['current_energy'], 2)}")
    print(f"📈 Điểm kiến thức (k_t) của {target_node_id} tăng từ {old_k} -> {round(new_k, 2)}")

# --- CHẠY THỬ NGHIỆM ---
if __name__ == "__main__":
    # GIẢ LẬP KỊCH BẢN HỌC TẬP CỦA SV01
    
    # Lần 1: SV01 học bài đầu tiên c1.1 và được 0.8 điểm (80%)
    simulate_learning(user_id="sv01", target_node_id="c1.1", quiz_score=0.8)
    
    # Lần 2: SV01 học tiếp bài c1.2 (có điều kiện tiên quyết là c1.1). 
    # Vì c1.1 điểm đã cao (0.8 > 0.6) nên không bị phạt năng lượng.
    simulate_learning(user_id="sv01", target_node_id="c1.2", quiz_score=0.9)
    
    # THỬ NGHIỆM HÀM PHẠT: Giả sử học bài c1.3 nhưng c1.2 lại bị hổng (đang giả lập điểm c1.2 thấp)
    # Bạn có thể tự đổi quiz_score ở trên thành 0.2 để xem hàm phạt alpha_t tăng vọt như thế nào.