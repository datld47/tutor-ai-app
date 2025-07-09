import docx
import json
import os
import re
import unicodedata

def sanitize_filename(name):
    """
    Loại bỏ các ký tự không hợp lệ và khoảng trắng khỏi tên để tạo tên file an toàn.
    Ví dụ: "Thương mại điện tử" -> "Thuong_mai_dien_tu"
    """
    s = unicodedata.normalize('NFD', name)
    s = re.sub(r'[\u0300-\u036f]', '', s)
    s = s.replace('đ', 'd').replace('Đ', 'D')
    s = re.sub(r'[^\w\s-]', '', s).strip()
    s = re.sub(r'[-\s]+', '_', s)
    return s

def process_docx_to_json(docx_path, output_folder):
    """
    Đọc một file DOCX có cấu trúc, phân tích và tạo ra một file course_*.json.
    
    Args:
        docx_path (str): Đường dẫn đến file .docx đầu vào.
        output_folder (str): Thư mục để lưu file JSON đầu ra.

    Returns:
        tuple: (True, output_path) nếu thành công, (False, error_message) nếu thất bại.
    """
    try:
        doc = docx.Document(docx_path)
        
        course_data = {
            "course_name": "Chưa xác định",
            "course_language": "Không",
            "task_list_title": "Chi tiết danh sách bài tập của từng buổi",
            "sessions": []
        }
        
        current_session = None
        current_exercise = None
        exercise_id_counter = 1

        for para in doc.paragraphs:
            if not para.text.strip():
                continue

            style_name = para.style.name

            if para.text.lower().startswith("tên môn:"):
                course_data["course_name"] = para.text[len("tên môn:"):].strip()
                continue
            
            if para.text.lower().startswith("ngôn ngữ:"):
                course_data["course_language"] = para.text[len("ngôn ngữ:"):].strip().lower()
                continue

            if 'Heading 1' in style_name:
                current_session = {
                    "title": para.text.strip(),
                    "exercises": []
                }
                course_data["sessions"].append(current_session)
                current_exercise = None
                continue

            if 'Heading 2' in style_name:
                if current_session is None:
                    return (False, "Lỗi cấu trúc: Tìm thấy 'Tên bài' (Heading 2) nhưng chưa có 'Buổi học' (Heading 1).")

                current_exercise = {
                    "id": exercise_id_counter,
                    "title": para.text.strip(),
                    "description": "",
                    "status": "✗",
                    "score": 0,
                    "image": [],
                    "guidance": []
                }
                current_session["exercises"].append(current_exercise)
                exercise_id_counter += 1
                continue
            
            # ===== BẮT ĐẦU THAY ĐỔI TỪ ĐÂY =====
            # 4. Phân tích nội dung (description) và danh sách (list)
            # Sửa đổi điều kiện để bao gồm cả style của list, ví dụ 'List Paragraph'
            if 'Normal' in style_name or 'List Paragraph' in style_name:
                if current_exercise is not None:
                    line_text = para.text.strip()
                    
                    # Nếu là một list item, thêm dấu gạch đầu dòng cho rõ ràng
                    if 'List Paragraph' in style_name:
                        current_exercise["description"] += "- " + line_text + "\n"
                    else:
                        current_exercise["description"] += line_text + "\n"
                else:
                    # Bỏ qua các đoạn text thừa
                    pass
            # ===== KẾT THÚC THAY ĐỔI =====

        # Dọn dẹp description (xóa dấu xuống dòng thừa ở cuối)
        for session in course_data["sessions"]:
            for ex in session["exercises"]:
                ex["description"] = ex["description"].strip()

        if course_data["course_name"] == "Chưa xác định":
            return (False, "Không tìm thấy 'Tên môn:' trong file DOCX.")
            
        sanitized_name = sanitize_filename(course_data["course_name"])
        output_filename = f"course_{sanitized_name}.json"
        output_path = os.path.join(output_folder, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
            
        return (True, output_path)

    except Exception as e:
        return (False, f"Đã xảy ra lỗi: {str(e)}")