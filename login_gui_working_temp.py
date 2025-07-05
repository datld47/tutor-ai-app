import tkinter as tk
from tkinter import messagebox
import json
import os
import sys

class LoginApp(tk.Toplevel):
    def __init__(self, master, student_list, dict_user_info_ref, update_user_info_callback, update_api_key_callback, path_student_list, path_json_config):
        super().__init__(master)
        self.master = master
        self.student_list = student_list
        self.dict_user_info = dict_user_info_ref # Tham chiếu đến biến có thể thay đổi trong app.py
        self.update_user_info_callback = update_user_info_callback
        self.update_api_key_callback = update_api_key_callback
        self.path_student_list = path_student_list
        self.path_json_config = path_json_config
        
        self.result = 'nok' # 'ok' cho thành công, 'nok' cho thất bại/hủy bỏ

        self.title("Đăng nhập")
        self.geometry("350x250")
        self.resizable(False, False)
        self.grab_set() # Biến cửa sổ thành modal (ngăn tương tác với cửa sổ chính)
        self.focus_set()

        # Tạo khung chứa các thành phần
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(expand=True)

        # Tiêu đề
        tk.Label(frame, text="ĐĂNG NHẬP / ĐĂNG KÝ", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # MSSV
        tk.Label(frame, text="Mã số sinh viên:", font=("Arial", 11)).grid(row=1, column=0, sticky='w', pady=5)
        self.txt_mssv = tk.Entry(frame, width=25, font=("Arial", 11))
        self.txt_mssv.grid(row=1, column=1, pady=5)

        # Tên người dùng (cho đăng ký)
        tk.Label(frame, text="Tên người dùng:", font=("Arial", 11)).grid(row=2, column=0, sticky='w', pady=5)
        self.txt_username = tk.Entry(frame, width=25, font=("Arial", 11))
        self.txt_username.grid(row=2, column=1, pady=5)
        
        # Mật khẩu
        tk.Label(frame, text="Mật khẩu:", font=("Arial", 11)).grid(row=3, column=0, sticky='w', pady=5)
        self.txt_password = tk.Entry(frame, width=25, show="*", font=("Arial", 11))
        self.txt_password.grid(row=3, column=1, pady=5)

        # Nút Đăng nhập
        btn_submit = tk.Button(frame, text="Đăng nhập", command=self.btn_login_click, font=("Arial", 12))
        btn_submit.grid(row=4, column=0, sticky='e', padx=5, pady=10)

        # Nút Đăng ký
        btn_register = tk.Button(frame, text="Đăng ký", command=self.btn_register_click, font=("Arial", 12))
        btn_register.grid(row=4, column=1, sticky='w', padx=5, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.wait_window() # Chặn luồng cho đến khi cửa sổ bị hủy

    def on_close(self):
        print('Đóng cửa sổ đăng nhập')
        self.result = 'nok'
        self.destroy()

    def btn_login_click(self):
        mssv_ = self.txt_mssv.get().strip()
        password_ = self.txt_password.get().strip()

        if mssv_ == '' or password_ == '':
            messagebox.showerror("Lỗi", "Thông tin cần nhập đầy đủ")
            return

        found_student = False
        for student in self.student_list:
            if student.get('idsv') == mssv_ and student.get('password') == password_:
                name_ = student.get('name')
                id_ = int(student.get('id', 0))
                
                # Gọi callback để cập nhật thông tin người dùng và API Key trong app.py
                self.update_user_info_callback(username=name_, mssv=mssv_, password=password_)
                self.update_api_key_callback(id_)

                messagebox.showinfo('Thông báo', f'Đăng nhập thành công: Xin chào {name_}')
                self.result = 'ok'
                self.destroy()
                found_student = True
                break
        
        if not found_student:
            messagebox.showerror("Lỗi", "Mã số sinh viên hoặc mật khẩu không đúng.")

    def btn_register_click(self):
        mssv_ = self.txt_mssv.get().strip()
        username_ = self.txt_username.get().strip()
        password_ = self.txt_password.get().strip()

        if mssv_ == '' or username_ == '' or password_ == '':
            messagebox.showerror("Lỗi", "Thông tin đăng ký cần nhập đầy đủ (MSSV, Tên người dùng, Mật khẩu)")
            return

        # Kiểm tra MSSV đã tồn tại
        for student in self.student_list:
            if student.get('idsv') == mssv_:
                messagebox.showerror("Lỗi", "Mã số sinh viên đã tồn tại. Vui lòng đăng nhập hoặc sử dụng MSSV khác.")
                return
        
        # Xác định ID mới cho sinh viên
        new_id = 0
        if self.student_list:
            new_id = max([s.get('id', 0) for s in self.student_list]) + 1
        
        # Tạo thông tin sinh viên mới
        new_student = {
            "id": new_id,
            "idsv": mssv_,
            "name": username_,
            "password": password_ # Lưu mật khẩu, cân nhắc mã hóa trong ứng dụng thực tế
        }
        self.student_list.append(new_student)

        # Lưu danh sách sinh viên đã cập nhật vào file
        try:
            # save_json_file cần được định nghĩa ở cấp độ này hoặc được truyền vào
            # Tuy nhiên, ta sẽ gọi lại load_app_data() trong app.py để đồng bộ
            # Ghi trực tiếp vào file student.json
            with open(self.path_student_list, 'w', encoding='utf-8') as f:
                json.dump(self.student_list, f, indent=2, ensure_ascii=False)
            print(f"Đã thêm sinh viên mới vào {self.path_student_list}")

            # Cập nhật config.json với thông tin người dùng mới và chọn API Key
            self.update_user_info_callback(username=username_, mssv=mssv_, password=password_)
            self.update_api_key_callback(new_id)

            messagebox.showinfo("Thành công", f"Đăng ký tài khoản '{username_}' thành công! Đã tự động đăng nhập.")
            self.result = 'ok'
            self.destroy()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đăng ký tài khoản: {e}")
            print(f"Lỗi khi ghi student.json: {e}")