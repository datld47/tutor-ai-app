import os
import json
from pyvis.network import Network

def visualize_knowledge_tree(user_id):
    """Đọc file JSON và vẽ Cây Tri Thức ra HTML bằng PyVis (VisJS)"""
    
    json_path = f"user_data/{user_id}/{user_id}_knowledge_tree.json"
    if not os.path.exists(json_path):
        print(f"❌ Không tìm thấy file {json_path}. Hãy chạy Step 1 và Step 2 trước.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        tree_data = json.load(f)

    print(f"🎨 Đang vẽ Cây Tri Thức cho {user_id}...")

    # Khởi tạo bảng vẽ PyVis (Directed Graph - Đồ thị có hướng)
    # Bật tính năng physics để các nút tự động đẩy nhau ra cho đẹp. Dùng "remote" cdn_resources để tránh lỗi thiếu file "lib/bindings/utils.js"
    net = Network(height="1200px", width="100%", directed=True, bgcolor="#1e1e1e", font_color="white", cdn_resources="remote")
    net.force_atlas_2based() # Thuật toán layout nhìn tự nhiên giống mạng nơ-ron

    # 1. Vẽ các Chương (Macro Nodes)
    for macro in tree_data.get("macro_nodes", []):
        net.add_node(
            macro["id"], 
            label=macro["title"], 
            shape="box", # Chương làm hình vuông
            color="#E3A869", # Màu vàng nổi bật
            size=30,
            font={"size": 20, "bold": True}
        )

    # 2. Vẽ các Bài học (Micro Nodes)
    micro_nodes = tree_data.get("micro_nodes", [])
    for micro in micro_nodes:
        # Tooltip hiện ra khi di chuột vào nút
        hover_text = f"Nội dung: {micro.get('content', '')}\nĐộ khó (Alpha): {micro.get('alpha_base', 10)}"
        
        net.add_node(
            micro["id"], 
            label=micro["title"], 
            shape="dot", # Bài học làm hình tròn
            color="#4CAF50", # Màu xanh lá
            title=hover_text, # Hiển thị khi hover
            size=15
        )
        
        # Tạo đường nối nét đứt (Dashed Edge) từ Chương đến Bài học
        net.add_edge(
            micro["parent_macro"], 
            micro["id"], 
            color="#555555", 
            dashes=True,
            arrows="to"
        )

    # 3. Vẽ các đường Tiên quyết (Prerequisite Edges) từ Step 2
    edges = tree_data.get("edges", [])
    for edge in edges:
        net.add_edge(
            edge["source"], 
            edge["target"], 
            color="#FF5722", # Mũi tên màu cam/đỏ thể hiện sự bắt buộc
            width=2,
            title=edge.get("reason", "Phụ thuộc tiên quyết"), # Hover vào dây sẽ thấy lý do
            arrows="to"
        )

    # Lấy tên môn học làm tiêu đề file
    course_name = tree_data.get("course_name", "Knowledge Tree")
    
    # Lưu file HTML
    output_html = f"user_data/{user_id}/{user_id}_visual_tree.html"
    net.save_graph(output_html)
    
    print(f"✅ Đã tạo xong giao diện! Hãy mở file này trên trình duyệt web: {os.path.abspath(output_html)}")

# --- CHẠY THỬ NGHIỆM ---
if __name__ == "__main__":
    visualize_knowledge_tree(user_id="sv01")