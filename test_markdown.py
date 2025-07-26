import tkinter as tk
import markdown
from tkhtmlview import HTMLLabel
from usercustomize1 import *
import html
from tkinterweb import HtmlFrame

# root = tk.Tk()
# root.title("Hiển thị Markdown trong Tkinter")
# root.minsize(640,480)
# # Nội dung markdown
# md_text = """
# # Tiêu đề lớn

# Bạn vẫn đang ở bước 2: **`n` có thể gán cứng hoặc sử dụng hàm `scanf()`**. Bạn có vẻ muốn dùng `scanf()` để nhập `n` từ bàn phím. \n\nĐể làm điều này, bạn cần:\n\n1. **Khai báo biến `n`:**  Ví dụ: `int n;`\n2. **Sử dụng hàm `scanf()` để đọc giá trị nhập từ bàn phím:** 
#  Cú pháp là `scanf(\"%d\", &n);`.  Trong đó:\n    *   `%d` là định dạng cho số nguyên (decimal integer).\n    *   `&n` là địa chỉ của biến `n` (chúng ta cần địa chỉ để `scanf()` có thể lưu giá trị vào biến `n`).\n\nVí dụ:\n\n```c\n#include <stdio.h>\n\nint main() {\n    int n;\n 
#    printf(\"Nhap vao so n: \");\n    scanf(\"%d\", &n);\n    printf(\"Ban vua nhap n = %d\\n\", n);\n    return 0;\n}\n```\n\nĐoạn code trên sẽ in ra màn hình dòng chữ "Nhap vao so n: " và chờ bạn nhập một số nguyên. Sau khi bạn nhập số và nhấn Enter, chương trình sẽ in ra dòng chữ "Ban vua nhap n = [so ban vua nhap]
   
# """
# # # Chuyển Markdown thành HTML
# root.rowconfigure(0,weight=1)
# root.columnconfigure(0,weight=1)
# root.columnconfigure(1,weight=1)
# fr=tk.Frame(root,bg='red')
# fr2=tk.Frame(root,bg='yellow')
# fr.grid(row=0,column=0,sticky='nswe')
# fr2.grid(row=0,column=1,sticky='nswe')

# fr.rowconfigure(0,weight=1)
# fr.columnconfigure(0,weight=1)
# html_content = markdown.markdown(md_text)
# label = HTMLLabel(fr, html=html_content)
# label.grid(row=0,column=0,sticky='nswe')
# # label.fit_height()



import markdown
import re
import json
# text='''{"data": "Để giúp bạn hiểu rõ hơn về cách triển khai chương trình kiểm tra số nguyên tố, tôi sẽ cung cấp một số kiến thức lý thuyết nền tảng và ví dụ minh họa:\n\n**1. Số nguyên tố:**\n   - Số nguyên tố là số tự nhiên lớn hơn 1, chỉ chia hết cho 1 và chính nó.\n   - Ví dụ: 2, 3, 5, 7, 11, 13, 
# ...\n\n**2. Cách kiểm tra số nguyên tố:**\n   - Cách đơn giản nhất là duyệt qua tất cả các số từ 2 đến n-1 và kiểm tra xem n có chia hết cho số nào không. Nếu có, n không phải là số nguyên tố.\n  
#  - Tuy nhiên, cách này không hiệu quả với các số lớn. Chúng ta có thể tối ưu bằng cách chỉ duyệt đến căn bậc hai của n.\n\n**3. Tại sao chỉ cần duyệt đến căn bậc hai của n?**\n   - Nếu n có một ước số lớn hơn căn bậc hai của n, thì nó cũng phải có một ước số nhỏ hơn căn bậc hai của n.\n   - Ví dụ: n = 36, căn bậc hai của n là 6. Các ước số của 36 là: 1, 2, 3, 4, 6, 9, 12, 18, 36.\n   - Ta 
# thấy rằng nếu 36 chia hết cho 9 (lớn hơn 6), thì nó cũng chia hết cho 4 (nhỏ hơn 6).\n\n**4. Ví dụ minh họa:**\n   - Kiểm tra xem 17 có phải là số nguyên tố hay không.\n   - Căn bậc hai của 17 là 
# khoảng 4.12. Vậy ta chỉ cần duyệt các số từ 2 đến 4.\n   - 17 không chia hết cho 2, 3, 4. Vậy 17 là số nguyên tố.\n\n**5. Mã giả (Pseudo code):**\n
# \nNhập số nguyên dương n\nNếu n <= 1 thì\n    
# In ra "n khong la so nguyen to"\n    Ket thuc chuong trinh\n\nsqrt_n = can bac hai cua n\n\nLap tu i = 2 den sqrt_n\n    Neu n chia het cho i thi\n        In ra "n khong la so nguyen to"\n        
# Ket thuc chuong trinh\n    Ket thuc neu\nKet thuc lap\n\nIn ra "n la so nguyen to"\nKet thuc chuong trinh\n
# ", "info": {"current_session_title": "Buổi 2", "current_exercise_title": "Bài 2.1", "exercise_status": "in_progress", "level": "Apply", "score": 4}}'''


# text2='''{"data": "Xin chào", "info": {"level": "Apply", "score": 4}}'''

# # try:
# #     data_dict = json.loads(text2)
# #     print(data_dict)
# # except Exception as er:
# pattern = r'"data"\s*:\s*"((?:.|\n)*?)"\s*,\s*"info"'
# match = re.search(pattern, text, re.DOTALL)
# data=match.group(1)

# pattern = r'"info"\s*:\s*({[^{}]*})'
# match = re.search(pattern, text)
# info=match.group(1)
# dic=json.loads(text2)
# print(type(dic['info']))

# print(info)
# input()



def extract_and_replace_c_blocks(text):
    blocks = []
    def replacer(match):
        blocks.append(match.group(0))
        return f"__CODE_{len(blocks)-1}__"
    new_text = re.sub(r'```c\s.*?```', replacer, text, flags=re.DOTALL)
    return new_text, blocks

# def normalize_code_block_indent(block: str) -> str:
#     """
#     Nhận vào block code kiểu Markdown (```c ... ```) và chuẩn hóa:
#     - Dấu ``` đóng phải nằm riêng trên dòng
#     - Nội dung code không thụt dòng
#     """
#     lines = block.strip().split('\n')

#     if len(lines) < 2 or not lines[0].startswith('```c'):
#         return block  # Không phải block code hợp lệ

#     opening = lines[0].strip()
#     closing = lines[-1].strip()

#     # Nếu dòng cuối không đúng là ``` thì cố gắng tìm trong dòng cuối hoặc loại bỏ thụt dòng
#     if closing != '```':
#         # Trường hợp ``` nằm chung dòng cuối cùng (ví dụ: '   ```')
#         if lines[-1].strip().endswith('```'):
#             # Cắt dấu ``` ra riêng
#             content_line = lines[-1].rstrip().removesuffix('```').rstrip()
#             if content_line:
#                 code_lines = [line.lstrip() for line in lines[1:-1]] + [content_line]
#             else:
#                 code_lines = [line.lstrip() for line in lines[1:-1]]
#         else:
#             # Không phát hiện được ``` -> giữ nguyên
#             return block
#     else:
#         code_lines = [line.lstrip() for line in lines[1:-1]]

#     # Gộp lại block chuẩn
#     return '\n'.join([opening] + code_lines + ['```'])

# def resume_block_code(new_text,code_blocks):
#     new_code_block=[]
#     for block in code_blocks:
#         cleaned = normalize_code_block_indent(block)
#         new_code_block.append(cleaned)
        
#     for i, block in enumerate(new_code_block):
#         print(block)
#         new_text = new_text.replace(f"__CODE_{i}__",f"\n{block}\n")
#     return new_text

# new_text, code_blocks = extract_and_replace_c_blocks(dictionary['data'])
# new_text=resume_block_code(new_text,code_blocks)
# html = markdown.markdown(new_text, extensions=["fenced_code"])

def get_description():
    path_json=get_path('project/project4/test.json')

    with open(path_json,"r", encoding="utf-8") as file:
        try:
            data=json.load(file)
        except Exception as err:
            print(err)
            data=''
    new_text=data['description']
    
    html_description = markdown.markdown(new_text, extensions=["fenced_code","extra",])
    return html_description

def btn_refesh_click(args):
    print('click')
    label=args['label']
    text_widget=args['text_widget']
    html_description=get_description()

    html_template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>MathJax Viewer</title>
        <script type="text/javascript"
          async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
        </script>
    </head>
    <body>
        <div style='font-size:16px; font-family:Verdana'>
            {html_description}
        </div>
    </body>
    </html>
    """
    
    label.load_html(html_template)
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", html_description)
        
        
        
def extract_data_and_info(text):
    def extract_data_block(text):
        start = text.find('"data":')
        end = text.find('"info":')
        if start == -1 or end == -1:
            return None
        raw_data = text[start + 7:end].strip().strip(',').strip()
        if raw_data.startswith('"') and raw_data.endswith('"'):
            raw_data = raw_data[1:-1]  # Bỏ dấu ngoặc kép đầu/cuối
        return raw_data

    def extract_info_block(text):
        start = text.find('"info":')
        if start == -1:
            return None
        brace_open = text.find('{', start)
        if brace_open == -1:
            return None

        count = 0
        end = brace_open
        while end < len(text):
            if text[end] == '{':
                count += 1
            elif text[end] == '}':
                count -= 1
                if count == 0:
                    break
            end += 1

        info_raw = text[brace_open:end + 1]
        
        try:
            import json
            info_dict = json.loads(info_raw)
        except json.JSONDecodeError:
            info_dict = {}
        return info_dict

    data_content = extract_data_block(text)
    info_metadata = extract_info_block(text)
    return data_content, info_metadata


def main():
   
   
   
    text='''
   ```json
    {
    "data": "Chào mừng bạn đến với bài học **Bài 2.6: Địa chỉ biến**. Hãy viết chương trình thực hiện các yêu cầu sau:\n\n- Khai báo biến cục bộ `x` lưu giá trị 80.\n- Khai báo biến toàn cục `y` lưu giá trị 80.\n- In giá trị của biến `x` và địa chỉ biến `x`.\n- In giá trị biến `y` và địa chỉ biến `y`.\n- Sử dụng con trỏ `p_x` để lưu địa chỉ biến `x`.\n- In giá trị con trỏ `p_x`.\n- Đọc giá trị biến `x` thông qua con trỏ `p_x` và lưu vào biến `z`.\n- In giá trị biến `z`.",
    "info": {
        "current_session_title": "Buổi 2: Biến và toán tử",
        "current_exercise_title": "Bài 2.6: Địa chỉ biến",
        "exercise_status": "in_progress",
        "level": "Apply",
        "score": 10
    }
    }
    ```
    '''
        

    raw_data,_=extract_data_and_info(text)    
   
   
    root = tk.Tk()
    root.title("Hiển thị Markdown trong Tkinter")
    root.minsize(640,480)

    root.rowconfigure(0,weight=0)
    root.rowconfigure(1,weight=1)
    root.columnconfigure(0,weight=1)
    root.columnconfigure(1,weight=1)
    
    fr_0=tk.Frame(root,bg='yellow')
    fr_0.grid(row=0,column=0,sticky='nswe',columnspan=2)
    fr_0.columnconfigure(0,weight=1)
    fr_0.rowconfigure(0,weight=1)
    btn_refesh=tk.Button(text='refesh')
    btn_refesh.grid(row=0,column=0,sticky='w')

    fr=tk.Frame(root,bg='red')
    fr.grid(row=1,column=0,sticky='nswe')
    fr.rowconfigure(0,weight=1)
    fr.columnconfigure(0,weight=1)
    
    #html_description=get_description()
    html_description = markdown.markdown(raw_data, extensions=["fenced_code","extra",])
    
    # print(html_description)
    label = HtmlFrame(fr)
    label.grid(row=0,column=0,sticky='nswe')
    
    fr2=tk.Frame(root,bg='green')
    fr2.grid(row=1,column=1,sticky='nswe')
    fr2.columnconfigure(0,weight=1)
    fr2.rowconfigure(0,weight=1)
    

    text_widget = tk.Text(fr2, wrap="word", font=("Courier New", 12))
    text_widget.grid(row=0,column=0,sticky='nswe')
    text_widget.insert("1.0", html_description)
    
    
    html_template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Phản hồi AI</title>
    </head>
    <body>
        <div style='font-size:16px; font-family:Verdana'>
            {html_description}
        </div>
    </body>
    </html>
    """
    
    label.load_html(html_template)
    
    # text_widget.delete("1.0", tk.END)
    # text_widget.insert("1.0", html_description)
    
    
    btn_refesh.config(command=lambda:btn_refesh_click({'label':label,'text_widget':text_widget}))

    root.mainloop()

if __name__=='__main__':
    main()

