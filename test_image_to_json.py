import tkinter as tk
from tkinter import filedialog
from PIL import Image as PILImage, ImageTk
import base64
import google.generativeai as genai

# === CẤU HÌNH GEMINI ===
GOOGLE_API_KEY = "AIzaSyDvCMr_GJMvGxFynOvLedw04rqJ6_iElF0"  # Thay bằng API key của bạn
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

# === HÀM: Đọc ảnh và mô tả bằng Gemini ===
def describe_image_with_gemini(image_path):

    prompt='''Bạn là trợ lý AI chuyên mô tả hình ảnh dưới dạng JSON chuẩn để các hệ thống AI khác có thể hiểu và xử lý.

    Ảnh được gửi kèm là file PNG hoặc JPG hoặc JPEG hoặc BMP

    Hãy phân tích và trả về một chuỗi JSON hợp lệ duy nhất, bao gồm các thông tin sau:

    - Mô tả tổng quan về ảnh.
    - Các thành phần chữ hoặc văn bản (nếu có), với nội dung, màu sắc, vị trí, kích thước, font chữ.
    
    Không thêm bất kỳ lời giải thích, chú thích hay văn bản thừa nào ngoài JSON.

    Chỉ trả về JSON thuần túy. '''
    
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
        
    try:
        response = model.generate_content([
           prompt,
            {"mime_type": "image/png", "data": image_bytes}
        ])
        return response.text
    except Exception as e:
        return f"Lỗi: {e}"

# === XỬ LÝ KHI CHỌN ẢNH ===
def upload_and_process_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not file_path:
        return

    # Gửi ảnh đến Gemini để mô tả
    result = describe_image_with_gemini(file_path)

    # Hiển thị mô tả lên TextBox
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, result)

    # Hiển thị preview ảnh
    img = PILImage.open(file_path)
    img.thumbnail((250, 250))
    img_tk = ImageTk.PhotoImage(img)
    image_label.configure(image=img_tk)
    image_label.image = img_tk  # giữ ảnh trong bộ nhớ

# === GIAO DIỆN TKINTER ===
root = tk.Tk()
root.title("🧠 Mô tả ảnh bằng Gemini Vision")
root.geometry("600x500")

upload_button = tk.Button(root, text="📁 Chọn ảnh để mô tả", command=upload_and_process_image, font=("Arial", 12))
upload_button.pack(pady=10)

image_label = tk.Label(root)
image_label.pack(pady=5)

output_text = tk.Text(root, wrap="word", font=("Arial", 11))
output_text.pack(expand=True, fill="both", padx=10, pady=10)

root.mainloop()