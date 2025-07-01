import tkinter as tk
from tkinter import ttk

json_course = {
    "sessions": [
        {
            "title": "Session 1",
            "label": "✓ Completed",
            "exercises": [
                {"title": "Exercise 1.1", "status": "✓"},
                {"title": "Exercise 1.2", "status": "✗"}
            ]
        },
        {
            "title": "Session 2",
            "label": "✗ Pending",
            "exercises": [
                {"title": "Exercise 2.1", "status": "✗"},
                {"title": "Exercise 2.2", "status": "✗"}
            ]
        }
    ]
}

def tree_load(tree, json_course):
    for i, session in enumerate(json_course["sessions"]):
        session_id = tree.insert("", "end", text=session["title"], values=(session["label"],))
        for j, ex in enumerate(session["exercises"]):
            tree.insert(session_id, "end", text=ex["title"], values=(ex["status"],))

# GUI
root = tk.Tk()
tree = ttk.Treeview(root, columns=("label",), show="tree headings")
tree.heading("#0", text="Title")
tree.heading("label", text="Status")

tree.pack(fill="both", expand=True)

# Load dữ liệu
tree_load(tree, json_course)

root.mainloop()