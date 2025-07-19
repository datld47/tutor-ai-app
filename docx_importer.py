
# import docx
# import json
# import os
# import re
# import unicodedata

# def sanitize_filename(name):
#     """
#     Loại bỏ các ký tự không hợp lệ và khoảng trắng khỏi tên để tạo tên file an toàn.
#     """
#     s = unicodedata.normalize('NFD', name)
#     s = re.sub(r'[\u0300-\u036f]', '', s)
#     s = s.replace('đ', 'd').replace('Đ', 'D')
#     s = re.sub(r'[^\w\s-]', '', s).strip()
#     s = re.sub(r'[-\s]+', '_', s)
#     return s

# def process_docx_to_json(docx_path, output_folder):
#     """
#     Đọc một file DOCX có cấu trúc, phân tích và tạo ra một file course_*.json.
#     Gộp tất cả các loại hướng dẫn vào một trường 'guidance'.
#     """
#     try:
#         doc = docx.Document(docx_path)
        
#         course_data = {
#             "course_name": "Chưa xác định",
#             "course_language": "Không",
#             "task_list_title": "Chi tiết danh sách bài tập của từng buổi",
#             "sessions": []
#         }
        
#         current_session = None
#         current_exercise = None
#         exercise_id_counter = 1
        
#         # Cờ để theo dõi loại nội dung đang đọc
#         # 0: Đang đọc nội dung mô tả (description)
#         # 1: Đang đọc nội dung hướng dẫn (guidance - gộp cả chung và làm bài)
#         current_content_type = 0 

#         for para in doc.paragraphs:
#             if not para.text.strip():
#                 continue

#             style_name = para.style.name
#             line_text = para.text.strip() 

#             # --- Xử lý thông tin chung của môn học ---
#             if line_text.lower().startswith("tên môn:"):
#                 course_data["course_name"] = line_text[len("tên môn:"):].strip()
#                 continue
            
#             if line_text.lower().startswith("ngôn ngữ:"):
#                 course_data["course_language"] = line_text[len("ngôn ngữ:"):].strip().lower()
#                 continue

#             # --- Xử lý Heading 1 (Buổi học) ---
#             if 'Heading 1' in style_name:
#                 current_session = {
#                     "title": line_text,
#                     "exercises": []
#                 }
#                 course_data["sessions"].append(current_session)
#                 current_exercise = None 
#                 current_content_type = 0 
#                 continue

#             # --- Xử lý Heading 2 (Bài tập) ---
#             if 'Heading 2' in style_name:
#                 if current_session is None:
#                     print(f"Lỗi cấu trúc: Tìm thấy 'Tên bài' (Heading 2) nhưng chưa có 'Buổi học' (Heading 1) ở dòng: {line_text}")
#                     continue 

#                 current_exercise = {
#                     "id": exercise_id_counter,
#                     "title": line_text,
#                     "description": "",
#                     "status": "✗",
#                     "score": 0,
#                     "image": [], 
#                     "guidance": [] # Chỉ còn một trường guidance duy nhất, là list of strings
#                 }
#                 current_session["exercises"].append(current_exercise)
#                 exercise_id_counter += 1
#                 current_content_type = 0 # Khi gặp bài mới, mặc định đọc description
#                 continue
            
#             # --- Xử lý Heading 3 (Hướng dẫn làm bài) ---
#             if 'Heading 3' in style_name:
#                 if current_exercise is None:
#                     print(f"Cảnh báo: Tìm thấy 'Hướng dẫn làm bài' (Heading 3) nhưng chưa có 'Bài tập' (Heading 2) ở dòng: {line_text}")
#                     continue 
#                 current_content_type = 1 # Chuyển sang đọc nội dung hướng dẫn (guidance)
                
#                 # Thêm chính nội dung của Heading 3 vào guidance
#                 #current_exercise["guidance"].append(line_text) # Thêm như một dòng mới
#                 continue 

#             # --- Xử lý nội dung thông thường (không phải Heading) ---
#             if current_exercise is not None:
#                 # Xử lý các tiền tố cũ để phân loại nội dung
#                 if line_text.lower().startswith("mô tả bài tập:"):
#                     current_content_type = 0 
#                     current_exercise["description"] += line_text[len("mô tả bài tập:"):].strip() + "\n"
#                     continue
#                 elif line_text.lower().startswith("hướng dẫn chung:"):
#                     current_content_type = 1 # Chuyển sang đọc guidance
#                     # Thêm phần còn lại của dòng vào guidance
#                     current_exercise["guidance"].append(line_text[len("hướng dẫn chung:"):].strip()) 
#                     continue
                
#                 # Định dạng dòng văn bản (thêm bullet nếu là list paragraph)
#                 formatted_line_content = line_text.strip()
#                 # Thêm dấu bullet nếu là List Paragraph style
#                 if 'List Paragraph' in style_name:
#                     formatted_line_content = "- " + formatted_line_content
                
#                 # Nối nội dung vào trường tương ứng
#                 if current_content_type == 0: # Đang đọc description
#                     current_exercise["description"] += formatted_line_content + "\n"
#                 elif current_content_type == 1: # Đang đọc guidance
#                     current_exercise["guidance"].append(formatted_line_content) # Thêm từng dòng vào list

#         # Dọn dẹp dấu xuống dòng thừa ở cuối các trường văn bản
#         for session in course_data["sessions"]:
#             for ex in session["exercises"]:
#                 ex["description"] = ex["description"].strip()
#                 # guidance đã là list, các phần tử đã strip khi thêm vào
#                 # Nếu muốn nối các dòng của guidance thành một chuỗi duy nhất:
#                 # ex["guidance"] = "\n".join(ex["guidance"]).strip() 

#         if course_data["course_name"] == "Chưa xác định":
#             return (False, "Không tìm thấy 'Tên môn:' trong file DOCX.")
            
#         sanitized_name = sanitize_filename(course_data["course_name"])
#         output_filename = f"course_{sanitized_name}.json"
#         output_path = os.path.join(output_folder, output_filename)

#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(course_data, f, indent=2, ensure_ascii=False)
            
#         return (True, output_path)

#     except Exception as e:
#         return (False, f"Đã xảy ra lỗi: {str(e)}")

# Thêm import mới và xóa import docx
from docx2python import docx2python
import json
import os
import re
import unicodedata

# Hàm sanitize_filename giữ nguyên như cũ
def sanitize_filename(name):
    """
    Loại bỏ các ký tự không hợp lệ và khoảng trắng khỏi tên để tạo tên file an toàn.
    """
    s = unicodedata.normalize('NFD', name)
    s = re.sub(r'[\u0300-\u036f]', '', s)
    s = s.replace('đ', 'd').replace('Đ', 'D')
    s = re.sub(r'[^\w\s-]', '', s).strip()
    s = re.sub(r'[-\s]+', '_', s)
    return s

def process_docx_to_json(docx_path, output_folder):
    """
    Đọc một file DOCX bằng docx2python, phân tích nội dung HTML và tạo file course_*.json.
    Công thức toán học sẽ được tự động chuyển thành LaTeX.
    """
    try:
        # Sử dụng docx2python với html=True để lấy các thẻ heading
        with docx2python(docx_path, html=True) as docx_content:
            text_content = docx_content.text

        course_data = {
            "course_name": "Chưa xác định",
            "course_language": "Không",
            "task_list_title": "Chi tiết danh sách bài tập của từng buổi",
            "sessions": []
        }
        
        current_session = None
        current_exercise = None
        exercise_id_counter = 1
        is_reading_guidance = False

        # Phân tích nội dung đã được chuyển đổi
        for line in text_content.splitlines():
            if not line.strip():
                continue

            # --- Xử lý thông tin chung ---
            if line.lower().startswith("tên môn:"):
                course_data["course_name"] = line[len("tên môn:"):].strip()
                continue
            if line.lower().startswith("ngôn ngữ:"):
                course_data["course_language"] = line[len("ngôn ngữ:"):].strip().lower()
                continue

            # --- Xử lý Buổi học (<h1>) ---
            match_h1 = re.search(r'<h1>(.*?)</h1>', line)
            if match_h1:
                is_reading_guidance = False
                current_session = {"title": match_h1.group(1).strip(), "exercises": []}
                course_data["sessions"].append(current_session)
                current_exercise = None
                continue

            # --- Xử lý Bài tập (<h2>) ---
            match_h2 = re.search(r'<h2>(.*?)</h2>', line)
            if match_h2:
                is_reading_guidance = False
                if current_session:
                    current_exercise = {
                        "id": exercise_id_counter,
                        "title": match_h2.group(1).strip(),
                        "description": "",
                        "status": "✗", "score": 0, "image": [],
                        "guidance": []
                    }
                    current_session["exercises"].append(current_exercise)
                    exercise_id_counter += 1
                continue

            # --- Xử lý Hướng dẫn (<h3>) ---
            match_h3 = re.search(r'<h3>(.*?)</h3>', line)
            if match_h3 and "hướng dẫn" in match_h3.group(1).lower():
                is_reading_guidance = True
                continue
            
            # --- Xử lý nội dung thông thường ---
            if current_exercise:
                # Xóa các thẻ HTML không cần thiết khác nếu có
                clean_line = re.sub(r'<.*?>', '', line).strip()
                if is_reading_guidance:
                    current_exercise["guidance"].append(clean_line)
                else:
                    # Công thức toán đã là LaTeX, chỉ cần nối chuỗi
                    current_exercise["description"] += clean_line + "\n"
        
        # Dọn dẹp dấu xuống dòng thừa
        for session in course_data["sessions"]:
            for ex in session["exercises"]:
                ex["description"] = ex["description"].strip()

        # --- Lưu file JSON (giữ nguyên logic) ---
        if course_data["course_name"] == "Chưa xác định":
            return (False, "Không tìm thấy 'Tên môn:' trong file DOCX.")
            
        sanitized_name = sanitize_filename(course_data["course_name"])
        output_filename = f"course_{sanitized_name}.json"
        output_path = os.path.join(output_folder, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
            
        return (True, output_path)

    except Exception as e:
        return (False, f"Đã xảy ra lỗi khi xử lý với docx2python: {str(e)}")