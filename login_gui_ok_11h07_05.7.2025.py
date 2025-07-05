import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
from usercustomize import get_path
import pyrebase
from datetime import datetime
#from requests.exceptions import HTTPError

# Giả sử các hàm này cần được truy cập từ bên ngoài hoặc được truyền vào
# Nếu chúng thuộc về app.py và không được định nghĩa trong login_gui.py
# thì bạn cần truyền chúng như một phần của đối số args hoặc import chúng từ app.py
# Để đơn giản, tôi sẽ giả định chúng có thể được định nghĩa hoặc truy cập
# một cách phù hợp.

# Các biến toàn cục và hàm hỗ trợ nếu cần thiết cho us_login (nếu chúng không được truyền vào)
# Tuy nhiên, cách tốt nhất là truyền dữ liệu cần thiết thông qua args
# hoặc nếu các hàm này thực sự thuộc về một module utility chung, hãy đặt chúng ở đó.
# Ví dụ:
# from your_utility_module import get_path, update_user_info, update_api_key

# Đây là một định nghĩa tạm thời cho các hàm mà us_login cần
# Trong thực tế, bạn sẽ import chúng từ nơi chúng được định nghĩa (ví dụ: app.py hoặc một file util riêng)
def get_path1(relative_path):
    # Định nghĩa tạm thời, thay thế bằng định nghĩa thực tế của bạn
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

 # Cần định nghĩa hoặc import

if getattr(sys, 'frozen', False):    
    PATH_JSON_CONFIG = get_path1('../data/config.json')
else:
    PATH_JSON_CONFIG = get_path1('data/config.json')
#PATH_JSON_CONFIG = get_path('data/config.json')
    
API_KEY_LIST = [] # Cần định nghĩa hoặc import
API_KEY = '' # Cần định nghĩa hoặc import

def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_user_info(username='', mssv='', password=''):
    global API_KEY_LIST
    global API_KEY # Cần biến API_KEY toàn cục nếu bạn đang sửa đổi nó
    # Đây là logic từ app.py, cần được tái tạo hoặc import
    # Để tránh phụ thuộc vòng tròn, tốt nhất là chuyển logic này ra ngoài hoặc
    # truyền các hàm callback cần thiết vào lớp us_login
    config = None
    if os.path.exists(PATH_JSON_CONFIG):
        with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError:
                pass # Xử lý lỗi nếu file không hợp lệ

    if config is not None:
        config['user'][0]['username'] = username
        config['user'][0]['mssv'] = mssv
        config['user'][0]['password'] = password
        save_json_file(PATH_JSON_CONFIG, config)
    else:
        # Xử lý trường hợp config không tồn tại hoặc lỗi
        print("Cảnh báo: Không thể tải hoặc cập nhật config.json")


def update_api_key(id_sv):
    global API_KEY
    global API_KEY_LIST # Đảm bảo API_KEY_LIST được truy cập từ đâu đó
    if not API_KEY_LIST: # Tránh lỗi nếu API_KEY_LIST rỗng
        print("Cảnh báo: API_KEY_LIST trống. Không thể cập nhật API_KEY.")
        return

    num_api_key = len(API_KEY_LIST)
    if num_api_key > 0:
        index = id_sv % num_api_key
        API_KEY = API_KEY_LIST[index]
        print(f"idsv={id_sv} ; index={index} ; api_key={API_KEY}")
    else:
        print("Cảnh báo: Không có API Key nào trong danh sách.")


class LoginApp(tk.Toplevel):
    def __init__(self, master, firebase_auth, firebase_db, update_user_info_callback, update_api_key_callback, path_json_config):
        super().__init__(master)
        self.master = master
        self.auth = firebase_auth
        self.db = firebase_db
        self.update_user_info_callback = update_user_info_callback
        self.update_api_key_callback = update_api_key_callback
        self.path_json_config = path_json_config

        self.result = 'nok'

        self.title("Đăng nhập")
        # self.geometry("350x250") # XÓA HOẶC COMMENT DÒNG NÀY
        
        # THÊM ĐOẠN CODE NÀY VÀO ĐÂY ĐỂ TÍNH TOÁN KÍCH THƯỚC VÀ VỊ TRÍ
        # Lấy kích thước màn hình
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Kích thước cửa sổ đăng nhập mong muốn
        width = 350
        height = 250

        # Tính toán vị trí để căn giữa
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Đặt kích thước và vị trí cho cửa sổ
        self.geometry(f"{width}x{height}+{x}+{y}")
        # KẾT THÚC ĐOẠN CODE THÊM MỚI

        self.resizable(False, False)
        self.grab_set()
        self.focus_set()        
        
        # Tạo khung chứa các thành phần
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(expand=True, fill="both") # Thêm fill="both" để khung mở rộng ra

        # Tiêu đề (đã đặt trong frame)
        tk.Label(frame, text="ĐĂNG NHẬP / ĐĂNG KÝ", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Các thành phần khác như label và entry cho email, mật khẩu...
        # SỬA CÁC DÒNG NÀY ĐỂ CHẮC CHẮN CHÚNG LÀ CON CỦA `frame`, KHÔNG PHẢI `self`
        
        # Ví dụ: sửa các dòng như sau:
        # self.lbl_name = tk.Label(self, text="Email:")  # SAI
        # thành:
        self.lbl_email = tk.Label(frame, text="Email:") # ĐÚNG - lbl_email là con của frame
        self.lbl_email.grid(row=1, column=0, sticky='w', pady=5) # Sử dụng grid cho lbl_email bên trong frame

        self.txt_email = tk.Entry(frame, width=30) # txt_email cũng là con của frame
        self.txt_email.grid(row=1, column=1, pady=5) # Sử dụng grid cho txt_email bên trong frame

        # Tương tự với mật khẩu
        self.lbl_password = tk.Label(frame, text="Mật khẩu:")
        self.lbl_password.grid(row=2, column=0, sticky='w', pady=5)

        self.txt_password = tk.Entry(frame, show="*", width=30)
        self.txt_password.grid(row=2, column=1, pady=5)
        
        # Nút đăng nhập/đăng ký cũng phải là con của `frame`
        self.btn_submit = tk.Button(frame, text="Đăng nhập", command=self.btn_submit_click, font=("Arial", 12))
        self.btn_submit.grid(row=3, column=0, columnspan=2, pady=10)

        self.btn_register = tk.Button(frame, text="Đăng ký", command=self.btn_register_click, font=("Arial", 12))
        self.btn_register.grid(row=4, column=0, columnspan=2, pady=5)

        self.btn_forgot_password = tk.Button(frame, text="Quên mật khẩu?", command=self.btn_forgot_password_click, font=("Arial", 10), fg="blue", cursor="hand2")
        self.btn_forgot_password.grid(row=5, column=0, columnspan=2, pady=(0, 10))


        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.wait_window()

    def on_close(self):
        print('đóng cửa sổ')
        self.result = 'nok'
        self.destroy()
        
    #def btn_login_click(self):
    def btn_submit_click(self):
        #email_ = self.txt_mssv.get()
        email_ = self.txt_email.get()
        password_ = self.txt_password.get()

        if email_ == '' or password_ == '':
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ email và mật khẩu.")
            return

        try:
            # Đăng nhập bằng Firebase Authentication
            #user = self.firebase_auth.sign_in_with_email_and_password(email_, password_)
            user = self.auth.sign_in_with_email_and_password(email_, password_)
            print(f"Đăng nhập thành công: {user['email']}")

            # Lấy thông tin user từ Realtime Database hoặc Firestore nếu cần
            # Trong ví dụ này, chúng ta sẽ giả định username là phần trước @ của email hoặc tìm trong student_list
            username_for_db = email_.split('@')[0]
            uid = user['localId'] # Firebase UID

            # Cập nhật thông tin người dùng trong ứng dụng
            # self.dict_user_info[0]['mssv'] = uid  # Lưu UID làm mssv
            # self.dict_user_info[0]['username'] = username_for_db # Lưu username

            # Cập nhật thông tin người dùng và API key trong app.py
            self.update_user_info_callback(username=username_for_db, mssv=uid)
            self.update_api_key_callback(uid) # Truyền UID để chọn API Key (hoặc tạo mới)

            messagebox.showinfo('Thành công', f'Đăng nhập thành công: Xin chào {username_for_db}')
            self.result = 'ok'
            self.destroy()

        except Exception as e: # Catch any exception, including those wrapped by Pyrebase
            # Try to parse Firebase specific error message from the response text
            try:
                # Pyrebase wraps the original HTTPError, and the Firebase error JSON is in e.args[1]
                error_data = json.loads(e.args[1])
                error_message = error_data['error']['message']

                if "EMAIL_NOT_FOUND" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                    messagebox.showerror("Lỗi đăng nhập", "Email hoặc mật khẩu không đúng. Vui lòng kiểm tra lại.")
                elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
                    messagebox.showerror("Lỗi đăng nhập", "Tài khoản bị khóa do quá nhiều lần thử sai. Vui lòng thử lại sau.")
                else:
                    messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi Firebase: {error_message}")
            except (IndexError, json.JSONDecodeError, KeyError):
                # Fallback if e.args[1] is not present, not valid JSON, or missing 'error' key
                # This might catch non-Firebase HTTP errors too, but the prompt requests simplicity.
                messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi không xác định. Chi tiết: {e}")
            # No need for a second 'except Exception' block here, as it's already caught above.
            
        # except HTTPError as e: # Catch specific requests.exceptions.HTTPError
        #     # Try to parse Firebase specific error message from the response text
        #     try:
        #         # Pyrebase wraps the original HTTPError, and the Firebase error JSON is in e.args[1]
        #         error_data = json.loads(e.args[1])
        #         error_message = error_data['error']['message']

        #         if "EMAIL_NOT_FOUND" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
        #             messagebox.showerror("Lỗi đăng nhập", "Email hoặc mật khẩu không đúng. Vui lòng kiểm tra lại.")
        #         elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
        #             messagebox.showerror("Lỗi đăng nhập", "Tài khoản bị khóa do quá nhiều lần thử sai. Vui lòng thử lại sau.")
        #         else:
        #             messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi Firebase: {error_message}")
        #     except (IndexError, json.JSONDecodeError, KeyError):
        #         # Fallback if e.args[1] is not present, not valid JSON, or missing 'error' key
        #         messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi Firebase không xác định: {e}")
        # except Exception as e: # Catch any other unexpected errors
        #     messagebox.showerror("Lỗi", f"Đã xảy ra lỗi không mong muốn: {e}")
            
        #except self.auth.AuthError as e: # Catch specific Pyrebase AuthError first
        #except pyrebase.AuthError as e: # Catch specific Pyrebase AuthError first
        # except pyrebase.pyrebase.AuthError as e: # Catch specific Pyrebase AuthError first
        #     # Try to parse Firebase specific error message
        #     try:
        #         error_message = json.loads(e.args[1])['error']['message']
        #         if "EMAIL_NOT_FOUND" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
        #             messagebox.showerror("Lỗi đăng nhập", "Email hoặc mật khẩu không đúng. Vui lòng kiểm tra lại.")
        #         elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
        #             messagebox.showerror("Lỗi đăng nhập", "Tài khoản bị khóa do quá nhiều lần thử sai. Vui lòng thử lại sau.")
        #         else:
        #             messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi Firebase: {error_message}")
        #     except (IndexError, json.JSONDecodeError):
        #         # Fallback if e.args[1] is not present or not valid JSON
        #         messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi Firebase không xác định: {e}")
        # except Exception as e: # Catch any other unexpected errors
        #     messagebox.showerror("Lỗi", f"Đã xảy ra lỗi không mong muốn: {e}")
        #except pyrebase.AuthError as e:
        #except self.auth.AuthError as e:
        # except Exception as e:
        #     error_message = json.loads(e.args[1])['error']['message']
        #     if "EMAIL_NOT_FOUND" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
        #         messagebox.showerror("Lỗi đăng nhập", "Email hoặc mật khẩu không đúng. Vui lòng kiểm tra lại.")
        #     elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
        #          messagebox.showerror("Lỗi đăng nhập", "Tài khoản bị khóa do quá nhiều lần thử sai. Vui lòng thử lại sau.")
        #     else:
        #         messagebox.showerror("Lỗi đăng nhập", f"Đã xảy ra lỗi Firebase: {error_message}")
        # except Exception as e:
        #     messagebox.showerror("Lỗi", f"Đã xảy ra lỗi không mong muốn: {e}")

    # def btn_submit_click(self):
    #     # Logic đăng nhập hiện tại sẽ được cập nhật ở bước sau
    #     # Hiện tại, bạn có thể để nó trống hoặc giữ lại logic cũ nếu muốn test GUI trước
    #     email = self.txt_email.get()
    #     password = self.txt_password.get()
    #     if not email or not password:
    #         messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Email và Mật khẩu.")
    #         return
    #     print(f"Đăng nhập với Email: {email}, Mật khẩu: {password}")
    #     # Logic Firebase sẽ được thêm vào đây sau

    # def btn_register_click(self):
    #     email_ = self.txt_email.get()
    #     password_ = self.txt_password.get()

    #     if not email_ or not password_:
    #         messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Email và Mật khẩu để đăng ký.")
    #         return

    #     try:
    #         # Bước 1: Đăng ký người dùng mới với Firebase Authentication
    #         # create_user_with_email_and_password không tự động đăng nhập.
    #         # Nó trả về một đối tượng user nếu thành công.
    #         new_user = self.auth.create_user_with_email_and_password(email_, password_)
            
    #         # Nếu đăng ký thành công, tự động đăng nhập để lấy thông tin UID
    #         user_signed_in = self.auth.sign_in_with_email_and_password(email_, password_)
    #         uid = user_signed_in['localId'] # Lấy UID của người dùng mới

    #         # Bước 2: Tùy chọn: Lưu thông tin bổ sung vào Firebase Realtime Database
    #         # (Ví dụ: lưu email và một username mặc định dưới node 'users/UID')
    #         username_for_db = email_.split('@')[0] # Lấy phần trước @ làm username mặc định
    #         self.db.child("users").child(uid).set({
    #             "email": email_,
    #             "username": username_for_db,
    #             "created_at": tk.StringVar().set(datetime.now().isoformat()) # Lưu thời gian tạo
    #         })

    #         # Bước 3: Cập nhật thông tin người dùng trong ứng dụng chính (nếu cần)
    #         self.update_user_info_callback(username=username_for_db, mssv=uid)
    #         self.update_api_key_callback(uid) # Truyền UID để chọn API Key (hoặc tạo mới)

    #         messagebox.showinfo("Thành công", f"Đăng ký tài khoản '{email_}' thành công! Đã tự động đăng nhập.")
    #         self.result = 'ok' # Đặt kết quả là 'ok' để cửa sổ chính hiển thị
    #         self.destroy() # Đóng cửa sổ đăng nhập

        
    #     # except Exception as e:
    #     #     # Xử lý các lỗi cụ thể từ Firebase Authentication
    #     #     error_message = json.loads(e.args[1])['error']['message']
    #     #     if "EMAIL_EXISTS" in error_message:
    #     #         messagebox.showerror("Lỗi đăng ký", "Email này đã được sử dụng. Vui lòng thử một email khác hoặc đăng nhập.")
    #     #     elif "WEAK_PASSWORD" in error_message:
    #     #         messagebox.showerror("Lỗi đăng ký", "Mật khẩu quá yếu. Vui lòng sử dụng mật khẩu mạnh hơn (ít nhất 6 ký tự).")
    #     #     elif "INVALID_EMAIL" in error_message:
    #     #         messagebox.showerror("Lỗi đăng ký", "Email không hợp lệ.")
    #     #     else:
    #     #         messagebox.showerror("Lỗi đăng ký", f"Đã xảy ra lỗi Firebase: {error_message}")
    #     # except Exception as e:
    #     #     messagebox.showerror("Lỗi", f"Đã xảy ra lỗi không mong muốn: {e}")
        
    #     except Exception as e: # Catch any exception during registration
    #         error_message = "Đã xảy ra lỗi không xác định." # Default message
    #         try:
    #             # Attempt to parse as a detailed Pyrebase AuthError (e.g., weak password, email exists)
    #             error_data = json.loads(e.args[1])
    #             error_message = error_data['error']['message']

    #             if "EMAIL_EXISTS" in error_message:
    #                 messagebox.showerror("Lỗi đăng ký", "Email này đã được sử dụng. Vui lòng thử một email khác hoặc đăng nhập.")
    #             elif "WEAK_PASSWORD" in error_message:
    #                 messagebox.showerror("Lỗi đăng ký", "Mật khẩu quá yếu. Vui lòng sử dụng mật khẩu mạnh hơn (ít nhất 6 ký tự).")
    #             elif "INVALID_EMAIL" in error_message:
    #                 messagebox.showerror("Lỗi đăng ký", "Email không hợp lệ.")
    #             else:
    #                 # Catch other Firebase specific errors
    #                 messagebox.showerror("Lỗi đăng ký", f"Đã xảy ra lỗi Firebase: {error_message}")
    #         except (IndexError, json.JSONDecodeError, KeyError):
    #             # This branch handles cases where e.args[1] is not present, not valid JSON,
    #             # or the JSON structure does not have ['error']['message'] (like the 404 error)
    #             if "404 Client Error: Not Found" in str(e):
    #                  messagebox.showerror("Lỗi đăng ký", "Lỗi cấu hình Database hoặc quyền truy cập. Vui lòng kiểm tra Firebase Realtime Database URL và Rules.")
    #             else:
    #                 # Fallback for other non-parsable exceptions
    #                 messagebox.showerror("Lỗi đăng ký", f"Đã xảy ra lỗi không mong muốn trong quá trình xử lý: {e}")
    #         except Exception as inner_e: # This nested catch is for errors *during parsing*
    #             messagebox.showerror("Lỗi đăng ký", f"Đã xảy ra lỗi không mong muốn khi xử lý lỗi: {inner_e}")
        

    # def btn_register_click(self):
    #     email_ = self.txt_mssv.get()
    #     password_ = self.txt_password.get()
    #     username_ = self.txt_username.get()

    #     if email_ == '' or password_ == '' or username_ == '':
    #         messagebox.showerror("Lỗi", "Thông tin cần nhập đầy đủ (Email, Mật khẩu, Tên người dùng).")
    #         return

    #     try:
    #         # Đăng ký tài khoản mới với Firebase Authentication
    #         user = self.firebase_auth.create_user_with_email_and_password(email_, password_)
    #         print(f"Đăng ký thành công: {user['email']}")

    #         uid = user['localId'] # Firebase UID

    #         # Lưu thông tin sinh viên vào student.json và cập nhật config.json
    #         # Lấy ID lớn nhất hiện có hoặc khởi tạo là 0
    #         new_id = 0
    #         if self.student_list:
    #             new_id = max([s.get('id', 0) for s in self.student_list]) + 1
            
    #         # Tạo thông tin sinh viên mới
    #         new_student = {
    #             "id": new_id,
    #             "idsv": uid, # Sử dụng UID Firebase làm ID sinh viên
    #             "name": username_,
    #             "password": password_, # Lưu mật khẩu, cân nhắc mã hóa trong ứng dụng thực tế
    #             "email": email_ # Lưu email
    #         }
    #         self.student_list.append(new_student)

    #         # Lưu danh sách sinh viên đã cập nhật vào file
    #         try:
    #             with open(self.path_student_list, 'w', encoding='utf-8') as f:
    #                 json.dump(self.student_list, f, indent=2, ensure_ascii=False)
    #             print(f"Đã thêm sinh viên mới vào {self.path_student_list}")
    #         except Exception as e:
    #             messagebox.showwarning("Cảnh báo", f"Không thể lưu thông tin sinh viên vào file cục bộ: {e}")

    #         # Cập nhật config.json với thông tin người dùng mới và chọn API Key
    #         self.update_user_info_callback(username=username_, mssv=uid, password=password_)
    #         self.update_api_key_callback(uid) # Truyền UID để chọn API Key (hoặc tạo mới)

    #         messagebox.showinfo("Thành công", f"Đăng ký tài khoản '{email_}' thành công! Đã tự động đăng nhập.")
    #         self.result = 'ok' # Đặt kết quả là 'ok' để cửa sổ chính hiển thị
    #         self.destroy() # Đóng cửa sổ đăng nhập

    #     #except pyrebase.AuthError as e:
    #     except Exception as e:
    #         # Xử lý các lỗi cụ thể từ Firebase Authentication
    #         error_message = json.loads(e.args[1])['error']['message']
    #         if "EMAIL_EXISTS" in error_message:
    #             messagebox.showerror("Lỗi đăng ký", "Email này đã được sử dụng. Vui lòng thử một email khác hoặc đăng nhập.")
    #         elif "WEAK_PASSWORD" in error_message:
    #             messagebox.showerror("Lỗi đăng ký", "Mật khẩu quá yếu. Vui lòng sử dụng mật khẩu mạnh hơn (ít nhất 6 ký tự).")
    #         elif "INVALID_EMAIL" in error_message:
    #             messagebox.showerror("Lỗi đăng ký", "Email không hợp lệ.")
    #         else:
    #             messagebox.showerror("Lỗi đăng ký", f"Đã xảy ra lỗi Firebase: {error_message}")
    #     # except Exception as e:
    #     #     messagebox.showerror("Lỗi", f"Đã xảy ra lỗi không mong muốn: {e}")
            
    # def btn_register_click(self):
    #     email_ = self.txt_email.get()
    #     password_ = self.txt_password.get()

    #     if not email_ or not password_:
    #         messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Email và Mật khẩu để đăng ký.")
    #         return

    #     try:
    #         # Bước 1: Đăng ký người dùng mới với Firebase Authentication
    #         new_user = self.auth.create_user_with_email_and_password(email_, password_)
            
    #         # Nếu đăng ký thành công, tự động đăng nhập để lấy thông tin UID
    #         user_signed_in = self.auth.sign_in_with_email_and_password(email_, password_)
    #         uid = user_signed_in['localId'] # Lấy UID của người dùng mới

    #         # Bước 2: Tùy chọn: Lưu thông tin bổ sung vào Firebase Realtime Database
    #         # (Ví dụ: lưu email và một username mặc định dưới node 'users/UID')
    #         username_for_db = email_.split('@')[0] # Lấy phần trước @ làm username mặc định
    #         self.db.child("users").child(uid).set({
    #             "email": email_,
    #             "username": username_for_db,
    #             "created_at": datetime.now().isoformat() # CORRECTED: Removed tk.StringVar().set()
    #         })

    #         # Bước 3: Cập nhật thông tin người dùng trong ứng dụng chính (nếu cần)
    #         self.update_user_info_callback(username=username_for_db, mssv=uid)
    #         self.update_api_key_callback(uid) # Truyền UID để chọn API Key (hoặc tạo mới)

    #         messagebox.showinfo("Thành công", f"Đăng ký tài khoản '{email_}' thành công! Đã tự động đăng nhập.")
    #         self.result = 'ok'
    #         self.destroy()

    #     except Exception as e: # Catch any exception, including HTTPError and AuthError
    #         error_message = "Đã xảy ra lỗi không xác định." # Default message
    #         try:
    #             # Attempt to parse as a detailed Pyrebase AuthError (e.g., weak password, email exists)
    #             error_data = json.loads(e.args[1])
    #             error_message = error_data['error']['message']

    #             if "EMAIL_EXISTS" in error_message:
    #                 messagebox.showerror("Lỗi đăng ký", "Email này đã được sử dụng. Vui lòng thử một email khác hoặc đăng nhập.")
    #             elif "WEAK_PASSWORD" in error_message:
    #                 messagebox.showerror("Lỗi đăng ký", "Mật khẩu quá yếu. Vui lòng sử dụng mật khẩu mạnh hơn (ít nhất 6 ký tự).")
    #             elif "INVALID_EMAIL" in error_message:
    #                 messagebox.showerror("Lỗi đăng ký", "Email không hợp lệ.")
    #             else:
    #                 messagebox.showerror("Lỗi đăng ký", f"Đã xảy ra lỗi Firebase: {error_message}")
    #         except (IndexError, json.JSONDecodeError, KeyError):
    #             # This branch handles cases where e.args[1] is not present, not valid JSON,
    #             # or the JSON structure does not have ['error']['message'] (like the 404 error)
    #             if "404 Client Error: Not Found" in str(e):
    #                  messagebox.showerror("Lỗi đăng ký", "Lỗi cấu hình Database hoặc quyền truy cập. Vui lòng kiểm tra Firebase Realtime Database URL và Rules.")
    #             else:
    #                 # Fallback for other non-parsable exceptions
    #                 messagebox.showerror("Lỗi đăng ký", f"Đã xảy ra lỗi không mong muốn trong quá trình xử lý: {e}")

    # def btn_register_click(self):
    #     email_ = self.txt_email.get()
    #     password_ = self.txt_password.get()

    #     if not email_ or not password_:
    #         messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Email và Mật khẩu để đăng ký.")
    #         return

    #     try:
    #         # Bước 1: Đăng ký người dùng mới với Firebase Authentication
    #         new_user = self.auth.create_user_with_email_and_password(email_, password_)
            
    #         # Nếu đăng ký thành công, tự động đăng nhập để lấy thông tin UID
    #         user_signed_in = self.auth.sign_in_with_email_and_password(email_, password_)
    #         uid = user_signed_in['localId'] # Lấy UID của người dùng mới

    #         # Bước 2: Tùy chọn: Lưu thông tin bổ sung vào Firebase Realtime Database
    #         # (Ví dụ: lưu email và một username mặc định dưới node 'users/UID')
    #         username_for_db = email_.split('@')[0] # Lấy phần trước @ làm username mặc định
    #         self.db.child("users").child(uid).set({
    #             "email": email_,
    #             "username": username_for_db,
    #             "created_at": datetime.now().isoformat() # CORRECTED: Removed tk.StringVar().set()
    #         })

    #         # Bước 3: Cập nhật thông tin người dùng trong ứng dụng chính (nếu cần)
    #         self.update_user_info_callback(username=username_for_db, mssv=uid)
    #         self.update_api_key_callback(uid) # Truyền UID để chọn API Key (hoặc tạo mới)

    #         messagebox.showinfo("Thành công", f"Đăng ký tài khoản '{email_}' thành công! Đã tự động đăng nhập.")
    #         self.result = 'ok'
    #         self.destroy()

    #     except Exception as e: # Catch any exception, including HTTPError and AuthError
    #         error_message = "Đã xảy ra lỗi không xác định." # Default message
    #         try:
    #             # Attempt to parse as a detailed Pyrebase AuthError (e.g., weak password, email exists)
    #             error_data = json.loads(e.args[1])
    #             error_message = error_data['error']['message']

    #             if "EMAIL_EXISTS" in error_message:
    #                 messagebox.showerror("Lỗi đăng ký", "Email này đã được sử dụng. Vui lòng thử một email khác hoặc đăng nhập.")
    #             elif "WEAK_PASSWORD" in error_message:
    #                 messagebox.showerror("Lỗi đăng ký", "Mật khẩu quá yếu. Vui lòng sử dụng mật khẩu mạnh hơn (ít nhất 6 ký tự).")
    #             elif "INVALID_EMAIL" in error_message:
    #                 messagebox.showerror("Lỗi đăng ký", "Email không hợp lệ.")
    #             else:
    #                 messagebox.showerror("Lỗi đăng ký", f"Đã xảy ra lỗi Firebase: {error_message}")
    #         except (IndexError, json.JSONDecodeError, KeyError):
    #             # This branch handles cases where e.args[1] is not present, not valid JSON,
    #             # or the JSON structure does not have ['error']['message'] (like the 404 error)
    #             if "404 Client Error: Not Found" in str(e):
    #                  messagebox.showerror("Lỗi đăng ký", "Lỗi cấu hình Database hoặc quyền truy cập. Vui lòng kiểm tra Firebase Realtime Database URL và Rules.")
    #             else:
    #                 # Fallback for other non-parsable exceptions
    #                 messagebox.showerror("Lỗi đăng ký", f"Đã xảy ra lỗi không mong muốn trong quá trình xử lý: {e}")

    def btn_register_click(self):
        email_ = self.txt_email.get()
        password_ = self.txt_password.get()

        if not email_ or not password_:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Email và Mật khẩu để đăng ký.")
            return

        try:
            # Bước 1: Đăng ký người dùng mới với Firebase Authentication
            new_user = self.auth.create_user_with_email_and_password(email_, password_)
            
            # Nếu đăng ký thành công, tự động đăng nhập để lấy thông tin UID
            user_signed_in = self.auth.sign_in_with_email_and_password(email_, password_)
            uid = user_signed_in['localId'] # Lấy UID của người dùng mới

            # Bước 2: Tùy chọn: Lưu thông tin bổ sung vào Firebase Realtime Database
            username_for_db = email_.split('@')[0] # Lấy phần trước @ làm username mặc định
            self.db.child("users").child(uid).set({
                "email": email_,
                "username": username_for_db,
                "created_at": datetime.now().isoformat() # CORRECTED: Removed tk.StringVar().set()
            })

            # Bước 3: Cập nhật thông tin người dùng trong ứng dụng chính (nếu cần)
            self.update_user_info_callback(username=username_for_db, mssv=uid)
            self.update_api_key_callback(uid) # Truyền UID để chọn API Key (hoặc tạo mới)

            messagebox.showinfo("Thành công", f"Đăng ký tài khoản '{email_}' thành công! Đã tự động đăng nhập.")
            self.result = 'ok'
            self.destroy()

        except Exception as e: # Catch any exception during registration (including HTTPError)
            print(f"DEBUG: Full exception details caught: {e}") # ADD THIS LINE TO PRINT TO CONSOLE
            error_message_display = "Đã xảy ra lỗi không xác định." # Default message for display
            
            raw_error_text = ""
            if len(e.args) > 1:
                raw_error_text = e.args[1]
                print(f"DEBUG: Raw error text from e.args[1]: {raw_error_text}") # For debugging

            try:
                # Attempt to parse as a detailed Pyrebase AuthError (e.g., weak password, email exists)
                error_data = json.loads(raw_error_text)
                
                # Check if 'error' is a dict and has 'message'
                if isinstance(error_data, dict) and 'error' in error_data and \
                   isinstance(error_data['error'], dict) and 'message' in error_data['error']:
                    error_message = error_data['error']['message'] # This is the expected Firebase Auth message
                    
                    if "EMAIL_EXISTS" in error_message:
                        error_message_display = "Email này đã được sử dụng. Vui lòng thử một email khác hoặc đăng nhập."
                    elif "WEAK_PASSWORD" in error_message:
                        error_message_display = "Mật khẩu quá yếu. Vui lòng sử dụng mật khẩu mạnh hơn (ít nhất 6 ký tự)."
                    elif "INVALID_EMAIL" in error_message:
                        error_message_display = "Email không hợp lệ."
                    else:
                        error_message_display = f"Đã xảy ra lỗi Firebase: {error_message}"
                elif isinstance(error_data, dict) and 'error' in error_data and \
                     isinstance(error_data['error'], str) and ("404 Not Found" in error_data['error'] or "Permission denied" in error_data['error']):
                    # This specifically handles the {"error": "404 Not Found"} or {"error": "Permission denied"} case
                    error_message_display = "Lỗi cấu hình Database hoặc quyền truy cập. Vui lòng kiểm tra Firebase Realtime Database URL và Rules."
                else:
                    error_message_display = f"Đã xảy ra lỗi Firebase với định dạng không mong muốn: {raw_error_text}"

            except (json.JSONDecodeError, IndexError):
                # If raw_error_text is not valid JSON or e.args[1] is missing/empty
                if "404 Client Error: Not Found" in str(e):
                    error_message_display = "Lỗi cấu hình Database hoặc quyền truy cập. Vui lòng kiểm tra Firebase Realtime Database URL và Rules."
                elif "401 Client Error: Unauthorized" in str(e) or "Permission denied" in str(e):
                    error_message_display = "Lỗi quyền truy cập Realtime Database. Vui lòng kiểm tra Rules."
                elif "requests.exceptions.HTTPError" in str(e): # Generic HTTP error not parsed as JSON
                    error_message_display = f"Lỗi phản hồi từ server: {str(e)}"
                else:
                    error_message_display = f"Đã xảy ra lỗi không xác định trong quá trình xử lý: {e}"
            except Exception as inner_e: # Catch any other unexpected errors *during this parsing attempt*
                error_message_display = f"Đã xảy ra lỗi không mong muốn khi xử lý lỗi: {inner_e}. Chi tiết gốc: {e}"
            
            messagebox.showerror("Lỗi đăng ký", error_message_display)
            
    def btn_forgot_password_click(self):
        # Phương thức này sẽ xử lý việc đặt lại mật khẩu
        messagebox.showinfo("Thông báo", "Chức năng quên mật khẩu sẽ được triển khai.")
        # Logic Firebase quên mật khẩu sẽ được thêm vào đây sau
        