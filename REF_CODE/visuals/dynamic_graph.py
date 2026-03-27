from nicegui import ui
from data_manager import data_manager
import re

# Try to load prerequisites, else empty
try:
    from build_structure_auto import PREREQUISITES
except ImportError:
    PREREQUISITES = {}

def render_dynamic_tree(container, student_state, on_click=None):
    """
    Vẽ đồ thị lực (Force-Directed Graph) với cấu trúc Logically Hierarchical.
    Cập nhật: Hiển thị nhãn chi tiết cho bài học.
    """
    nodes = []
    links = []
    
    # 1. Lấy dữ liệu bài học
    concepts = data_manager.get_all_concepts() 
    
    # Structure to group
    structure = {}
    
    # Colors
    root_color = "#2C3E50" 
    chapter_colors = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", 
        "#F7DC6F", "#BB8FCE", "#F1948A", "#85C1E9", "#82E0AA"
    ]
    
    # Regex
    chapter_pattern = re.compile(r"(ch[uương]+[_ ]?(\d+))", re.IGNORECASE)
    lesson_pattern = re.compile(r"(ti[eết]+[_ ]?(\d+))", re.IGNORECASE)

    # --- A. ROOT NODE ---
    root_id = "ROOT_SUBJECT"
    nodes.append({
        "id": root_id,
        "name": "MÔN HỌC:\nTMĐT",
        "symbolSize": 60,
        "itemStyle": {"color": root_id, "color": root_color},
        "category": 0,
        "label": {"show": True, "fontWeight": "bold", "fontSize": 14, "color": "white"},
        "fixed": True,
        "x": 550, 
        "y": 300
    })

    # --- B. PROCESS LESSONS ---
    for concept in concepts:
        c_id = concept['id']
        c_name = concept['name']
        
        # Parse Info
        parse_target = c_name 
        chap_match = chapter_pattern.search(parse_target)
        less_match = lesson_pattern.search(parse_target)
        
        if chap_match:
            chap_num = int(chap_match.group(2))
            chap_key = f"CHAPTER_{chap_num}"
            chap_display = f"Chương {chap_num}"
        else:
            chap_num = 999
            chap_key = "CHAPTER_OTHER"
            chap_display = "Tài nguyên"

        if less_match:
            less_num = int(less_match.group(2))
            # Tạo tên ngắn gọn: "Tiết 1: <Tên bài>"
            # Loại bỏ phần "Chương... Tiết..." trong tên gốc để lấy nội dung chính
            # Giả sử tên là "Chương 1 Tiết 1 Khái niệm..." -> lấy "Khái niệm..."
            # Simple heuristic: lấy phần sau cùng của split('_') hoặc khoảng trắng
            # Cách tốt hơn: Xóa phần khớp regex
            
            clean_name = chapter_pattern.sub("", c_name)
            clean_name = lesson_pattern.sub("", clean_name)
            clean_name = clean_name.replace("_", " ").strip()
            # Xóa các ký tự thừa
            clean_name = re.sub(r"^[^\w]+", "", clean_name) 
            
            display_name = f"Tiết {less_num}: {clean_name[:20]}..." if len(clean_name) > 20 else f"Tiết {less_num}: {clean_name}"
        else:
            less_num = 999
            display_name = c_name[:15] + "..."
            
        if chap_key not in structure:
            structure[chap_key] = {
                "name": chap_display,
                "num": chap_num,
                "lessons": []
            }
        
        # Mastery
        mastery = student_state.get_mastery(c_id)
        if mastery >= 0.8: color = "#4caf50" 
        elif mastery >= 0.4: color = "#ff9800" 
        else: color = "#bdc3c7" # Grey
        
        # Current
        size = 15
        is_current = (c_id == student_state.current_concept_id)
        if is_current:
            color = "#2980b9" # Blue
            size = 25
            
        # Lesson Node
        nodes.append({
            "id": c_id,
            "name": display_name, # Tên hiển thị trên graph
            "full_name": c_name,  # (Custom field, không hiện nhưng có thể dùng nếu cần)
            "symbolSize": size,
            "itemStyle": {"color": color},
            "category": 2,
            "value": mastery,
            # Show label now!
            "label": {
                "show": True, 
                "position": "right", 
                "fontSize": 10,
                "formatter": "{b}" # Show 'name'
            },
            # Tooltip shows full name
            "tooltip": {"formatter": f"{c_name}<br>Mastery: {int(mastery*100)}%"}
        })
        
        structure[chap_key]["lessons"].append({
            "id": c_id,
            "num": less_num
        })

    # --- C. CREATE CHAPTER NODES ---
    sorted_chapters = sorted(structure.items(), key=lambda x: x[1]['num'])
    
    prev_chapter_node = None
    
    for idx, (chap_key, data) in enumerate(sorted_chapters):
        color = chapter_colors[idx % len(chapter_colors)]
        
        nodes.append({
            "id": chap_key,
            "name": data['name'],
            "symbolSize": 40,
            "itemStyle": {"color": color},
            "category": 1,
            "label": {"show": True, "fontWeight": "bold", "fontSize": 12}
        })
        
        # Link: ROOT -> Chapter
        links.append({
            "source": root_id,
            "target": chap_key,
            "lineStyle": {"width": 3, "color": "#7f8c8d"}
        })
        
        # Link: Chapter -> Chapter loop
        if prev_chapter_node:
             links.append({
                "source": prev_chapter_node,
                "target": chap_key,
                "lineStyle": {"width": 1, "type": "dashed", "color": "#bdc3c7", "curveness": 0.3}
            })
        prev_chapter_node = chap_key

        sorted_lessons = sorted(data['lessons'], key=lambda x: x['num'])
        prev_lesson_id = None
        
        for lesson in sorted_lessons:
            l_id = lesson['id']
            
            # Link: Chapter -> Lesson
            links.append({
                "source": chap_key,
                "target": l_id,
                "lineStyle": {"width": 2, "color": color, "opacity": 0.5}
            })
            
            # Link: Sequence
            if prev_lesson_id:
                links.append({
                    "source": prev_lesson_id,
                    "target": l_id,
                    "lineStyle": {"width": 1, "color": "#bdc3c7", "type": "dotted"}
                })
            prev_lesson_id = l_id

    # --- MAPPING FOR CLICKS ---
    name_to_id = {}
    for n in nodes:
        name_to_id[n['name']] = n['id']

    # 3. ECharts Config
    options = {
        "title": {
            "text": "Bản đồ Tri thức",
            "bottom": "0%",
            "left": "center"
        },
        "tooltip": {},
        "legend": {
            "data": [{"name": "Môn học"}, {"name": "Chương"}, {"name": "Bài học"}],
            "top": "top",
            "left": "left"
        },
        "series": [
            {
                "type": "graph",
                "layout": "force",
                "categories": [
                    {"name": "Môn học"},
                    {"name": "Chương"},
                    {"name": "Bài học"}
                ],
                "force": {
                    "repulsion": 350,
                    "gravity": 0.1,
                    "edgeLength": [50, 120],
                    "layoutAnimation": True
                },
                "data": nodes,
                "links": links,
                "roam": True,
                "label": {
                    "position": "right",
                    "formatter": "{b}"
                },
                "lineStyle": {
                    "curveness": 0.1
                },
                "emphasis": {
                    "focus": "adjacency",
                    "scale": True,
                    "label": {"show": True}
                }
            }
        ]
    }
    
    
    with container:
        chart = ui.echart(options).classes('w-full h-full')
        
        def handle_click(e):
            print(f"DEBUG: Graph Click Event Args: {e.args}")
            
            # 1. Try dataIndex (Most reliable)
            if 'dataIndex' in e.args:
                idx = e.args['dataIndex']
                if isinstance(idx, int) and 0 <= idx < len(nodes):
                    clicked_node = nodes[idx]
                    print(f"DEBUG: Matched dataIndex {idx} to Node {clicked_node['id']}")
                    if "CHAPTER_" not in clicked_node['id'] and "ROOT_" not in clicked_node['id']:
                        on_click(clicked_node['id'])
                    return

            # 2. Fallback to Name
            if 'name' in e.args:
                clicked_name = e.args['name']
                if clicked_name in name_to_id:
                     clicked_id = name_to_id[clicked_name]
                     print(f"DEBUG: Matched Name '{clicked_name}' to ID '{clicked_id}'")
                     if "CHAPTER_" not in clicked_id and "ROOT_" not in clicked_id:
                         on_click(clicked_id)
                else:
                    print(f"DEBUG: Name '{clicked_name}' not found in map")
            else:
                print("DEBUG: No 'name' or 'dataIndex' in event args")
        
        # Explicitly request 'dataIndex' and 'name'
        chart.on('click', handle_click, ['dataIndex', 'name', 'componentType'])
