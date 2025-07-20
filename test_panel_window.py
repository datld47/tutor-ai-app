import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("VSCode Layout")
root.geometry("1000x600")

# Khung trên cùng (header)
fr_top = tk.Frame(root, height=40, bg="gray")
fr_top.pack(side="top", fill="x")

# PanedWindow chính (horizontal)
main_paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
main_paned.pack(fill="both", expand=True)

# Frame bên trái (sidebar)
fr_left = tk.Frame(main_paned, bg="#ddd", width=200)
main_paned.add(fr_left)

# PanedWindow lồng bên trong để chia center và right
center_right_paned = tk.PanedWindow(main_paned, orient=tk.HORIZONTAL)

# Frame trung tâm
fr_center = tk.Frame(center_right_paned, bg="white", width=600)
center_right_paned.add(fr_center)

# Frame bên phải
fr_right = tk.Frame(center_right_paned, bg="#eee", width=200)
center_right_paned.add(fr_right)

# Thêm center_right_paned vào main_paned
main_paned.add(center_right_paned)

# Thêm nhãn minh họa
tk.Label(fr_left, text="BÊN TRÁI", bg="#ddd").pack(pady=20)
tk.Label(fr_center, text="TRUNG TÂM", bg="white").pack(pady=20)
tk.Label(fr_right, text="BÊN PHẢI", bg="#eee").pack(pady=20)

root.mainloop()