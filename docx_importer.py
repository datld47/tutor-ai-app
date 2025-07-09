import docx
import json
import os
import re
import unicodedata # <--- THÊM DÒNG NÀY

def sanitize_filename(name):
    """
    Loại bỏ các ký tự không hợp lệ và khoảng trắng khỏi tên để tạo tên file an toàn.
    Ví dụ: "Thương mại điện tử" -> "Thuong_mai_dien_tu"
    """
    # Chuyển thành chữ không dấu
    # SỬA DÒNG BÊN DƯỚI
    s = unicodedata.normalize('NFD', name)
    s = re.sub(r'[\u0300-\u036f]', '', s)
    
    # Thay thế 'đ' và 'Đ'
    s = s.replace('đ', 'd').replace('Đ', 'D')
    # Loại bỏ các ký tự đặc biệt
    s = re.sub(r'[^\w\s-]', '', s).strip()
    # Thay thế khoảng trắng và gạch nối bằng gạch dưới
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
        
        # Cấu trúc JSON cơ bản
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
            # Bỏ qua các đoạn trống
            if not para.text.strip():
                continue

            style_name = para.style.name

            # 1. Phân tích thông tin chung của môn học
            if para.text.lower().startswith("tên môn:"):
                course_data["course_name"] = para.text[len("tên môn:"):].strip()
                continue
            
            if para.text.lower().startswith("ngôn ngữ:"):
                course_data["course_language"] = para.text[len("ngôn ngữ:"):].strip().lower()
                continue

            # 2. Phân tích các session (Buổi học)
            if 'Heading 1' in style_name:
                current_session = {
                    "title": para.text.strip(),
                    "exercises": []
                }
                course_data["sessions"].append(current_session)
                current_exercise = None # Reset bài tập khi có buổi mới
                continue

            # 3. Phân tích các exercise (Bài tập)
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
            
            # 4. Phân tích nội dung (description)
            if 'Normal' in style_name:
                if current_exercise is not None:
                    # Nối vào description của bài tập hiện tại
                    current_exercise["description"] += para.text.strip() + "\n"
                else:
                    # Có thể là một đoạn text thừa, bỏ qua
                    pass

        # Dọn dẹp description (xóa dấu xuống dòng thừa ở cuối)
        for session in course_data["sessions"]:
            for ex in session["exercises"]:
                ex["description"] = ex["description"].strip()

        # Tạo tên file output
        if course_data["course_name"] == "Chưa xác định":
            return (False, "Không tìm thấy 'Tên môn:' trong file DOCX.")
            
        sanitized_name = sanitize_filename(course_data["course_name"])
        output_filename = f"course_{sanitized_name}.json"
        output_path = os.path.join(output_folder, output_filename)

        # Ghi file JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
            
        return (True, output_path)

    except Exception as e:
        return (False, f"Đã xảy ra lỗi: {str(e)}")