import tkinter as tk
from tkinter import messagebox
import json
import os
import sys

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
def get_path(relative_path):
    # Định nghĩa tạm thời, thay thế bằng định nghĩa thực tế của bạn
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

PATH_JSON_CONFIG = get_path('data/config.json') # Cần định nghĩa hoặc import
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


class us_login(tk.Toplevel):

    def __init__(self, parent, args, width=300, height=150):
        super().__init__(parent)
        self.title('Đăng nhập')
        self.result = 'nok'

        self.dict_user = args['dict_user']
        self.student_list = args['student_list']
        # Lấy các hàm callback từ args nếu chúng được truyền vào từ main app
        # self.update_user_info_callback = args.get('update_user_info_callback', update_user_info)
        # self.update_api_key_callback = args.get('update_api_key_callback', update_api_key)


        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.transient(parent)
        self.grab_set()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.lbl_name = tk.Label(self, text='Đăng Nhập hệ thống', font=("Arial", 14), bg='green', fg='white')
        self.lbl_name.grid(row=0, column=0, columnspan=2, sticky='nswe', pady=5)

        self.lbl_mssv = tk.Label(self, text='ID sinh viên', font=("Arial", 12))
        self.lbl_mssv.grid(row=1, column=0, sticky='ns')

        self.txt_mssv = tk.Entry(self, font=("Arial", 12))
        self.txt_mssv.grid(row=1, column=1, sticky='we', padx=5, pady=10)

        if self.dict_user is not None and self.dict_user: # Kiểm tra dict_user không rỗng
            if 'mssv' in self.dict_user[0]: # Kiểm tra khóa 'mssv' tồn tại
                mssv = self.dict_user[0]['mssv']
                self.txt_mssv.delete(0, tk.END)
                self.txt_mssv.insert(0, mssv)

        btn_submit = tk.Button(self, text='Đăng nhập', command=self.btn_submit_click, font=("Arial", 12))
        btn_submit.grid(row=2, column=0, columnspan=2, sticky='n', pady=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.wait_window()

    def on_close(self):
        print('đóng cửa sổ')
        self.result = 'nok'
        self.destroy()

    def btn_submit_click(self):
        mssv_ = self.txt_mssv.get()
        if mssv_ == '':
            messagebox.showerror("Lỗi", "Thông tin cần nhập đầy đủ")
        else:
            print(mssv_)
            found_student = False
            for student in self.student_list:
                if student.get('idsv') == mssv_: # Sử dụng .get() để tránh KeyError
                    name_ = student.get('name')
                    id_ = int(student.get('id', 0)) # Mặc định là 0 nếu 'id' không tồn tại

                    self.dict_user[0]['mssv'] = mssv_
                    self.dict_user[0]['username'] = name_

                    # Gọi các hàm cập nhật. Sử dụng hàm tạm thời hoặc hàm được truyền vào
                    update_user_info(name_, mssv_) # hoặc self.update_user_info_callback(...)
                    update_api_key(id_) # hoặc self.update_api_key_callback(...)

                    messagebox.showinfo('info', f'Đăng nhập thành công: Xin chào {name_}')
                    self.result = 'ok'
                    self.destroy()
                    found_student = True
                    return
            if not found_student:
                messagebox.showerror('error', 'Đăng nhập không thành công')