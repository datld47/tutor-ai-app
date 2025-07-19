import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import base64
import google.generativeai as genai
import re

# === CẤU HÌNH GEMINI ===
GOOGLE_API_KEY = "AIzaSyDvCMr_GJMvGxFynOvLedw04rqJ6_iElF0"  # Thay bằng API key của bạn
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

def create_prompt(file_content):
    return  f"""
Bạn là trợ lý chuyển đổi file sơ đồ thuật toán hoặc netlist thành định dạng JSON chuẩn để AI xử lý.

Hãy chỉ trả về **chuỗi JSON hợp lệ duy nhất**, không thêm bất kỳ giải thích, chú thích hay văn bản thừa nào.

Định dạng JSON gồm các trường cần thiết để mô tả đầy đủ sơ đồ thuật toán hoặc mạch điện.

Dưới đây là nội dung file (XML hoặc netlist):

{file_content}

Hãy chuyển đổi chính xác nội dung trên thành JSON và chỉ trả về JSON đó.
"""

def select_file():
    file_path = filedialog.askopenfilename(
        title="Chọn file .fprg, .xml hoặc .net",
        filetypes=[
            ("Flowgorithm files", "*.fprg"),
            ("XML files", "*.xml"),
            ("Netlist files", "*.net"),
            ("All files", "*.*")
        ]
    )
    if not file_path:
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        text_input.delete(1.0, tk.END)
        text_input.insert(tk.END, content)
        label_file.config(text=f"Đã chọn: {file_path}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể đọc file:\n{e}")

def extract_json_from_response(text):
    """
    Lọc JSON trong response text có dạng ```json ... ```
    Nếu không tìm thấy, trả về nguyên văn.
    """
    match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Nếu parse lỗi thì trả về nguyên văn
            return text
    else:
        # Không tìm thấy code block, trả về nguyên văn
        return text

def convert_file():
    content = text_input.get(1.0, tk.END).strip()
    if not content:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập hoặc chọn file trước.")
        return
    prompt = create_prompt(content)
    try:
        # Gọi API Gemini
        
        message=[{'role': 'user', 'parts': [prompt]}]
        
        response = model.generate_content(message)
        print(type(response))
        # Lấy text JSON từ response (giả sử đúng cấu trúc response)   
        response_text = response.text   
        # Trích xuất JSON thực sự
        parsed = extract_json_from_response(response_text)
        
        if isinstance(parsed, dict):
            formatted_json = json.dumps(parsed, indent=2, ensure_ascii=False)
        else:
            # Nếu không parse được JSON, hiển thị nguyên văn
            formatted_json = parsed
        
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, formatted_json)
        label_status.config(text="Chuyển đổi thành công!")
    except Exception as e:
        print(e)
        messagebox.showerror("Lỗi", f"Không thể chuyển đổi:\n{e}")


root = tk.Tk()
root.title("Chuyển đổi file Flowchart/Netlist sang JSON bằng Gemini AI")
root.geometry("900x700")

btn_select = tk.Button(root, text="Chọn file .fprg, .xml hoặc .net", command=select_file)
btn_select.pack(pady=10)

label_file = tk.Label(root, text="Chưa chọn file nào")
label_file.pack()


text_input = scrolledtext.ScrolledText(root, height=15)
text_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

btn_convert = tk.Button(root, text="Chuyển đổi sang JSON", command=convert_file)
btn_convert.pack(pady=10)

label_status = tk.Label(root, text="")
label_status.pack()

text_output = scrolledtext.ScrolledText(root, height=15)
text_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()