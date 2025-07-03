
import tkinter as tk
from tkinter import ttk

# Dữ liệu từ json_course
json_course = {
    "task_list_title": "Chi tiết danh sách bài tập của từng buổi",
    "sessions": [
        {
            "title": "Buổi 1",
            "exercises": [
                {
                    "title": "Bài 1.1",
                    "description": "Viết chương trình tính tổng S(n) = 1 + 2 + 3 + ... + n.",
                    "guidance": [
                        "Khởi tạo biến sum = 0.",
                        "n có thể gán cứng hoặc sử dụng hàm scanf()",
                        "Dùng vòng lặp từ i = 1 đến n.",
                        "Cộng dồn i vào sum.",
                        "Kết thúc vòng lặp, in ra sum."
                    ]
                },
                {
                    "title": "Bài 1.2",
                    "description": "Viết chương trình tính tổng các số chẵn nhỏ hơn hoặc bằng n.",
                    "guidance": [
                        "Khởi tạo biến sum = 0.",
                        "Dùng vòng lặp từ i = 2 đến n, mỗi bước tăng 2.",
                        "Cộng dồn i vào sum.",
                        "Kết thúc vòng lặp, in ra tổng."
                    ]
                }
            ]
        },
        {
            "title": "Buổi 2",
            "exercises": [
                {
                    "title": "Bài 2.1",
                    "description": "Viết chương trình kiểm tra một số nguyên dương n có phải số nguyên tố hay không.",
                    "guidance": [
                        "Nếu n <= 1 thì không phải số nguyên tố.",
                        "Dùng vòng lặp từ 2 đến căn bậc hai của n.",
                        "Nếu tìm thấy một ước số chia hết, kết luận không phải số nguyên tố.",
                        "Nếu không tìm thấy ước số, kết luận là số nguyên tố."
                    ]
                },
                {
                    "title": "Bài 2.2",
                    "description": "Viết chương trình tính giai thừa của số nguyên dương n (n!).",
                    "guidance": [
                        "Khởi tạo biến fact = 1.",
                        "Dùng vòng lặp từ i = 1 đến n.",
                        "Nhân fact với i ở mỗi bước.",
                        "Kết thúc vòng lặp, in ra fact."
                    ]
                }
            ]
        }
    ]
}

# Giao diện cơ bản
root = tk.Tk()
root.title("Danh sách bài tập")
root.geometry("1000x600")

# Frame điều hướng trái
frame_nav = tk.Frame(root, width=250, bg="lightgray")
frame_nav.pack(side="left", fill="y")

# Frame nội dung bên phải
frame_content = tk.Frame(root, bg="white")
frame_content.pack(side="right", fill="both", expand=True)

label_title = tk.Label(frame_nav, text=json_course["task_list_title"], bg="lightgray", font=("Arial", 12, "bold"))
label_title.pack(pady=5)

tree = ttk.Treeview(frame_nav)
tree.pack(fill="both", expand=True)

# Hàm xử lý khi click vào bài tập
def on_select(event):
    selected_item = tree.focus()
    data = tree.item(selected_item)
    values = data.get("values")
    if values and values[0] == "exercise":
        session_index, exercise_index = map(int, values[1:])
        exercise = json_course["sessions"][session_index]["exercises"][exercise_index]

        # Xóa nội dung cũ
        for widget in frame_content.winfo_children():
            widget.destroy()

        # Hiển thị nội dung bài
        label_tittle=tk.Label(frame_content, text=exercise["title"], font=("Arial", 16, "bold"), bg="white")
        label_tittle.pack(anchor="w", padx=10, pady=(10, 5))
        label_tittle.bind("<Configure>", lambda e: label_tittle.config(wraplength=e.width))
        
        
        label_description=tk.Label(frame_content, text=exercise["description"], font=("Arial", 12), bg="white", wraplength=700, justify="left").pack(anchor="w", padx=10, pady=5)
        label_description.pack(anchor="w", padx=10, pady=5)
        label_description.bind("<Configure>", lambda e: label_description.config(wraplength=e.width))
        
        tk.Label(frame_content, text="Hướng dẫn:", font=("Arial", 12, "underline"), bg="white").pack(anchor="w", padx=10, pady=(10, 5))
        for g in exercise["guidance"]:
            tk.Label(frame_content, text="• " + g, font=("Arial", 11), bg="white", wraplength=700, justify="left").pack(anchor="w", padx=20)

# Gắn sự kiện click
tree.bind("<<TreeviewSelect>>", on_select)

# Thêm dữ liệu vào Treeview
for i, session in enumerate(json_course["sessions"]):
    session_id = tree.insert("", "end", text=session["title"], open=True)
    for j, ex in enumerate(session["exercises"]):
        tree.insert(session_id, "end", text=ex["title"], values=("exercise", i, j))

root.mainloop()