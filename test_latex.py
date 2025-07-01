import tkinter as tk
from tkinter import scrolledtext
import json
import markdown
import tempfile
import webbrowser
from usercustomize import *

def get_description():
    try:
        path_json=get_path('project/project4/test.json')
        with open(path_json, "r", encoding="utf-8") as file:
            data = json.load(file)
            new_text = data.get("description", "")
            html_description = markdown.markdown(new_text, extensions=["fenced_code", "extra"])
            return html_description
    except Exception as e:
        print(f"Lỗi đọc JSON: {e}")
        return ""

def open_mathjax_viewer(html_body):
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
            {html_body}
        </div>
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as f:
        f.write(html_template)
        webbrowser.open(f.name)

def refresh_content():
    html_body = get_description()
    open_mathjax_viewer(html_body)
    text_box.delete("1.0", tk.END)
    text_box.insert("1.0", html_body)

# === Giao diện Tkinter đơn giản ===
window = tk.Tk()
window.title("Xem LaTeX từ Markdown JSON")
window.geometry("600x400")

btn = tk.Button(window, text="Hiển thị công thức", command=refresh_content)
btn.pack(pady=10)

text_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Courier", 10))
text_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

window.mainloop()