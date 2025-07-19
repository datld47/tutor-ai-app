# import tkinter as tk
# from tkinter import messagebox
# import json
# import os
# import sys
# # --- THAY ĐỔI QUAN TRỌNG ---
# # 1. Xóa "get_path" và import các biến đường dẫn đã được định nghĩa tập trung
# from usercustomize import PATH_DATA
# import pyrebase
# from datetime import datetime

# # 2. Lấy đường dẫn config.json từ biến PATH_DATA đã import
# #    Không cần khối if/else cho sys.frozen nữa vì usercustomize đã xử lý việc đó.
# PATH_JSON_CONFIG = os.path.join(PATH_DATA, 'config.json')

# # 3. Xóa bỏ hoàn toàn hàm get_path1 không cần thiết.

# # Các biến và hàm này nên được quản lý trong file app.py chính
# # và truyền vào LoginApp qua các hàm callback.
# API_KEY_LIST = []
# API_KEY = ''

# def save_json_file(filepath, data):
#     with open(filepath, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # Các hàm update_user_info và update_api_key nên nằm trong app.py
# # và được truyền vào LoginApp dưới dạng callback để tránh logic lặp lại.
# # Dưới đây chỉ là giữ lại để code không báo lỗi cú pháp.
# def update_user_info(username='', mssv='', password=''):
#     config = None
#     if os.path.exists(PATH_JSON_CONFIG):
#         with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as file:
#             try:
#                 config = json.load(file)
#             except json.JSONDecodeError:
#                 pass
#     if config is not None:
#         config['user'][0]['username'] = username
#         config['user'][0]['mssv'] = mssv
#         config['user'][0]['password'] = password
#         save_json_file(PATH_JSON_CONFIG, config)
#     else:
#         print("Cảnh báo: Không thể tải hoặc cập nhật config.json")

# def update_api_key(id_sv):
#     global API_KEY, API_KEY_LIST
#     if not API_KEY_LIST:
#         print("Cảnh báo: API_KEY_LIST trống.")
#         return
#     num_api_key = len(API_KEY_LIST)
#     if num_api_key > 0:
#         index = id_sv % num_api_key
#         API_KEY = API_KEY_LIST[index]
#         print(f"idsv={id_sv} ; index={index} ; api_key={API_KEY}")


# class LoginApp(tk.Toplevel):
#     def __init__(self, master, firebase_auth, firebase_db, update_user_info_callback, update_api_key_callback, path_json_config):
#         super().__init__(master)
#         self.master = master
#         self.auth = firebase_auth
#         self.db = firebase_db
#         self.update_user_info_callback = update_user_info_callback
#         self.update_api_key_callback = update_api_key_callback
#         self.path_json_config = path_json_config
#         self.current_user_uid = None
#         self.result = 'nok'
#         self.title("Đăng nhập")
        
#         screen_width = self.master.winfo_screenwidth()
#         screen_height = self.master.winfo_screenheight()
#         width = 350
#         height = 250
#         x = (screen_width // 2) - (width // 2)
#         y = (screen_height // 2) - (height // 2)
#         self.geometry(f"{width}x{height}+{x}+{y}")
#         self.resizable(False, False)
#         self.grab_set()
#         self.focus_set()        
        
#         frame = tk.Frame(self, padx=20, pady=20)
#         frame.pack(expand=True, fill="both")

#         tk.Label(frame, text="ĐĂNG NHẬP / ĐĂNG KÝ", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

#         self.lbl_email = tk.Label(frame, text="Email:")
#         self.lbl_email.grid(row=1, column=0, sticky='w', pady=5)
#         self.txt_email = tk.Entry(frame, width=30)
#         self.txt_email.grid(row=1, column=1, pady=5)

#         self.lbl_password = tk.Label(frame, text="Mật khẩu:")
#         self.lbl_password.grid(row=2, column=0, sticky='w', pady=5)
#         self.txt_password = tk.Entry(frame, show="*", width=30)
#         self.txt_password.grid(row=2, column=1, pady=5)
        
#         self.btn_submit = tk.Button(frame, text="Đăng nhập", command=self.btn_submit_click, font=("Arial", 12))
#         self.btn_submit.grid(row=3, column=0, columnspan=2, pady=10)

#         self.btn_register = tk.Button(frame, text="Đăng ký", command=self.btn_register_click, font=("Arial", 12))
#         self.btn_register.grid(row=4, column=0, columnspan=2, pady=5)

#         self.btn_forgot_password = tk.Button(frame, text="Quên mật khẩu?", command=self.btn_forgot_password_click, font=("Arial", 10), fg="blue", cursor="hand2")
#         self.btn_forgot_password.grid(row=5, column=0, columnspan=2, pady=(0, 10))

#         self.protocol("WM_DELETE_WINDOW", self.on_close)
#         self.wait_window()

#     def on_close(self):
#         print('đóng cửa sổ')
#         self.result = 'nok'
#         self.destroy()

#     def btn_submit_click(self):
#         email_ = self.txt_email.get()
#         password_ = self.txt_password.get()

#         if not email_ or not password_:
#             messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ email và mật khẩu.")
#             return

#         try:
#             user = self.auth.sign_in_with_email_and_password(email_, password_)
#             uid = user['localId']
#             token = user['idToken']
#             username_for_db = email_.split('@')[0]
#             print(f"Đăng nhập thành công: {user['email']}")

#             self.update_user_info_callback(username=username_for_db, mssv=uid, token=token)
            
#             messagebox.showinfo('Thành công', f'Đăng nhập thành công: Xin chào {username_for_db}')
#             self.result = 'ok'
#             self.destroy()

#         except Exception as e:
#             try:
#                 error_data = json.loads(e.args[1])
#                 error_message = error_data['error']['message']
#                 if "INVALID_LOGIN_CREDENTIALS" in error_message:
#                     messagebox.showerror("Lỗi đăng nhập", "Email hoặc mật khẩu không đúng.")
#                 else:
#                     messagebox.showerror("Lỗi đăng nhập", f"Lỗi: {error_message}")
#             except (IndexError, json.JSONDecodeError, KeyError):
#                 messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi không xác định: {e}")

#     def btn_register_click(self):
#         email_ = self.txt_email.get()
#         password_ = self.txt_password.get()

#         if not email_ or not password_:
#             messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Email và Mật khẩu để đăng ký.")
#             return

#         try:
#             self.auth.create_user_with_email_and_password(email_, password_)
#             user_signed_in = self.auth.sign_in_with_email_and_password(email_, password_)
#             uid = user_signed_in['localId']
#             token = user_signed_in['idToken']
#             self.current_user_uid = uid
#             username_for_db = email_.split('@')[0]
#             user_data = {
#                 "email": email_,
#                 "username": username_for_db,
#                 "created_at": datetime.now().isoformat(),
#                 "gemini_api_keys": []
#             }
            
#             self.db.child("users").child(uid).set(user_data, token)
#             self.update_user_info_callback(username=username_for_db, mssv=uid, token=token)
#             self.update_api_key_callback(uid)

#             messagebox.showinfo("Thành công", f"Đăng ký tài khoản '{email_}' thành công! Đã tự động đăng nhập.")
#             self.result = 'ok'
#             self.destroy()

#         except Exception as e:
#             error_message_display = "Đã xảy ra lỗi không xác định."
#             raw_error_text = ""
#             if len(e.args) > 1:
#                 raw_error_text = e.args[1]
#             try:
#                 error_data = json.loads(raw_error_text)
#                 if isinstance(error_data, dict) and 'error' in error_data and isinstance(error_data['error'], dict) and 'message' in error_data['error']:
#                     error_message = error_data['error']['message']
#                     if "EMAIL_EXISTS" in error_message:
#                         error_message_display = "Email này đã được sử dụng."
#                     elif "WEAK_PASSWORD" in error_message:
#                         error_message_display = "Mật khẩu quá yếu (cần ít nhất 6 ký tự)."
#                     else:
#                         error_message_display = f"Lỗi Firebase: {error_message}"
#                 else:
#                     error_message_display = f"Lỗi Firebase không rõ định dạng: {raw_error_text}"
#             except (json.JSONDecodeError, IndexError):
#                 error_message_display = f"Lỗi không xác định: {e}"
#             messagebox.showerror("Lỗi đăng ký", error_message_display)
            
#     def btn_forgot_password_click(self):
#         messagebox.showinfo("Thông báo", "Chức năng quên mật khẩu sẽ được triển khai.")

# import tkinter as tk
# from tkinter import messagebox
# import json
# import os
# import sys
# from PIL import Image as PILImage, ImageTk
# from usercustomize import PATH_DATA, PATH_IMG
# import pyrebase
# from datetime import datetime

# PATH_JSON_CONFIG = os.path.join(PATH_DATA, 'config.json')

# API_KEY_LIST = []
# API_KEY = ''

# def save_json_file(filepath, data):
#     with open(filepath, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# def update_user_info(username='', mssv='', password=''):
#     config = None
#     if os.path.exists(PATH_JSON_CONFIG):
#         with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as file:
#             try:
#                 config = json.load(file)
#             except json.JSONDecodeError:
#                 pass
#     if config is not None:
#         config['user'][0]['username'] = username
#         config['user'][0]['mssv'] = mssv
#         config['user'][0]['password'] = password
#         save_json_file(PATH_JSON_CONFIG, config)
#     else:
#         print("Cảnh báo: Không thể tải hoặc cập nhật config.json")

# def update_api_key(id_sv):
#     global API_KEY, API_KEY_LIST
#     if not API_KEY_LIST:
#         print("Cảnh báo: API_KEY_LIST trống.")
#         return
#     num_api_key = len(API_KEY_LIST)
#     if num_api_key > 0:
#         index = id_sv % num_api_key
#         API_KEY = API_KEY_LIST.get(str(id_sv)) if isinstance(API_KEY_LIST, dict) and str(id_sv) in API_KEY_LIST else (API_KEY_LIST.pop(0) if API_KEY_LIST else '')
#         print(f"idsv={id_sv} ; api_key={API_KEY}")


# class LoginApp(tk.Toplevel):
#     def __init__(self, master, firebase_auth, firebase_db, update_user_info_callback, update_api_key_callback, path_json_config):
#         super().__init__(master)
#         self.master = master
#         self.auth = firebase_auth
#         self.db = firebase_db
#         self.update_user_info_callback = update_user_info_callback
#         self.update_api_key_callback = update_api_key_callback
#         self.path_json_config = path_json_config
#         self.current_user_uid = None
#         self.result = 'nok'
#         self.title("Đăng nhập")

#         screen_width = self.master.winfo_screenwidth()
#         screen_height = self.master.winfo_screenheight()
#         width = 300
#         height = 340
#         x = (screen_width // 2) - (width // 2)
#         y = (screen_height // 2) - (height // 2)
#         self.geometry(f"{width}x{height}+{x}+{y}")
#         self.resizable(False, False)
#         self.grab_set()
#         self.focus_set()

#         frame = tk.Frame(self, padx=20, pady=20)
#         frame.pack(expand=True, fill="both")

#         try:
#             logo_path = os.path.join(PATH_IMG, 'LOGO_UDA.png')
#             logo_image = PILImage.open(logo_path)
#             original_width, original_height = logo_image.size
#             new_width = 100
#             new_height = int(new_width * original_height / original_width)
#             logo_image_resized = logo_image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
#             self.logo_photo = ImageTk.PhotoImage(logo_image_resized)

#             logo_label = tk.Label(frame, image=self.logo_photo)
#             logo_label.image = self.logo_photo
#             logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
#         except FileNotFoundError:
#             print("Cảnh báo: Không tìm thấy file logo 'LOGO_UDA.png' trong thư mục img.")
#         except Exception as e:
#             print(f"Lỗi khi tải logo: {e}")

#         tk.Label(frame, text="ĐĂNG NHẬP / ĐĂNG KÝ", font=("Arial", 14, "bold")).grid(row=1, column=0, columnspan=2, pady=10)

#         self.lbl_email = tk.Label(frame, text="Email:")
#         self.lbl_email.grid(row=2, column=0, sticky='w', pady=5)
#         self.txt_email = tk.Entry(frame, width=30)
#         self.txt_email.grid(row=2, column=1, pady=5)

#         self.lbl_password = tk.Label(frame, text="Mật khẩu:")
#         self.lbl_password.grid(row=3, column=0, sticky='w', pady=5)
#         self.txt_password = tk.Entry(frame, show="*", width=30)
        
#         # === THAY ĐỔI: GÁN SỰ KIỆN NHẤN ENTER CHO Ô MẬT KHẨU ===
#         self.txt_password.bind("<Return>", self.on_enter_key)

#         self.btn_submit = tk.Button(frame, text="Đăng nhập", command=self.btn_submit_click, font=("Arial", 12))
#         self.btn_submit.grid(row=4, column=0, columnspan=2, pady=10)

#         self.btn_register = tk.Button(frame, text="Đăng ký", command=self.btn_register_click, font=("Arial", 12))
#         self.btn_register.grid(row=5, column=0, columnspan=2, pady=5)

#         self.btn_forgot_password = tk.Button(frame, text="Quên mật khẩu?", command=self.btn_forgot_password_click, font=("Arial", 10), fg="blue", cursor="hand2")
#         self.btn_forgot_password.grid(row=6, column=0, columnspan=2, pady=(0, 10))

#         self.protocol("WM_DELETE_WINDOW", self.on_close)
#         self.wait_window()

#     def on_close(self):
#         print('đóng cửa sổ')
#         self.result = 'nok'
#         self.destroy()

#     def btn_submit_click(self):
#         email_ = self.txt_email.get()
#         password_ = self.txt_password.get()

#         if not email_ or not password_:
#             messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ email và mật khẩu.")
#             return

#         try:
#             user = self.auth.sign_in_with_email_and_password(email_, password_)
#             uid = user['localId']
#             token = user['idToken']
#             username_for_db = email_.split('@')[0]
#             print(f"Đăng nhập thành công: {user['email']}")

#             self.update_user_info_callback(username=username_for_db, mssv=uid, token=token)

#             messagebox.showinfo('Thành công', f'Đăng nhập thành công: Xin chào {username_for_db}')
#             self.result = 'ok'
#             self.destroy()

#         except Exception as e:
#             try:
#                 error_data = json.loads(e.args[-1]) # Lấy thông tin lỗi cuối cùng
#                 error_message = error_data['error']['message']
#                 if "INVALID_LOGIN_CREDENTIALS" in error_message:
#                     messagebox.showerror("Lỗi đăng nhập", "Email hoặc mật khẩu không đúng.")
#                 else:
#                     messagebox.showerror("Lỗi đăng nhập", f"Lỗi: {error_message}")
#             except (IndexError, json.JSONDecodeError, KeyError):
#                 messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi không xác định: {e}")

#     def btn_register_click(self):
#         email_ = self.txt_email.get()
#         password_ = self.txt_password.get()

#         if not email_ or not password_:
#             messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Email và Mật khẩu để đăng ký.")
#             return

#         try:
#             self.auth.create_user_with_email_and_password(email_, password_)
#             user_signed_in = self.auth.sign_in_with_email_and_password(email_, password_)
#             uid = user_signed_in['localId']
#             token = user_signed_in['idToken']
#             self.current_user_uid = uid
#             username_for_db = email_.split('@')[0]
#             user_data = {
#                 "email": email_,
#                 "username": username_for_db,
#                 "created_at": datetime.now().isoformat(),
#                 "gemini_api_keys": []
#             }

#             self.db.child("users").child(uid).set(user_data, token)
#             self.update_user_info_callback(username=username_for_db, mssv=uid, token=token)
#             self.update_api_key_callback(uid)

#             messagebox.showinfo("Thành công", f"Đăng ký tài khoản '{email_}' thành công! Đã tự động đăng nhập.")
#             self.result = 'ok'
#             self.destroy()

#         except Exception as e:
#             error_message_display = "Đã xảy ra lỗi không xác định."
#             raw_error_text = ""
#             if len(e.args) > 1:
#                 raw_error_text = e.args[-1] # Lấy thông tin lỗi cuối cùng
#             try:
#                 error_data = json.loads(raw_error_text)
#                 if isinstance(error_data, dict) and 'error' in error_data and isinstance(error_data['error'], dict) and 'message' in error_data['error']:
#                     error_message = error_data['error']['message']
#                     if "EMAIL_EXISTS" in error_message:
#                         error_message_display = "Email này đã được sử dụng."
#                     elif "WEAK_PASSWORD" in error_message:
#                         error_message_display = "Mật khẩu quá yếu (cần ít nhất 6 ký tự)."
#                     else:
#                         error_message_display = f"Lỗi Firebase: {error_message}"
#                 else:
#                     error_message_display = f"Lỗi Firebase không rõ định dạng: {raw_error_text}"
#             except (json.JSONDecodeError, IndexError):
#                 error_message_display = f"Lỗi không xác định: {e}"
#             messagebox.showerror("Lỗi đăng ký", error_message_display)

#     def btn_forgot_password_click(self):
#         messagebox.showinfo("Thông báo", "Chức năng quên mật khẩu sẽ được triển khai.")

# if __name__ == '__main__':
#     # Đây chỉ là một ví dụ đơn giản để chạy giao diện đăng nhập độc lập
#     # Trong ứng dụng chính, bạn nên tích hợp nó vào luồng hoạt động của app.
#     class MockFirebaseUtil:
#         def __init__(self):
#             pass
#         def sign_in_with_email_and_password(self, email, password):
#             print(f"Đăng nhập với: {email}, {password}")
#             return {'localId': 'mock_uid', 'idToken': 'mock_token', 'email': email}
#         def create_user_with_email_and_password(self, email, password):
#             print(f"Đăng ký với: {email}, {password}")
#             pass
#         def child(self, path):
#             return self
#         def set(self, data, token):
#             print(f"Lưu data: {data} với token: {token}")

#     root = tk.Tk()
#     root.withdraw() # Ẩn cửa sổ root

#     firebase_auth_mock = MockFirebaseUtil()
#     firebase_db_mock = MockFirebaseUtil()

#     def update_user_info_mock(username='', mssv='', password=''):
#         print(f"Cập nhật thông tin người dùng: {username}, {mssv}")

#     def update_api_key_mock(uid):
#         print(f"Cập nhật API key cho UID: {uid}")

#     # Tạo một file config.json giả nếu nó không tồn tại
#     if not os.path.exists(PATH_JSON_CONFIG):
#         os.makedirs(os.path.dirname(PATH_JSON_CONFIG), exist_ok=True)
#         with open(PATH_JSON_CONFIG, 'w') as f:
#             json.dump({"user": [{"username": "", "mssv": "", "password": ""}]}, f)

#     app = LoginApp(root, firebase_auth_mock, firebase_db_mock, update_user_info_mock, update_api_key_mock, PATH_JSON_CONFIG)
#     root.mainloop()

import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
from PIL import Image as PILImage, ImageTk
from usercustomize import PATH_DATA, PATH_IMG
import pyrebase
from datetime import datetime

PATH_JSON_CONFIG = os.path.join(PATH_DATA, 'config.json')

API_KEY_LIST = []
API_KEY = ''

def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_user_info(username='', mssv='', password=''):
    config = None
    if os.path.exists(PATH_JSON_CONFIG):
        with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError:
                pass
    if config is not None:
        config['user'][0]['username'] = username
        config['user'][0]['mssv'] = mssv
        config['user'][0]['password'] = password
        save_json_file(PATH_JSON_CONFIG, config)
    else:
        print("Cảnh báo: Không thể tải hoặc cập nhật config.json")

def update_api_key(id_sv):
    global API_KEY, API_KEY_LIST
    if not API_KEY_LIST:
        print("Cảnh báo: API_KEY_LIST trống.")
        return
    num_api_key = len(API_KEY_LIST)
    if num_api_key > 0:
        index = id_sv % num_api_key
        API_KEY = API_KEY_LIST.get(str(id_sv)) if isinstance(API_KEY_LIST, dict) and str(id_sv) in API_KEY_LIST else (API_KEY_LIST.pop(0) if API_KEY_LIST else '')
        print(f"idsv={id_sv} ; api_key={API_KEY}")


class LoginApp(tk.Toplevel):
    def __init__(self, master, firebase_auth, firebase_db, update_user_info_callback, update_api_key_callback, path_json_config):
        super().__init__(master)
        self.master = master
        self.auth = firebase_auth
        self.db = firebase_db
        self.update_user_info_callback = update_user_info_callback
        self.update_api_key_callback = update_api_key_callback
        self.path_json_config = path_json_config
        self.current_user_uid = None
        self.result = 'nok'
        self.title("Đăng nhập")

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        width = 300
        height = 340
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(expand=True, fill="both")

        try:
            logo_path = os.path.join(PATH_IMG, 'LOGO_UDA.png')
            logo_image = PILImage.open(logo_path)
            original_width, original_height = logo_image.size
            new_width = 120
            new_height = int(new_width * original_height / original_width)
            logo_image_resized = logo_image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image_resized)

            logo_label = tk.Label(frame, image=self.logo_photo)
            logo_label.image = self.logo_photo
            logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        except FileNotFoundError:
            print("Cảnh báo: Không tìm thấy file logo 'LOGO_UDA.png' trong thư mục img.")
        except Exception as e:
            print(f"Lỗi khi tải logo: {e}")

        tk.Label(frame, text="ĐĂNG NHẬP / ĐĂNG KÝ", font=("Arial", 14, "bold")).grid(row=1, column=0, columnspan=2, pady=10)

        self.lbl_email = tk.Label(frame, text="Email:")
        self.lbl_email.grid(row=2, column=0, sticky='w', pady=5)
        self.txt_email = tk.Entry(frame, width=30)
        self.txt_email.grid(row=2, column=1, pady=5)

        self.lbl_password = tk.Label(frame, text="Mật khẩu:")
        self.lbl_password.grid(row=3, column=0, sticky='w', pady=5)
        self.txt_password = tk.Entry(frame, show="*", width=30)
        self.txt_password.grid(row=3, column=1, pady=5)
        
        # === THAY ĐỔI: GÁN SỰ KIỆN NHẤN ENTER CHO Ô MẬT KHẨU ===
        self.txt_password.bind("<Return>", self.on_enter_key)

        self.btn_submit = tk.Button(frame, text="Đăng nhập", command=self.btn_submit_click, font=("Arial", 12))
        self.btn_submit.grid(row=4, column=0, columnspan=2, pady=10)

        self.btn_register = tk.Button(frame, text="Đăng ký", command=self.btn_register_click, font=("Arial", 12))
        self.btn_register.grid(row=5, column=0, columnspan=2, pady=5)

        self.btn_forgot_password = tk.Button(frame, text="Quên mật khẩu?", command=self.btn_forgot_password_click, font=("Arial", 10), fg="blue", cursor="hand2")
        self.btn_forgot_password.grid(row=6, column=0, columnspan=2, pady=(0, 10))

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.wait_window()

    def on_close(self):
        print('đóng cửa sổ')
        self.result = 'nok'
        self.destroy()

    # === THAY ĐỔI: TẠO HÀM XỬ LÝ SỰ KIỆN NHẤN ENTER ===
    def on_enter_key(self, event):
        self.btn_submit_click()

    def btn_submit_click(self):
        email_ = self.txt_email.get()
        password_ = self.txt_password.get()

        if not email_ or not password_:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ email và mật khẩu.")
            return

        try:
            user = self.auth.sign_in_with_email_and_password(email_, password_)
            uid = user['localId']
            token = user['idToken']
            username_for_db = email_.split('@')[0]
            print(f"Đăng nhập thành công: {user['email']}")

            self.update_user_info_callback(username=username_for_db, mssv=uid, token=token)

            messagebox.showinfo('Thành công', f'Đăng nhập thành công: Xin chào {username_for_db}')
            self.result = 'ok'
            self.destroy()

        except Exception as e:
            try:
                error_data = json.loads(e.args[-1])
                error_message = error_data['error']['message']
                if "INVALID_LOGIN_CREDENTIALS" in error_message:
                    messagebox.showerror("Lỗi đăng nhập", "Email hoặc mật khẩu không đúng.")
                else:
                    messagebox.showerror("Lỗi đăng nhập", f"Lỗi: {error_message}")
            except (IndexError, json.JSONDecodeError, KeyError):
                messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi không xác định: {e}")

    def btn_register_click(self):
        email_ = self.txt_email.get()
        password_ = self.txt_password.get()

        if not email_ or not password_:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Email và Mật khẩu để đăng ký.")
            return

        try:
            self.auth.create_user_with_email_and_password(email_, password_)
            user_signed_in = self.auth.sign_in_with_email_and_password(email_, password_)
            uid = user_signed_in['localId']
            token = user_signed_in['idToken']
            self.current_user_uid = uid
            username_for_db = email_.split('@')[0]
            user_data = {
                "email": email_,
                "username": username_for_db,
                "created_at": datetime.now().isoformat(),
                "gemini_api_keys": []
            }

            self.db.child("users").child(uid).set(user_data, token)
            self.update_user_info_callback(username=username_for_db, mssv=uid, token=token)
            self.update_api_key_callback(uid)

            messagebox.showinfo("Thành công", f"Đăng ký tài khoản '{email_}' thành công! Đã tự động đăng nhập.")
            self.result = 'ok'
            self.destroy()

        except Exception as e:
            error_message_display = "Đã xảy ra lỗi không xác định."
            raw_error_text = ""
            if len(e.args) > 1:
                raw_error_text = e.args[-1]
            try:
                error_data = json.loads(raw_error_text)
                if isinstance(error_data, dict) and 'error' in error_data and isinstance(error_data['error'], dict) and 'message' in error_data['error']:
                    error_message = error_data['error']['message']
                    if "EMAIL_EXISTS" in error_message:
                        error_message_display = "Email này đã được sử dụng."
                    elif "WEAK_PASSWORD" in error_message:
                        error_message_display = "Mật khẩu quá yếu (cần ít nhất 6 ký tự)."
                    else:
                        error_message_display = f"Lỗi Firebase: {error_message}"
                else:
                    error_message_display = f"Lỗi Firebase không rõ định dạng: {raw_error_text}"
            except (json.JSONDecodeError, IndexError):
                error_message_display = f"Lỗi không xác định: {e}"
            messagebox.showerror("Lỗi đăng ký", error_message_display)

    def btn_forgot_password_click(self):
        messagebox.showinfo("Thông báo", "Chức năng quên mật khẩu sẽ được triển khai.")

if __name__ == '__main__':
    class MockFirebaseUtil:
        def __init__(self):
            pass
        def sign_in_with_email_and_password(self, email, password):
            print(f"Đăng nhập với: {email}, {password}")
            return {'localId': 'mock_uid', 'idToken': 'mock_token', 'email': email}
        def create_user_with_email_and_password(self, email, password):
            print(f"Đăng ký với: {email}, {password}")
            pass
        def child(self, path):
            return self
        def set(self, data, token):
            print(f"Lưu data: {data} với token: {token}")

    root = tk.Tk()
    root.withdraw()

    firebase_auth_mock = MockFirebaseUtil()
    firebase_db_mock = MockFirebaseUtil()

    def update_user_info_mock(username='', mssv='', password=''):
        print(f"Cập nhật thông tin người dùng: {username}, {mssv}")

    def update_api_key_mock(uid):
        print(f"Cập nhật API key cho UID: {uid}")

    if not os.path.exists(PATH_JSON_CONFIG):
        os.makedirs(os.path.dirname(PATH_JSON_CONFIG), exist_ok=True)
        with open(PATH_JSON_CONFIG, 'w') as f:
            json.dump({"user": [{"username": "", "mssv": "", "password": ""}]}, f)

    app = LoginApp(root, firebase_auth_mock, firebase_db_mock, update_user_info_mock, update_api_key_mock, PATH_JSON_CONFIG)
    root.mainloop()