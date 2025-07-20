from usercustomize import *
#threading
import threading

#flask
from flask import Flask,jsonify,request
from flask_caching import Cache
from flask_httpauth import HTTPTokenAuth
import logging

#image
from PIL import Image as PILImage, ImageTk
import matplotlib.pyplot  as plt

#tkinter
from tkinter import *
from tkinter import messagebox,scrolledtext
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
import os
import requests

from queue import Queue,Empty
import json
from datetime import datetime
import glob
import google.generativeai as genai
from prompt.rule import continue_conversation_rule,help_promt,json_sessions_to_markdown,create_main_rule,re_response_prompt
from compiler_c import *
import markdown
from tkhtmlview import HTMLLabel
import ast
import re
from tkcode import CodeEditor
import tkcode
import unicodedata
import codecs
import time
from enum import Enum

#for About
from tkinter import messagebox, ttk, scrolledtext, Toplevel, Label, Text, PhotoImage

#for login
from login_gui import *

from datetime import datetime, timedelta

#for export json
import shutil

#for browser display
import webbrowser
import pathlib

from google_driver_api import upload_file_to_driver,upload_file_course,download_file_course_from_driver,upload_img,extract_zip_overwrite,download_file_img_from_driver

#for download compiler 
from compiler_manager import download_and_extract_compiler

#for firebase
import pyrebase

import random
#for icon bar
from PIL import Image, ImageTk
# ----------------------------------------------------
# KHỞI TẠO CẤU HÌNH FIREBASE - CẬP NHẬT CÁC GIÁ TRỊ TỪ BƯỚC NÀY
firebaseConfig = {
  "apiKey": "AIzaSyAgTDYs03DJ8FOHjL0v_EfD4R3TQoPUheM", # Dán giá trị từ Firebase Console vào đây
  "authDomain": "tutoraiexercisesteps.firebaseapp.com", # Dán giá trị từ Firebase Console vào đây
  "databaseURL": "https://tutoraiexercisesteps-default-rtdb.firebaseio.com/", # THÊM DÒNG NÀY VÀ THAY tutoraiexercisesteps BẰNG projectId CỦA BẠN (nếu bạn dùng Realtime Database)
  "projectId": "tutoraiexercisesteps", # Dán giá trị từ Firebase Console vào đây
  "storageBucket": "tutoraiexercisesteps.firebasestorage.app", # Dán giá trị từ Firebase Console vào đây
  "messagingSenderId": "396805630899", # Dán giá trị từ Firebase Console vào đây
  "appId": "1:396805630899:web:7ca9be22701f35589b79c6" # Dán giá trị từ Firebase Console vào đây
}

firebase = pyrebase.initialize_app(firebaseConfig)

# Lấy tham chiếu đến các dịch vụ Firebase
auth = firebase.auth()
db = firebase.database() # Nếu bạn dùng Realtime Database

# để import file docx tạo bài tập cho môn học mới môn học mới
from docx_importer import process_docx_to_json

##########Biến toàn cục #################################################################################

# Import các biến đường dẫn đã được định nghĩa tập trung từ usercustomize
from usercustomize import (
    PATH_DATA, PATH_LOG, PATH_CACHE, PATH_DOWNLOAD, PATH_UPLOAD,
    PATH_COMPILER, PATH_IMG,
    initialize_app_folders
)

# Khởi tạo tất cả các thư mục cần thiết một lần duy nhất khi ứng dụng bắt đầu
initialize_app_folders()

# Định nghĩa các đường dẫn file cụ thể dựa trên các biến đã import
PATH_JSON_CONFIG = os.path.join(PATH_DATA, 'config.json')
PATH_JSON_COURSE = os.path.join(PATH_DATA, 'course.json')
PATH_JSON_COURSE_UPDATE = os.path.join(PATH_DATA, 'course_update.json')
PATH_JSON_RULE = os.path.join(PATH_DATA, 'rule.md')
PATH_STUDENT_LIST = os.path.join(PATH_DATA, 'student.json')

# KẾT THÚC PHẦN THAY THẾ

APP_VERSION='1.0'
CACHE_STATUS=0
STUDENT_LIST=[]
API_KEY_LIST=[]
API_KEY=''
ACCOUNT_ROLE=''
MODEL=None # Đã sửa NONE thành None
DICT_USER_INFO=None
CURRENT_USER_TOKEN = None
json_course=None
main_rule=''
model=None
history=[]
queue = Queue()
queue_log=Queue()
ID_EXERCISE=None
MAX_RETRY=2

COURSE_FILE_MAP = {} # Biến mới để lưu ánh xạ từ tên môn học -> đường dẫn file JSON

#thông tin cho prompt môn học
CURRENT_COURSE_NAME = ""
CURRENT_COURSE_LANGUAGE = ""

#ngôn ngữ của compiler
CURRENT_EXERCISE_LANGUAGE = ""

# Biến toàn cục mới để theo dõi trạng thái đăng nhập
IS_LOGGED_IN = False

# Thêm class này vào để tạo chú thích cho icon
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1,
                         font=("Arial", "9", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = None
        
class SplashScreen(tk.Toplevel):
    """Lớp tạo màn hình chờ đơn giản."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Splash")
        self.geometry("400x250")
        self.overrideredirect(True) # Bỏ viền và các nút của cửa sổ

        # Canh giữa màn hình
        parent.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (parent.winfo_screenwidth() // 2) - (width // 2)
        y = (parent.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        # Thêm logo và text
        try:
            logo_path = os.path.join(PATH_IMG, 'LOGO_UDA.png')
            img = PILImage.open(logo_path).resize((120, 50), PILImage.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.logo_img).pack(pady=(30, 10))
        except Exception as e:
            print(f"Không thể tải logo cho splash screen: {e}")
            tk.Label(self, text="Tutor AI", font=("Arial", 24, "bold")).pack(pady=(30, 10))

        tk.Label(self, text="Đang khởi tạo, vui lòng chờ...", font=("Arial", 12)).pack(pady=5)
        self.update()
        
class CompilerDownloadDialog(tk.Toplevel):
    def __init__(self, parent, compiler_map, missing_compilers):
        super().__init__(parent)
        self.title("Cài đặt và Cập nhật Compiler")
        self.geometry("500x350") # Tăng kích thước cửa sổ một chút
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.compiler_map = compiler_map
        self.vars = {}
        self.to_download = []
        self.current_download_index = 0

        tk.Label(self, text="Kiểm tra các trình biên dịch cần thiết.", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        tk.Label(self, text="Chọn các mục cần tải và cài đặt:").pack(pady=5)

        frame_checks = tk.Frame(self)
        frame_checks.pack(pady=10, padx=20, fill='x')

        for name, data in self.compiler_map.items():
            self.vars[name] = tk.BooleanVar()
            is_missing = name in missing_compilers
            cb = tk.Checkbutton(frame_checks, text=f"Compiler cho {name.upper()}", variable=self.vars[name], font=("Arial", 10))
            cb.pack(anchor='w')
            
            if is_missing:
                self.vars[name].set(True)
                cb.config(fg="red")
            else:
                self.vars[name].set(False)
                cb.config(state="disabled", text=f"Compiler cho {name.upper()} (Đã cài đặt)")

        # THAY ĐỔI 1: Thay thế Label bằng ScrolledText để hiển thị nhiều dòng
        self.status_log = scrolledtext.ScrolledText(self, height=5, wrap=tk.WORD, font=("Arial", 9), state='disabled')
        self.status_log.pack(pady=5, padx=10, fill='both', expand=True)

        self.download_button = tk.Button(self, text="Tải và Cài đặt các mục đã chọn", command=self.start_download_sequence)
        self.download_button.pack(pady=10)

        self.wait_window()

    def log_status(self, message):
        """Hàm an toàn để ghi log vào ScrolledText từ bất kỳ luồng nào."""
        def _update_widget():
            self.status_log.config(state='normal')
            self.status_log.insert(tk.END, message + "\n")
            self.status_log.see(tk.END) # Tự động cuộn xuống dòng cuối
            self.status_log.config(state='disabled')
        # Lên lịch cập nhật trên luồng chính của GUI
        self.after(0, _update_widget)

    def on_progress_and_finish(self, status_message):
        """
        Callback duy nhất xử lý cả tiến trình và tín hiệu hoàn tất.
        """
        # Ghi lại mọi thông điệp trạng thái nhận được
        self.log_status(status_message)

        # Chỉ hành động khi nhận được thông báo kết thúc (thành công hoặc lỗi)
        if status_message.startswith("✓") or status_message.startswith("✗"):
            # Tăng chỉ số để chuẩn bị cho lần tải tiếp theo
            self.current_download_index += 1
            # Lên lịch cho lần tải tiếp theo để đảm bảo an toàn cho GUI
            self.after(100, self.trigger_next_download)
    
    def trigger_next_download(self):
        """Bắt đầu tải compiler tiếp theo trong danh sách."""
        if self.current_download_index < len(self.to_download):
            name = self.to_download[self.current_download_index]
            url = self.compiler_map[name]['url']
            
            self.log_status(f"--- Bắt đầu tác vụ cho {name.upper()} ---")
            
            # Gọi hàm tải và truyền vào callback duy nhất
            download_and_extract_compiler(name, url, self.on_progress_and_finish)
        else:
            # Khi tất cả các tác vụ trong danh sách đã hoàn tất
            self.log_status("--- Hoàn tất tất cả tác vụ! ---")
            messagebox.showinfo("Hoàn tất", "Quá trình cài đặt đã kết thúc. Vui lòng kiểm tra log bên dưới.")
            self.download_button.config(text="Đóng", state="normal", command=self.destroy)

    def start_download_sequence(self):
        """Bắt đầu chuỗi tải xuống tuần tự."""
        self.download_button.config(state="disabled")
        
        # Xóa log cũ trước khi bắt đầu
        self.status_log.config(state='normal')
        self.status_log.delete('1.0', tk.END)
        self.status_log.config(state='disabled')

        self.to_download = [name for name, var in self.vars.items() if var.get()]
        
        if not self.to_download:
            messagebox.showinfo("Thông báo", "Không có compiler nào được chọn để tải.")
            self.download_button.config(state="normal")
            return
            
        self.current_download_index = 0
        self.trigger_next_download() # Bắt đầu tác vụ đầu tiên

######## Khai báo lớp ##########
class ExerciseStatus(Enum):
    COMPLETED = "✓"
    INCOMPLETE = "✗"

class label_image(tk.Frame):
    def __init__(self, parent, path_image,title):
        super().__init__(parent)
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=0)
        img_ = PILImage.open(path_image)
        tk_img = ImageTk.PhotoImage(img_)
        self.label_img = tk.Label(self, image=tk_img)
        self.label_img.image = tk_img  # giữ tham chiếu
        self.label_img.grid(row=0,column=0,sticky='nswe')
       
       
        self.label_title = tk.Label(self, text=title, font=("Arial", 12), fg="blue")
        self.label_title.grid(row=1,column=0,sticky='s') 
        
class us_gemini_image_description(tk.Frame):
    
    def __init__(self, parent,model):
        super().__init__(parent)
        
    
        self.model=model
        self.output_text=tk.Text(self,wrap="word", font=("Arial", 11))
        self.image_label=tk.Label(self)
        self.upload_button = tk.Button(self, text="📁 Chọn ảnh để mô tả", command=self.upload_and_process_image, font=("Arial", 12))

        self.columnconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=1)
        
        self.grid(row=0,column=0,sticky='nswe')
        self.upload_button.grid(row=0,column=0,sticky='ns')
        self.image_label.grid(row=1,column=0,sticky='nswe')
        self.output_text.grid(row=2,column=0,sticky='nswe')
        
    def describe_image_with_gemini(self,image_path):
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()

        try:
            response = self.model.generate_content([
                "Tôi cần lấy mô tả ảnh để cung cấp cho hệ thống AI hiểu trong các ứng dụng liên quan đến ảnh. Hãy mô tả chi tiết ảnh này bằng tiếng việt, tôi sẽ lưu kết quả này vào chuỗi nên và **lưu ý:chỉ ghi trên một dòng, chú ý escape sao cho khi gán vào chuỗi sẽ hợp lệ**",
                {"mime_type": "image/png", "data": image_bytes}
            ])
            return response.text
        except Exception as e:
            return f"Lỗi: {e}"
        
    def upload_and_process_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not file_path:
            return

        # Gửi ảnh đến Gemini để mô tả
        result = self.describe_image_with_gemini(file_path)

        # Hiển thị mô tả lên TextBox
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, result)

        # Hiển thị preview ảnh
        img = PILImage.open(file_path)
        img.thumbnail((250, 250))
        img_tk = ImageTk.PhotoImage(img)
        self.image_label.configure(image=img_tk)
        self.image_label.image = img_tk  # giữ ảnh trong bộ nhớ


class us_upload_file_to_google_driver(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.grid(row=0,column=0,sticky='nswe')
        
        tk.Label(self,text='Tải file lên google drive',bg='green',fg='white',font=("Arial", 12)).grid(row=0,column=0,sticky='nswe',pady=10,columnspan=2)
        
        self.btn_upload= tk.Button(self, text="📁 Chọn file course", command=self.upload_file, font=("Arial", 12))
        self.btn_upload.grid(row=1,column=0,sticky='ns',pady=5)
        
        self.status1=tk.Label(self,text='status',font=("Arial", 12))
        self.status1.grid(row=1,column=1,sticky='w',pady=5)
        
        self.btn_upload_img=tk.Button(self,text="📁 Chọn folder img",command=self.upload_img,font=("Arial", 12))
        self.btn_upload_img.grid(row=2,column=0,sticky='ns',pady=5)
        
        self.status2=tk.Label(self,text='status',font=("Arial", 12))
        self.status2.grid(row=2,column=1,sticky='w',pady=5)
        
    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path.endswith('.json'):
            try:
                id= upload_file_course(file_path,'course_update.json')
                if id!='':
                    self.status1.config(text='✓')
            except Exception as err:
                messagebox.showerror('Lỗi upload file',f'err')
                self.status1.config(text='✗')
        else:
            messagebox.showinfo("Lỗi đường dẫn file",'file chọn bắt buộc kiểu json')
            self.status1.config(text='✗')
    
    def upload_img(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            try:
                id=upload_img(folder_path,'img.zip')
                if id!='':
                    self.status2.config(text='✓')
            except Exception as err:
                messagebox.showerror('Lỗi upload img',f'err')
                self.status2.config(text='✗')
        else:
            messagebox.showinfo("Lỗi đường dẫn folder",'Chưa chọn folder')
            self.status2.config(text='✗')
                     
#############Khai báo hàm#########################################################################################
# Thêm hàm này vào khu vực khai báo hàm trong app.py
"""Quét lại thư mục data, cập nhật COURSE_FILE_MAP và làm mới Combobox."""
def refresh_course_list(course_combobox_widget, course_variable_obj):
    """Quét lại thư mục data, cập nhật COURSE_FILE_MAP và làm mới Combobox."""
    global COURSE_FILE_MAP
    
    COURSE_FILE_MAP.clear()
    data_folder_path = PATH_DATA
    course_files = glob.glob(os.path.join(data_folder_path, 'course_*.json'))
    
    for file_path in course_files:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                temp_course_data = json.load(file)
                course_name = temp_course_data.get("course_name")
                if course_name:
                    COURSE_FILE_MAP[course_name] = file_path
        except Exception as e:
            print(f"Lỗi khi quét lại file course {file_path}: {e}")
            
    available_courses = list(COURSE_FILE_MAP.keys())
    course_combobox_widget['values'] = available_courses
    
    # Tùy chọn: chọn môn học đầu tiên nếu có
    if available_courses:
        course_variable_obj.set(available_courses[0])
        # Trigger event để tải dữ liệu môn học đầu tiên
        course_combobox_widget.event_generate("<<ComboboxSelected>>")

# Tạo hàm xử lý sự kiện handle_import_docx
#Hàm này sẽ được gọi khi bạn nhấn vào nút menu. 
# Nó sẽ mở hộp thoại chọn file và gọi hàm process_docx_to_json.
"""Mở hộp thoại file, xử lý import từ DOCX và làm mới danh sách."""
def handle_import_docx(course_combobox_widget, course_variable_obj):
    """Mở hộp thoại file, xử lý import từ DOCX và làm mới danh sách."""
    file_path = filedialog.askopenfilename(
        title="Chọn file Word để import",
        filetypes=(("Word Documents", "*.docx"), ("All files", "*.*"))
    )
    
    if not file_path:
        # Người dùng đã hủy
        return
        
    # PATH_DATA là biến toàn cục đã được định nghĩa trong app.py
    success, message = process_docx_to_json(file_path, PATH_DATA)
    
    if success:
        messagebox.showinfo("Thành công", f"Đã import thành công và lưu tại:\n{message}")
        # Làm mới lại danh sách môn học trên giao diện
        refresh_course_list(course_combobox_widget, course_variable_obj)
    else:
        messagebox.showerror("Lỗi Import", f"Không thể import file:\n{message}")
            
def is_connected():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.ConnectionError as err:
        return False
    

def save_last_working_key(key):
    """Lưu API key hoạt động gần nhất vào file config.json."""
    try:
        config = {}
        if os.path.exists(PATH_JSON_CONFIG):
            with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as f:
                config = json.load(f)
        
        # Đảm bảo các khóa cần thiết tồn tại
        if 'api' not in config: config['api'] = [{}, {}]
        if len(config['api']) < 1: config['api'].append({})
        
        config['api'][0]['last_working_key'] = key
        
        with open(PATH_JSON_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"DEBUG: Đã lưu key đang hoạt động: ...{key[-4:]}")
    except Exception as e:
        print(f"Lỗi khi lưu last_working_key: {e}")

def find_working_api_key(keys_to_check):
    """
    Kiểm tra danh sách các API key và trả về key đầu tiên hoạt động.
    """
    print("DEBUG: Bắt đầu tìm kiếm API key đang hoạt động...")
    for key in keys_to_check:
        try:
            genai.configure(api_key=key)
            # Thử tạo một model đơn giản để xác thực key
            test_model = genai.GenerativeModel('gemini-1.5-flash')
            # Nếu không có lỗi, key này hoạt động
            print(f"DEBUG: Tìm thấy key hoạt động: ...{key[-4:]}")
            save_last_working_key(key) # Lưu lại key này cho lần sau
            return key
        except Exception as e:
            print(f"DEBUG: Key ...{key[-4:]} không hoạt động. Lỗi: {e}")
            continue # Thử key tiếp theo
    
    print("CẢNH BÁO: Không tìm thấy API key nào hoạt động trong danh sách.")
    return None # Trả về None nếu không có key nào hoạt động

def load_app_data():
    """
    Tải cấu hình, tìm API key hoạt động và ưu tiên key đã lưu.
    """
    global API_KEY_LIST, API_KEY, MODEL, main_rule, APP_VERSION
    
    API_KEY_LIST_DEFAULT = [
        "AIzaSyDvCMr_GJMvGxFynOvLedw04rqJ6_iElF0", "AIzaSyAF5-pKkd-y_EJYRoOQbYgw7fAmNWtvsq4",
        "AIzaSyAxVA26qSbc3Hvg6Hdqti4HvxtU0wN1sqo", "AIzaSyDrCxX9U0zNXPVkU2SE9wpGeN0sSYwNJ2I",
        "AIzaSyAK4nsb74n2I51jt3sH9bqpuHMRlJntV6Q", "AIzaSyAeB3zypsW9cgqENXPt1QfwkSBL7Bm2BAM",
        "AIzaSyD5j90VdXoQCRiVWD0bMzhpSXiOIcWx_Mg", "AIzaSyAhl5OP4FG7m048BHjjiKhZSC4pFrMBpVo",
        "AIzaSyDy5z-BHwmPL8ItNJJ6IdNaWjw-l2bNR4E", "AIzaSyAi2miv5ixUjrMTrFehhPH62Efo6wMIMMA",
        "AIzaSyBEpoVLETjcehxmd7faIkU7lablGAm7k9k", "AIzaSyBP39bWjuKeCDYqzLlY1FBueSQH2wtGfDg",
        "AIzaSyBrLVKtuwIs11WjYVS-1VyYICpkxpcRLys", "AIzaSyAT7ghjymT6klV-uN_8zqaGapnxnHJO7FI",
        "AIzaSyDhUZ9TOsGH5oIj4xHVg7wTootfe0eJCjY", "AIzaSyAg85SyVh8bwmoAHD5ClMYPSZDYcUKZge8",
        "AIzaSyBgXlzFpaQJbAaj-_6DYeE4m-Q-fYq21GM", "AIzaSyDLBPmqFncpruW52U5jQvWsLbkeMsf6c0g",
        "AIzaSyB64OSSTmfiaAKokNhYIeG1xHAv1Vq4jEw", "AIzaSyB2rtw9IJH8U_T064-Egx-iq0l16vq9Bj0",
        "AIzaSyCcQ0B0xrMTrxfo_4FVvgVX059dHHu0WKA", "AIzaSyCMdYZUu20OuhGvg4GlkF9Tg1E-aCWuXgw",
        "AIzaSyDkI2K-mytvzdWm7isbcSATa0sELEtzuRU", "AIzaSyB0tadJbKusAxTbYQBkvTqulK2UkMU82sQ",
        "AIzaSyALNGPa7ub-cvNTBNz1oKKjU631yKHP3Hw", "AIzaSyApCym0pQaZFHKVZIABBrZdxpKV-mzCuZg",
        "AIzaSyBqmgmNPF76Ex5u7S0IWIP-tZyMVv_Bcxk", "AIzaSyBrx2NP9XH2wkimt9XItNe6g9lbIDg8A2c",
        "AIzaSyCZiYQ9rofcm3ndFDIPcpEXk3y0b2LbKLA", "AIzaSyCss_cuhhDcA2ScTtTJ9VttU7Zq35e3MOE",
        "AIzaSyBQM1j6IMi08CfToV96aS96XFCpcKUYyPE"
    ]

    config_keys = []
    last_working_key = None
    try:
        with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as file:
            config = json.load(file)
        config_keys = config.get('api', [{}])[0].get('gemini_key', [])
        last_working_key = config.get('api', [{}])[0].get('last_working_key')
        MODEL = config.get('api', [{}, {}])[1].get('model', 'gemini-1.5-flash')
        APP_VERSION = config.get('system', [{}, {}])[1].get('version', '1.0')
    except Exception as e:
        print(f"Lỗi khi tải config.json: {e}. Sử dụng giá trị mặc định.")
        MODEL = 'gemini-1.5-flash'
        APP_VERSION = '1.0'

    combined_keys = API_KEY_LIST_DEFAULT + [key for key in config_keys if key not in API_KEY_LIST_DEFAULT]
    API_KEY_LIST = combined_keys
    
    # Tạo danh sách ưu tiên để kiểm tra
    keys_to_check = []
    if last_working_key and last_working_key in API_KEY_LIST:
        keys_to_check.append(last_working_key)
    # Thêm các key còn lại sau khi đã xáo trộn để tăng tính ngẫu nhiên
    other_keys = [key for key in API_KEY_LIST if key != last_working_key]
    random.shuffle(other_keys)
    keys_to_check.extend(other_keys)

    # Tìm key hoạt động và gán cho API_KEY
    API_KEY = find_working_api_key(keys_to_check)
    
    if not API_KEY:
        messagebox.showerror("Lỗi API Key", "Không có API Key nào hoạt động. Vui lòng kiểm tra lại danh sách key.")
        API_KEY = "" # Gán rỗng để tránh lỗi

    # Tải RULE
    try:
        with open(PATH_JSON_RULE, "r", encoding="utf-8") as file:
            main_rule = file.read()
    except Exception as e:
        print(f"Lỗi tải rule.md: {e}")
        main_rule = ''
        
        
def load_all_course_data(course_combobox_widget):
    """Quét thư mục data, tải thông tin các môn học và cập nhật Combobox."""
    global COURSE_FILE_MAP, json_course, CURRENT_EXERCISE_LANGUAGE

    COURSE_FILE_MAP.clear()
    course_files = glob.glob(os.path.join(PATH_DATA, 'course_*.json'))

    if not course_files:
        messagebox.showerror("Lỗi", "Không tìm thấy file khóa học (*.json) nào trong thư mục data/.")
        return

    for file_path in course_files:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                temp_course_data = json.load(file)
                course_name = temp_course_data.get("course_name")
                if course_name:
                    COURSE_FILE_MAP[course_name] = file_path
        except Exception as e:
            print(f"Lỗi khi đọc file course JSON {file_path}: {e}")

    # Cập nhật giá trị cho Combobox
    available_course_names = list(COURSE_FILE_MAP.keys())
    course_combobox_widget['values'] = available_course_names
    
    # Tự động chọn môn học mặc định để hiển thị
    if available_course_names:
        default_selection = "Kỹ thuật lập trình (C)"
        if default_selection in available_course_names:
            course_combobox_widget.set(default_selection)
        else:
            course_combobox_widget.set(available_course_names[0])
        # Tự động trigger sự kiện để tải dữ liệu của môn học đầu tiên vào Treeview
        course_combobox_widget.event_generate("<<ComboboxSelected>>")
                                
def update_course_from_course_update(path_course_update):
    global json_course # json_course hiện tại đang chứa dữ liệu của môn học đang hiển thị
    
    if os.path.exists(path_course_update):
        with open(path_course_update, "r", encoding="utf-8") as file:
            try:
                json_course_update = json.load(file)
            except Exception as e: # Catch specific exception
                print(f"Lỗi tải course_update.json: {e}")
                json_course_update = None
                
        if json_course_update is not None:
            # Xác định file JSON của môn học hiện tại để cập nhật
            # Giả sử json_course (global) chứa dữ liệu của môn học đang hiển thị
            # và nó có trường 'course_name' để tìm đường dẫn file.
            
            current_course_name = json_course.get("course_name") if json_course else None
            
            if current_course_name and current_course_name in COURSE_FILE_MAP:
                # Lấy đường dẫn file JSON của môn học hiện tại
                path_to_save_current_course = COURSE_FILE_MAP[current_course_name]
                
                # Cập nhật trạng thái và điểm của các bài tập trong json_course_update
                # dựa trên trạng thái hiện tại của json_course
                if json_course is not None:
                    update_map = {}
                    for session in json_course.get('sessions', []):
                        for ex in session.get('exercises', []):
                            update_map[ex['id']] = {
                                'status': ex.get('status', '✗'), # Use .get()
                                'score': ex.get('score', 0)     # Use .get()
                            }

                    # Cập nhật lại vào json_course_update
                    for session in json_course_update.get('sessions', []):
                        for ex in session.get('exercises', []):
                            ex_id = ex['id']
                            if ex_id in update_map:
                                ex['status'] = update_map[ex_id]['status']
                                ex['score'] = update_map[ex_id]['score']
                
                # Ghi dữ liệu đã cập nhật vào file JSON TƯƠNG ỨNG của môn học đang hoạt động
                try:
                    with open(path_to_save_current_course, 'w', encoding='utf-8') as f:
                        json.dump(json_course_update, f, indent=2, ensure_ascii=False)
                    print(f"Đã cập nhật file: {path_to_save_current_course}")
                    delete_file(path_course_update) # Xóa file update sau khi cập nhật
                except Exception as e:
                    print(f"Lỗi khi ghi file cập nhật cho môn học: {e}")
                    messagebox.showerror("Lỗi ghi file", f"Không thể lưu cập nhật cho môn học: {e}")
            else:
                print("Cảnh báo: Không thể xác định file môn học hiện tại để cập nhật.")
                messagebox.showwarning("Cảnh báo", "Không thể lưu cập nhật: Môn học hiện tại không xác định.")
        else:
            print("Cảnh báo: course_update.json rỗng hoặc lỗi, không có gì để cập nhật.")
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu cập nhật từ course_update.json.")

def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
  
def update_exercise(json_data,id, new_status:ExerciseStatus, new_score=None):
    for session in json_data.get("sessions", []):
            for ex in session.get("exercises", []):
                if ex["id"] == id:
                    if new_status is not None:
                        ex["status"] = new_status.value
                    if new_score is not None:
                        ex["score"] = new_score
                    return True  # cập nhật thành công
    return False  # không tìm thấy
        
def update_json_course(id, new_status:ExerciseStatus, new_score=None):
    global json_course # json_course đang chứa dữ liệu của môn học hiện tại
    res=update_exercise(json_course,id, new_status,new_score)
    if res == True:
        # Xác định file JSON của môn học hiện tại để lưu
        current_course_name = json_course.get("course_name") if json_course else None
        if current_course_name and current_course_name in COURSE_FILE_MAP:
            path_to_save = COURSE_FILE_MAP[current_course_name]
            save_json_file(path_to_save, json_course) # Lưu vào file cụ thể của môn học
            print(f"Đã lưu cập nhật cho bài tập {id} vào {path_to_save}")
        else:
            print("Cảnh báo: Không thể lưu cập nhật bài tập. Môn học hiện tại không xác định hoặc không có đường dẫn file.")
            # Fallback: nếu không tìm được, có thể lưu vào course.json mặc định hoặc hiển thị lỗi
            save_json_file(PATH_JSON_COURSE, json_course) # Vẫn lưu vào default nếu không tìm được map
    else:
        print('cập nhập lỗi bài tập trong bộ nhớ')
    
def update_model():
    global MODEL
    global API_KEY
    global model
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL)
               


def write_log(data):
    try:
        # SỬA LỖI: Dùng hàm chuẩn os.path.join thay cho get_path_join
        path_log = os.path.join(PATH_LOG, 'log.json')

        # Bước 1: Đọc dữ liệu cũ nếu file tồn tại
        if os.path.exists(path_log):
            with open(path_log, "r", encoding="utf-8") as f:
                try:
                    old_data = json.load(f)
                    if not isinstance(old_data, list):
                        old_data = []
                except json.JSONDecodeError:
                    old_data = []
        else:
            old_data = []

        # Bước 2: Append dữ liệu mới
        if isinstance(data, list):
            old_data.extend(data)
        else:
            old_data.append(data)

        # Bước 3: Ghi lại toàn bộ vào file
        with open(path_log, "w", encoding="utf-8") as f:
            json.dump(old_data, f, indent=4, ensure_ascii=False)
            
    except Exception as err:
       # Chuyển lỗi thành chuỗi để hiển thị rõ ràng hơn
       messagebox.showerror("Lỗi ghi log", str(err))

def create_file_log_name(name,mssv):
    timestamp = datetime.now().strftime("%y%m%d%H%M%S")
    # Chuyển tên thành không dấu và thay khoảng trắng bằng gạch dưới
    def convert_name(name):
        name_ascii = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
        return name_ascii.replace(" ", "_")
    name_formatted = convert_name(name)
    mssv=mssv.replace(" ","")
    # Ghép lại thành chuỗi
    result = f"{mssv}_{timestamp}__{name_formatted}.json"
    return result

def update_data_from_foler_download(path_course_update,path_img_zip):
    global PATH_IMG
    if path_course_update!='':
        update_course_from_course_update(path_course_update)
    if path_img_zip!='':
        extract_zip_overwrite(path_img_zip,PATH_IMG)
        delete_file(path_img_zip)
        
##################################################################################################################
def get_latest_cache():
    

    if getattr(sys, 'frozen', False):    
        course_files = get_path('../cache/cache_*.json')
    else:
        file_list = glob.glob(os.path.join(PATH_CATCH, "cache_*.json"))
        
        
    # Nếu có file thì tìm file mới nhất dựa trên tên
    if file_list:
        # Sắp xếp theo tên giảm dần (tên chứa timestamp)
        newest_file = sorted(file_list, reverse=True)[0]
        return newest_file
    else:
        print("Không tìm thấy file cache nào.")
        return None
    
def load_latest_cache():
    global history
    path_cache=get_latest_cache()
    if path_cache is not None:
        with open(path_cache, "r") as f:
            data = json.load(f)
            if data:
                history.clear()
                history=data
                return True
    return False

def continue_conversation(output,fr_info):
    global queue
    if load_latest_cache():
        prompt=continue_conversation_rule
        if prompt:
           call_gemini_api_thread(prompt,queue,output,fr_info)
    else:
        messagebox.showwarning('Cảnh báo','cache rỗng cần nạp lại bài tập')
           
def get_api_response(prompt):
    global model
    global history
    log=[]
    message = [{'role': 'user', 'parts': [prompt]}]
    
    timestamp = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    message_ = [{'timestamp':f'{timestamp}','role': 'user', 'parts': [prompt]}]
    
    log.append(message_)
    
    history.extend(message)  # Thêm message vào lịch sử
    
    response = model.generate_content(history)
    
    timestamp = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    message_ = [{'timestamp':f'{timestamp}','role': 'model', 'parts': [response.text]}]
    
    log.append(message_)
    
    history.append({'role': 'model', 'parts': [response.text]})                                  
    return response.text,log
        
def call_gemini_api_thread(prompt, queue, output=None, fr_info=None,was_retry=False):
    
    if not is_connected():
        print('Rớt mạng')
        messagebox.showerror("Lỗi mạng","Lỗi rớt mạng - Vui lòng kiểm tra mạng")
        return
    
    def worker():
        global API_KEY
        global API_KEY_LIST
        tried_keys = set()
        global model
        log=[]
        if API_KEY!='' and model!='':
            while True:
                try:
                    response,log=get_api_response(prompt)
                    break
                except Exception as err:
                    print(f"Lỗi với API_KEY {API_KEY}: {err}")
                    tried_keys.add(API_KEY)
                    available_keys = [key for key in API_KEY_LIST if key not in tried_keys]
                    if not available_keys:
                        print("Tất cả API_KEY đã thử và đều gặp lỗi.")
                        return
                    API_KEY = random.choice(available_keys)
                    print(f"Thử lại với API_KEY mới: {API_KEY}")
                    update_model()
                    
            queue.put((response, output, fr_info, log,was_retry))

    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()        
        
def mardown_json_to_dict(mardown_json):
    try:
        lines = mardown_json.strip().splitlines()
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines[-1].startswith('```'):
            lines = lines[:-1]
        cleaned_json = '\n'.join(lines)
        data_dict = json.loads(cleaned_json)
        return data_dict
    except:
        return None
   
def markdown_preserve_code_blocks(text):
    print('---markdown gốc---')
    print(text)
    return None

def escape_code_block_content(code: str) -> str:
    """Escape nội dung block code cho JSON."""
    return code.replace('\\', '\\\\') \
               .replace('"', '\\"') \
               .replace('\n', '\\n')

def extract_and_replace_c_blocks(text):
    blocks = []
    def replacer(match):
        blocks.append(match.group(0))
        return f"__CODE_{len(blocks)-1}__"
    new_text = re.sub(r'```c\s.*?```', replacer, text, flags=re.DOTALL)
    return new_text, blocks

def normalize_code_block_indent(block: str) -> str:
    """
    Nhận vào block code kiểu Markdown (```c ... ```) và chuẩn hóa:
    - Dấu ``` đóng phải nằm riêng trên dòng
    - Nội dung code không thụt dòng
    """
    lines = block.strip().split('\n')

    if len(lines) < 2 or not lines[0].startswith('```c'):
        return block  # Không phải block code hợp lệ

    opening = lines[0].strip()
    closing = lines[-1].strip()

    # Nếu dòng cuối không đúng là ``` thì cố gắng tìm trong dòng cuối hoặc loại bỏ thụt dòng
    if closing != '```':
        # Trường hợp ``` nằm chung dòng cuối cùng (ví dụ: '   ```')
        if lines[-1].strip().endswith('```'):
            # Cắt dấu ``` ra riêng
            content_line = lines[-1].rstrip().removesuffix('```').rstrip()
            if content_line:
                code_lines = [line.lstrip() for line in lines[1:-1]] + [content_line]
            else:
                code_lines = [line.lstrip() for line in lines[1:-1]]
        else:
            # Không phát hiện được ``` -> giữ nguyên
            return block
    else:
        code_lines = [line.lstrip() for line in lines[1:-1]]

    # Gộp lại block chuẩn
    return '\n'.join([opening] + code_lines + ['```'])

def resume_block_code(new_text,code_blocks):
    new_code_block=[]
    for block in code_blocks:
        cleaned = normalize_code_block_indent(block)
        new_code_block.append(cleaned)
        
    for i, block in enumerate(new_code_block):
        #print(block)
        new_text = new_text.replace(f"__CODE_{i}__",f"\n{block}\n")
    return new_text

def process_markdown_escape_smart(md_text):
    # Tách block code ```...``` ra
    code_blocks = re.findall(r'```.*?```', md_text, flags=re.DOTALL)
    placeholders = []
    temp_text = md_text

    for i, block in enumerate(code_blocks):
        placeholder = f"@@CODEBLOCK{i}@@"
        placeholders.append((placeholder, block))
        temp_text = temp_text.replace(block, placeholder)

    # Tách inline code `...`
    inline_codes = re.findall(r'`[^`\n]+`', temp_text)
    inline_placeholders = []

    for i, block in enumerate(inline_codes):
        placeholder = f"@@INLINE{i}@@"
        inline_placeholders.append((placeholder, block))
        temp_text = temp_text.replace(block, placeholder)

    print('-----')
    print(temp_text)
    
    return temp_text

def render_ai_json_markdown(response_text: str) -> str:
     
    print(response_text)
    match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, flags=re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = response_text.strip()

    try:
        obj = json.loads(json_str)
        markdown_text = obj["data"]
        new_text, code_blocks = extract_and_replace_c_blocks(markdown_text)
        new_text=re.sub(r'(?<!\n)\n(?!\n)', '  \n', new_text)
        new_text=resume_block_code(new_text,code_blocks)        
        html = markdown.markdown(new_text, extensions=["fenced_code", "sane_lists"])
        return html,obj['info'],None
    except Exception as err:
        print('***************Lỗi phản hồi json*******************')
        return '',{},err
    
#####################################################################################################################

def update_response_callback(info):
    global ID_EXERCISE, json_course # Thêm json_course vào global

    # --- LOGIC MỚI: CHỈ CẬP NHẬT KHI ĐANG LÀM BÀI CÓ TRONG MÔN HỌC ---
    # Bỏ qua việc cập nhật nếu là Bài tập tự do (ID_EXERCISE là 'custom_exercise')
    # hoặc không có môn học nào đang được tải (json_course is None)
    if ID_EXERCISE is None or ID_EXERCISE == 'custom_exercise' or json_course is None:
        print("DEBUG: Bỏ qua cập nhật tiến trình cho Bài tập tự do.")
        return # Dừng hàm tại đây

    # Nếu không phải bài tập tự do, tiếp tục logic cập nhật như cũ
    print('---cập nhập json_course---')
    print(info)
    status_text = info.get('exercise_status', 'in_progress')
    
    if status_text == 'completed':
        status = ExerciseStatus.COMPLETED
    else:
        status = ExerciseStatus.INCOMPLETE

    score = info.get('score') # Lấy điểm trực tiếp từ info
    
    # Logic trừ điểm có thể không cần thiết nếu AI đã xử lý
    # if status == ExerciseStatus.INCOMPLETE and score is not None:
    #     score = score - 10 # Cân nhắc lại logic này nếu AI đã tự trừ điểm
    
    print(f"DEBUG: Cập nhật bài tập ID {ID_EXERCISE} với trạng thái '{status.value}' và điểm {score}")
    update_json_course(ID_EXERCISE, status, score)
                
def update_response(window,queue):
    global re_response_prompt
    global MAX_RETRY
    try:
        while True:
            response, output, fr_info, log, was_retry= queue.get_nowait()
            html_content,info,err=render_ai_json_markdown(response)
            
            if html_content == '' and info == {}:
                print(err)
                if not was_retry:
                    print("⚠️ Phản hồi lỗi → gọi lại API 1 lần duy nhất")
                    call_gemini_api_thread(re_response_prompt, queue, output, fr_info, was_retry=True)
                else:
                    print("❌ Phản hồi tiếp tục lỗi sau khi đã retry → bỏ qua")
                continue  # luôn bỏ qua kết quả lỗi
            
            if html_content!='':
                if output is not None:
                    html_content_=f"<div style='font-size:12px; font-family:Verdana'>{html_content}</div>"
                    output.set_html(html_content_)
                
            if fr_info is not None:
                lbl_level=fr_info['level']
                lbl_socre=fr_info['score']
                lbl_level.config(text=info.get('level', '-'))
                lbl_socre.config(text=info.get('score', '-'))       
                           
            if info:
                update_response_callback(info)
            
            for msg in log:
                write_log(msg)
            
    except Empty:
        pass
    window.after(100, update_response,window,queue)
            
##cập nhập log             
def wait_queue_log(queue,output):
    try:
        result = queue.get_nowait()
        output.insert(tk.END, result+"\n")  # Chèn nội dung vào cuối
    except Empty:
        output.after(100, wait_queue_log, queue, output)
        
def print_log(text,output):
    global queue_log
    queue_log.put(text)
    wait_queue_log(queue_log,output)


def btn_send_click(args):
    """
    Hàm được gọi khi nhấn nút "Chấm bài & Đánh giá".
    Tự động xác định ngữ cảnh và ngôn ngữ dựa trên tab đang hoạt động.
    """
    global main_rule, json_course, ID_EXERCISE, CURRENT_COURSE_NAME, CURRENT_COURSE_LANGUAGE

    input_widget = args['input_widget']
    custom_input_widget = args['custom_input']
    notebook = args['notebook']
    queue = args['queue']
    output = args['output']
    fr_info = args['fr_info']
    
    user_code = input_widget.get("1.0", tk.END).strip()
    if not user_code:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập bài làm trước khi gửi.")
        return
        
    full_prompt = ""
    course_name_to_use = CURRENT_COURSE_NAME
    language_to_use = CURRENT_COURSE_LANGUAGE
    
    active_tab_text = notebook.tab(notebook.select(), "text")

    if active_tab_text == 'Bài tập Tự do':
        exercise_description = custom_input_widget.get("1.0", tk.END).strip()
        if not exercise_description:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đề bài ở tab 'Bài tập Tự do' trước.")
            return
        
        # SỬA LỖI: Lấy ngôn ngữ từ biến toàn cục đã được cập nhật bởi Combobox
        language_to_use = CURRENT_EXERCISE_LANGUAGE
        course_name_to_use = "Bài tập tự do" # Gán lại tên môn học cho đúng ngữ cảnh
        
        full_prompt = f"# Đề bài\n{exercise_description}\n\n# Bài làm của người học:\n```_placeholder\n{user_code}\n```"
    
    elif active_tab_text == 'Bài tập theo Môn học' and json_course and ID_EXERCISE:
        current_exercise_data = None
        session_idx, exercise_idx = -1, -1
        for i, session in enumerate(json_course.get("sessions", [])):
            for j, ex in enumerate(session.get("exercises", [])):
                if ex.get("id") == ID_EXERCISE:
                    current_exercise_data, session_idx, exercise_idx = ex, i, j
                    break
            if current_exercise_data: break
        
        if current_exercise_data:
            exercise_context = json_sessions_to_markdown(json_course, session_idx, exercise_idx)
            full_prompt = f"{exercise_context}\n\n# Bài làm của người học:\n```_placeholder\n{user_code}\n```"
    
    if not full_prompt:
        messagebox.showerror("Lỗi", "Không thể xác định ngữ cảnh bài tập.")
        return

    final_prompt = create_main_rule(main_rule, full_prompt, course_name=course_name_to_use, course_language=language_to_use)
    call_gemini_api_thread(final_prompt, queue, output, fr_info)
        
    
def btn_clear_cache_click(args):
    input_widget = args['input_widget'] # Sửa lại key ở đây
    output = args['output']
    input_widget.delete("1.0", tk.END) 
    output.set_html("") # Dùng set_html("") cho HTMLLabel
    history.clear()
    # ...
    
def btn_load_rule_click(args):
    queue = args['queue']  # Lấy tham số queue từ args
    output = args['output']  # Lấy tham số label từ args
    history.clear()
    prompt=main_rule
    if prompt:
        call_gemini_api_thread(prompt,queue,output)
    print('load rule ok')

def btn_help_click(args):
    """
    Hàm được gọi khi nhấn nút "AI Giúp đỡ".
    Tự động xác định ngữ cảnh và ngôn ngữ dựa trên tab đang hoạt động.
    """
    global main_rule, json_course, ID_EXERCISE, CURRENT_COURSE_NAME, CURRENT_COURSE_LANGUAGE

    custom_input_widget = args['custom_input']
    notebook = args['notebook']
    queue = args['queue']
    output = args['output']
    fr_info = args['fr_info']

    full_prompt = ""
    course_name_to_use = CURRENT_COURSE_NAME
    language_to_use = CURRENT_COURSE_LANGUAGE
    
    active_tab_text = notebook.tab(notebook.select(), "text")
    
    if active_tab_text == 'Bài tập Tự do':
        exercise_description = custom_input_widget.get("1.0", tk.END).strip()
        if not exercise_description:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đề bài ở tab 'Bài tập Tự do' trước.")
            return

        # SỬA LỖI: Lấy ngôn ngữ từ biến toàn cục đã được cập nhật bởi Combobox
        language_to_use = CURRENT_EXERCISE_LANGUAGE
        course_name_to_use = "Bài tập tự do"

        full_prompt = f"# Đề bài\n{exercise_description}\n\n# Yêu cầu của người học:\nHướng dẫn tôi"
    
    elif active_tab_text == 'Bài tập theo Môn học' and json_course and ID_EXERCISE:
        current_exercise_data = None
        session_idx, exercise_idx = -1, -1
        for i, session in enumerate(json_course.get("sessions", [])):
            for j, ex in enumerate(session.get("exercises", [])):
                if ex.get("id") == ID_EXERCISE:
                    current_exercise_data, session_idx, exercise_idx = ex, i, j
                    break
            if current_exercise_data: break

        if current_exercise_data:
            exercise_context = json_sessions_to_markdown(json_course, session_idx, exercise_idx)
            full_prompt = f"{exercise_context}\n\n# Yêu cầu của người học:\nHướng dẫn tôi"
            
    if not full_prompt:
        messagebox.showerror("Lỗi", "Không thể xác định ngữ cảnh bài tập.")
        return

    final_prompt = create_main_rule(main_rule, full_prompt, course_name=course_name_to_use, course_language=language_to_use)
    call_gemini_api_thread(final_prompt, queue, output, fr_info)
    print('Yêu cầu trợ giúp đã được gửi đi.')

def window_on_closing(window):
    print('close window')
    global history
    global CACHE_STATUS
    if CACHE_STATUS==1:
        timestr = datetime.now().strftime("%y%m%d%H%M%S")
        path_catch=f'{PATH_CATCH}/cache_{timestr}.json'
        with open(path_catch, "w") as f:
            json.dump(history, f, indent=4)
    window.destroy()  # Bắt buộc gọi để thoát

def btn_run_code_click(args):
    # --- Định nghĩa thông tin các compiler ---
    COMPILER_MAP = {
        'c': {
            'dir': 'ucrt64',
            'url': 'https://drive.google.com/uc?id=1VfddlnK1Gh2iL8P-VkgrqeZ5PFqW614a'
        },
        'python': {
            'dir': 'python313',
            'url': 'https://drive.google.com/uc?id=11PtS_uVMd6nWaRIy0tNbV6l96nbUvchs'
        },
        'java': {
            'dir': 'jdk-23',
            'url': 'https://drive.google.com/uc?id=1cCo9OoPCP3QRmYn9ML6g8isHGS9GmLK0'
        }
    }
    
    # Lấy các widget cần thiết từ 'args'
    #code_input = args['input']
    code_input = args['input_widget']
    output_widget = args['output']
    main_window = args['window']
    code = code_input.get("1.0", tk.END).strip()
    
    if not code:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã để chạy.")
        return
    
    global CURRENT_EXERCISE_LANGUAGE
    lang = CURRENT_EXERCISE_LANGUAGE.lower()
    
    if lang not in COMPILER_MAP:
        messagebox.showerror("Lỗi Ngôn ngữ", f"Ngôn ngữ '{lang}' không được hỗ trợ để biên dịch.")
        return

    ### <<< BẮT ĐẦU KHỐI LOGIC MỚI ĐỂ KIỂM TRA COMPILER >>> ###
    required_dir = COMPILER_MAP[lang]['dir']
    compiler_path = os.path.join(PATH_COMPILER, required_dir)

    # 1. Kiểm tra nếu compiler cần thiết chưa tồn tại
    if not os.path.isdir(compiler_path):
        # Tìm tất cả các compiler đang thiếu
        missing = [name for name, data in COMPILER_MAP.items() if not os.path.isdir(os.path.join(PATH_COMPILER, data['dir']))]
        
        messagebox.showinfo("Yêu cầu Cài đặt", "Trình biên dịch cần thiết chưa được cài đặt. Vui lòng thực hiện cài đặt trong cửa sổ tiếp theo.")
        # Mở cửa sổ dialog để người dùng tải về
        #CompilerDownloadDialog(main_window, missing, COMPILER_MAP)
        CompilerDownloadDialog(main_window, COMPILER_MAP, missing)
        
        # Sau khi dialog đóng, kiểm tra lại một lần nữa
        if not os.path.isdir(compiler_path):
            messagebox.showerror("Chưa sẵn sàng", f"Vẫn chưa cài đặt compiler cho {lang.upper()}. Không thể chạy code. Vui lòng thử lại.")
            return
    ### <<< KẾT THÚC KHỐI LOGIC MỚI >>> ###

    # 2. Nếu compiler đã tồn tại (hoặc vừa cài xong), tiếp tục chạy code như cũ
    result = ""
    print(f"DEBUG: Attempting to run code for language: {CURRENT_EXERCISE_LANGUAGE}")

    if CURRENT_EXERCISE_LANGUAGE == "c":
        if 'compile_code' in globals(): 
            result = compile_code(code)
        else:
            result = "Error: C compiler function (compile_code) not found. Please check compiler_c.py import."
            messagebox.showerror("Lỗi", "Không tìm thấy trình biên dịch C.")
    elif CURRENT_EXERCISE_LANGUAGE == "java":
        if 'compile_java' in globals(): 
            result = compile_java(code)
        else:
            result = "Error: Java compiler function (compile_java) not found. Please ensure it's imported."
            messagebox.showerror("Lỗi", "Không tìm thấy trình biên dịch Java.")
    elif CURRENT_EXERCISE_LANGUAGE == "python":
        if 'run_python' in globals(): 
            result = run_python(code)
        else:
            result = "Error: Python runner function (run_python) not found. Please ensure it's imported."
            messagebox.showerror("Lỗi", "Không tìm thấy trình chạy Python.")
    else:
        result = f"Error: Ngôn ngữ '{CURRENT_EXERCISE_LANGUAGE}' không được hỗ trợ hoặc không xác định."
        messagebox.showerror("Lỗi", result)
        
    # Hiển thị kết quả ra widget output đã được truyền vào
    output_widget.set_html(f"<pre>{result}</pre>")
    
def tree_load(tree,json_course):
    for i, session in enumerate(json_course["sessions"]):
        session_id = tree.insert("", "end", text=session["title"], open=True)
        for j, ex in enumerate(session["exercises"]):
            tree.insert(session_id, "end", text=ex["title"],values=(ex['status'],ex['score'],i, j))

def reload_tree(tree, json_course):
    # ❌ Xóa hết các node cũ
    for item in tree.get_children():
        tree.delete(item)

    # ✅ Load lại dữ liệu
    tree_load(tree, json_course)

def btn_refesh_click(args):
    global json_course
    global main_rule
    global API_KEY
    global MODEL
    
    try:
        path_course=download_file_course_from_driver()
        path_img_zip=download_file_img_from_driver()
        update_data_from_foler_download(path_course,path_img_zip)
    except:
        messagebox.showerror('Error','Lỗi cập nhập bài tập từ google driver')
        
    
    with open(PATH_JSON_COURSE, "r", encoding="utf-8") as file:
        try:
            json_course = json.load(file)
            tree=args['tree']
            reload_tree(tree,json_course)
        except:
            json_course=None
            messagebox.showerror('Error','Lỗi load file course.json')
            return
    
    with open(PATH_JSON_RULE, "r", encoding="utf-8") as file:
        try:
            main_rule = file.read()
        except:
            main_rule=''
            messagebox.showerror('Error','Lỗi load file rule.md')
            return
        
    messagebox.showinfo('info','Làm mới OK')

def btn_refesh_offline_click(args):
    global json_course
    try:
        path_course=get_path_join(PATH_UPLOAD,"course_update.json")
        shutil.copy(path_course, PATH_DOWNLOAD)
        path_course_download=get_path_join(PATH_DOWNLOAD,"course_update.json")
        
        path_img_upload=get_path_join(PATH_UPLOAD,"img")
        shutil.copytree(path_img_upload,PATH_IMG, dirs_exist_ok=True)
        
        update_data_from_foler_download(path_course_download,'')
    except Exception as err:
        messagebox.showerror('Lỗi cập nhập file',err)
    
    with open(PATH_JSON_COURSE, "r", encoding="utf-8") as file:
        try:
            json_course = json.load(file)
            tree=args['tree']
            reload_tree(tree,json_course)
            messagebox.showinfo("OK","cập nhập course ok")
        except:
            json_course=None
            messagebox.showerror('Error','Lỗi load file course.json')
            return
    

def update_code_editor_language(code_editor_widget, language):
    """Cập nhật ngôn ngữ highlight cho CodeEditor."""
    if hasattr(code_editor_widget, 'configure_language'):
        code_editor_widget.configure_language(language)
    else:
        print(f"Cảnh báo: CodeEditor không hỗ trợ configure_language. Không thể thay đổi highlight cho: {language}")

# Sửa định nghĩa hàm on_course_select
def on_course_select(event, tree_widget, course_var_obj, input_widget=None, fr_lesson_tree_widget=None): # THÊM fr_lesson_tree_widget
    global json_course
    global CURRENT_COURSE_NAME
    global CURRENT_COURSE_LANGUAGE
    global CURRENT_EXERCISE_LANGUAGE
    
    selected_course_name = course_var_obj.get()
    print(f"Môn học được chọn: {selected_course_name}")

    # Đảm bảo hiển thị lại treeview nếu đang ở chế độ xem chi tiết bài tập
    if fr_lesson_tree_widget:
        # Lấy tất cả các widget con của fr_lesson_tree_widget
        for widget in fr_lesson_tree_widget.winfo_children():
            # Kiểm tra nếu widget con không phải là tree_widget (cây bài tập)
            # thì hủy bỏ nó (vì nó là frame_content chứa chi tiết bài học)
            if widget != tree_widget:
                widget.destroy()
        tree_widget.grid(row=0, column=0, sticky='nswe') # Đảm bảo tree_widget hiển thị

    for item in tree_widget.get_children():
        tree_widget.delete(item)

    if selected_course_name in COURSE_FILE_MAP:
        file_path_to_load = COURSE_FILE_MAP[selected_course_name]
        try:
            with open(file_path_to_load, "r", encoding="utf-8") as file:
                json_course_new = json.load(file)
            
            json_course = json_course_new # Update global json_course
            
            # Cập nhật thông tin môn học hiện tại
            CURRENT_COURSE_NAME = json_course.get("course_name", "Môn học không xác định")
            CURRENT_COURSE_LANGUAGE = json_course.get("course_language", "c").lower()
            CURRENT_EXERCISE_LANGUAGE = CURRENT_COURSE_LANGUAGE # Đồng bộ cho compiler

            print(f"DEBUG: Course language set to: {CURRENT_COURSE_LANGUAGE}")
            print(f"DEBUG: Course name set to: {CURRENT_COURSE_NAME}")

            if input_widget:
                update_code_editor_language(input_widget, CURRENT_EXERCISE_LANGUAGE)
            
            tree_load(tree_widget, json_course)
            print(f"DEBUG: Loaded course: {selected_course_name} from {file_path_to_load}")

        except FileNotFoundError:
            messagebox.showerror("Lỗi", f"Không tìm thấy file: {file_path_to_load}")
            print(f"ERROR: File not found: {file_path_to_load}")
            CURRENT_COURSE_NAME = "Môn học không xác định"
            CURRENT_COURSE_LANGUAGE = "c"
            CURRENT_EXERCISE_LANGUAGE = "c"
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu cho môn {selected_course_name}: {e}")
            print(f"ERROR: Failed to load course {selected_course_name}: {e}")
            CURRENT_COURSE_NAME = "Môn học không xác định"
            CURRENT_COURSE_LANGUAGE = "c"
            CURRENT_EXERCISE_LANGUAGE = "c"
    else:
        messagebox.showwarning("Cảnh báo", f"Không tìm thấy file dữ liệu cho môn: {selected_course_name}.")
        CURRENT_COURSE_NAME = "Môn học không xác định"
        CURRENT_COURSE_LANGUAGE = "c"
        CURRENT_EXERCISE_LANGUAGE = "c"
        

def display_exercise_details(exercise_data, session_index, exercise_index, args):
    """
    Hàm chung để hiển thị chi tiết một bài tập (thật hoặc ảo) lên giao diện.
    Đây là phiên bản tái cấu trúc từ hàm on_select cũ.
    """
    global history, main_rule, ID_EXERCISE, CURRENT_COURSE_NAME, CURRENT_COURSE_LANGUAGE

    # Lấy các widget và đối tượng cần thiết từ dictionary 'args'
    tree = args['tree']
    fr_lesson_tree = args['fr_tree']
    queue = args['queue']
    output = args['output']
    fr_info = args['fr_info']
    input_widget = args.get('input_widget')

    # Cập nhật ID bài tập hiện tại
    ID_EXERCISE = exercise_data['id']

    # Xóa nội dung cũ trong ô làm bài và ô AI output
    if input_widget:
        input_widget.delete("1.0", tk.END)
    output.set_html("") # Xóa nội dung AI output cũ

    # Ẩn Treeview và chuẩn bị hiển thị Frame chi tiết
    tree.grid_forget()
    frame_content = tk.Frame(fr_lesson_tree)
    frame_content.grid(row=0, column=0, sticky='nswe')
    frame_content.columnconfigure(0, weight=1)
    frame_content.rowconfigure(1, weight=1) # Row cho mô tả
    frame_content.rowconfigure(4, weight=1) # Row cho hướng dẫn

    # --- Bắt đầu xây dựng giao diện chi tiết ---
    tk.Label(frame_content, text=exercise_data["title"], font=("Arial", 12, "bold")).grid(row=0, column=0, sticky='nswe', pady=(0, 5))

    # Mô tả bài tập
    description_frame = tk.Frame(frame_content)
    description_frame.grid(row=1, column=0, sticky='nswe')
    description_frame.rowconfigure(0, weight=1)
    description_frame.columnconfigure(0, weight=1)
    txt_desc = tk.Text(description_frame, font=("Arial", 12), wrap='word', bg='#f0f0f0', relief="flat")
    txt_desc.grid(row=0, column=0, sticky='nswe')
    scrollbar_desc = ttk.Scrollbar(description_frame, orient='vertical', command=txt_desc.yview)
    scrollbar_desc.grid(row=0, column=1, sticky='ns')
    txt_desc.config(yscrollcommand=scrollbar_desc.set)
    txt_desc.insert(tk.END, exercise_data["description"])
    txt_desc.config(state=tk.DISABLED)

    # Nút hiển thị hình ảnh (nếu có)
    if exercise_data.get("image"):
        # 1. Tạo một frame riêng để chứa các nút hình ảnh
        fr_pic = tk.Frame(frame_content)
        fr_pic.grid(row=2, column=0, sticky='w', pady=(5,0)) # Đặt frame dưới mô tả

        # 2. Hàm để mở cửa sổ xem ảnh (giữ nguyên từ code cũ của bạn)
        def btn_img_click(img_path, img_title):
            img_window = tk.Toplevel(frame_content)
            img_window.title(img_title)
            img_window.transient(frame_content)
            img_window.grab_set()

            try:
                img_ = PILImage.open(img_path)
                tk_img = ImageTk.PhotoImage(img_)
                label_img = tk.Label(img_window, image=tk_img)
                label_img.image = tk_img
                label_img.pack()
            except Exception as e:
                tk.Label(img_window, text=f"Lỗi hiển thị ảnh:\n{e}").pack(padx=20, pady=20)

            img_window.wait_window()

        # 3. Vòng lặp để tạo các nút bấm cho mỗi ảnh
        for img_info in exercise_data.get("image", []):
            if img_info.get('link'):
                img_path = os.path.join(PATH_IMG, img_info['link'])
                img_title = img_info.get('image_title', 'Xem ảnh')

                # Sử dụng lambda với đối số mặc định để truyền đúng giá trị
                btn = tk.Button(fr_pic, text=f"🖼️ {img_title}", 
                                command=lambda p=img_path, t=img_title: btn_img_click(p, t))
                btn.pack(side=tk.LEFT, padx=2)

    # Hướng dẫn
    tk.Label(frame_content, text="Hướng dẫn:", font=("Arial", 12, "bold"), fg="white", bg="green").grid(row=3, column=0, sticky='nswe', pady=(5,0))
    guidance_frame = tk.Frame(frame_content)
    guidance_frame.grid(row=4, column=0, sticky='nswe')
    guidance_frame.rowconfigure(0, weight=1)
    guidance_frame.columnconfigure(0, weight=1)
    txt_guidance = tk.Text(guidance_frame, font=("Arial", 11), wrap='word', bg='#f0f0f0', relief="flat")
    txt_guidance.grid(row=0, column=0, sticky='nswe')
    scrollbar_guidance = ttk.Scrollbar(guidance_frame, orient='vertical', command=txt_guidance.yview)
    scrollbar_guidance.grid(row=0, column=1, sticky='ns')
    txt_guidance.config(yscrollcommand=scrollbar_guidance.set)
    if exercise_data.get("guidance"):
        full_guidance = "\n".join(exercise_data["guidance"])
        txt_guidance.insert(tk.END, full_guidance)
    else:
        txt_guidance.insert(tk.END, "Không có hướng dẫn cho bài tập này.")
    txt_guidance.config(state=tk.DISABLED)

    # --- Các hàm xử lý và nút bấm ---
    def back_to_tree():
        frame_content.destroy()
        reload_tree(tree, json_course)
        tree.grid(row=0, column=0, sticky='nswe')

    def help_from_AI():
        history.clear()
        prompt = ""
        # Nếu là bài tập tự do (index < 0), tạo prompt đơn giản
        if session_index < 0:
            prompt = create_main_rule(
                main_rule,
                f"# Đề bài\n{exercise_data['description']}",
                course_name="Bài tập tự do",
                course_language=CURRENT_COURSE_LANGUAGE
            )
        else: # Bài tập trong khóa học
            prompt = create_main_rule(
                main_rule,
                json_sessions_to_markdown(json_course, session_index, exercise_index),
                course_name=CURRENT_COURSE_NAME,
                course_language=CURRENT_COURSE_LANGUAGE
            )
        call_gemini_api_thread(prompt, queue, output, fr_info)

    fr_button = tk.Frame(frame_content)
    fr_button.grid(row=5, column=0, sticky='ew', pady=5)
    tk.Button(fr_button, text="⬅ Quay lại danh sách", font=("Arial", 11), command=back_to_tree).pack(side=tk.LEFT)

    # Tự động gọi AI để lấy hướng dẫn khi mở bài
    help_from_AI()


def start_custom_exercise(args):
    """Tạo và hiển thị một bài tập tự do từ input của người dùng."""
    custom_input_widget = args['custom_input']
    
    description = custom_input_widget.get("1.0", tk.END).strip()
    if not description:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đề bài trước khi bắt đầu.")
        return

    # Tạo một đối tượng "bài tập ảo"
    custom_exercise = {
        "id": "custom_exercise",
        "title": "Bài tập tự do: " + description.splitlines()[0],
        "description": description,
        "status": "✗", "score": 0, "image": [],
        "guidance": ["Đây là bài tập do bạn tự cung cấp. AI sẽ đưa ra hướng dẫn dựa trên đề bài."]
    }

    # Gọi hàm hiển thị chi tiết với index ảo (-1)
    display_exercise_details(custom_exercise, -1, -1, args)

# def on_select(event, args):
#     """
#     Hàm được gọi khi người dùng chọn một bài tập từ Treeview.
#     """
#     tree = args['tree']
#     selected_item = tree.focus()
def on_select(event, args):
    """
    Hàm được gọi khi người dùng chọn một bài tập từ Treeview.
    """
    # === THÊM ĐOẠN CODE KIỂM TRA NÀY VÀO ĐẦU HÀM ===
    if not IS_LOGGED_IN:
        messagebox.showinfo("Yêu cầu đăng nhập", "Vui lòng đăng nhập để truy cập các bài tập theo môn học.")
        # Giả sử bạn có hàm open_login_window như đã tạo ở Bước 1
        # Nếu không, bạn cần tạo nó để gọi cửa sổ đăng nhập
        # open_login_window() 
        return # Ngăn không cho hàm chạy tiếp
    # ===============================================

    tree = args['tree']
    selected_item = tree.focus()
    if not selected_item: return

    data = tree.item(selected_item)
    values = data.get("values")
    
    if values and len(values) >= 4:
        session_index = values[-2]
        exercise_index = values[-1]
        exercise = json_course["sessions"][session_index]["exercises"][exercise_index]
        
        # Gọi hàm hiển thị chung
        display_exercise_details(exercise, session_index, exercise_index, args)

        
def apply_treeview_style():
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 12))
    style.configure("Treeview.Heading", font=("Arial", 13, "bold"))  # Nếu dùng heading

def btn_create_img_description_click(args):
    global DICT_USER_INFO
    
    model=args['model']
    fr_parent=args['frame']
    new_window = tk.Toplevel(fr_parent)
    new_window.title('create image description')
    #new_window.geometry("500x400")  # Kích thước cửa sổ mới
    new_window.transient(fr_parent)  # Gắn cửa sổ mới vào cửa sổ chính
    new_window.grab_set()       # Vô hiệu hóa tương tác với cửa sổ chính

    new_window.rowconfigure(0,weight=1)
    new_window.columnconfigure(0,weight=1)
    
    us_gemini_image_description(new_window,model)
    
    def on_close():
        print('đóng cửa sổ')
        new_window.destroy()
    
    new_window.protocol("WM_DELETE_WINDOW", on_close)
    new_window.wait_window()

def btn_submit_exercise_click(args):
    global DICT_USER_INFO
    name_=DICT_USER_INFO[0]['username']
    mssv_=DICT_USER_INFO[0]['mssv']
    path_log_file=get_path_join(PATH_LOG,'log.json')
    if os.path.exists(path_log_file):
        file_log_name =create_file_log_name(name_,mssv_)
        try:
            upload_file_to_driver(path_log_file,file_log_name)
            messagebox.showinfo("Info",f'{file_log_name}  upload thành công')
        except Exception as err:
            messagebox.showinfo("Info",f'{file_log_name}  upload không thành công: {err}')
    else:
        messagebox.showinfo("Info",'Không tìm thấy file để upload')

def btn_upload_course_click(args):
    fr_parent=args['frame']
    new_window = tk.Toplevel(fr_parent)
    new_window.title('Upload course')
    new_window.geometry("500x200")  # Kích thước cửa sổ mới

    new_window.transient(fr_parent)  # Gắn cửa sổ mới vào cửa sổ chính
    new_window.grab_set()       # Vô hiệu hóa tương tác với cửa sổ chính

    new_window.rowconfigure(0,weight=1)
    new_window.columnconfigure(0,weight=1)

    us_upload_file_to_google_driver(new_window)

    def on_close():
        print('đóng cửa sổ')
        new_window.destroy()
    
    new_window.protocol("WM_DELETE_WINDOW", on_close)
    new_window.wait_window()

import webbrowser # Đảm bảo dòng này đã được thêm ở đầu file

def open_gemini_api_window(parent_window):
    """
    Mở cửa sổ quản lý API key.
    Hoạt động cho cả Khách (lưu vào file local) và Người dùng đã đăng nhập (lưu vào Firebase).
    """
    new_window = tk.Toplevel(parent_window)
    new_window.title("Quản lý Gemini API Keys")
    new_window.geometry("600x400")
    new_window.rowconfigure(3, weight=1)
    new_window.columnconfigure(0, weight=1)

    tk.Label(new_window, text="Quản lý Gemini API Keys", font=("Arial", 14, "bold"), fg="blue", pady=10).grid(row=0, column=0, columnspan=2, sticky='ew')
    tk.Button(new_window, text="Mở trang Get Gemini API", font=("Arial", 11), command=btn_get_gemini_api_click_external).grid(row=1, column=0, padx=10, pady=5, sticky='w')
    
    txt_gemini_api_keys = scrolledtext.ScrolledText(new_window, wrap="word", font=("Arial", 10), height=10)
    txt_gemini_api_keys.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='nswe')
    
    keys_to_display = []
    # === LOGIC KIỂM TRA MỚI ===
    if IS_LOGGED_IN:
        # --- Chế độ ĐÃ ĐĂNG NHẬP: Tải key từ Firebase ---
        tk.Label(new_window, text="Các Gemini API Key của tài khoản (mỗi key một dòng):", font=("Arial", 11)).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='w')
        try:
            current_user_uid = DICT_USER_INFO[0]['mssv']
            user_data = db.child("users").child(current_user_uid).get(token=CURRENT_USER_TOKEN)
            if user_data.val() and 'gemini_api_keys' in user_data.val():
                keys_to_display = user_data.val()['gemini_api_keys']
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải API keys từ Firebase: {e}")
    else:
        # --- Chế độ KHÁCH: Tải key từ biến toàn cục (đã đọc từ config.json) ---
        tk.Label(new_window, text="Các Gemini API Key đang dùng (lưu tại máy, mỗi key một dòng):", font=("Arial", 11)).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='w')
        keys_to_display = API_KEY_LIST

    if keys_to_display:
        txt_gemini_api_keys.insert(tk.END, "\n".join(keys_to_display))

    tk.Button(new_window, text="Lưu API Keys", font=("Arial", 11), command=lambda: btn_save_gemini_api_click(txt_gemini_api_keys, new_window)).grid(row=4, column=0, padx=10, pady=10, sticky='w')

    new_window.transient(parent_window)
    new_window.grab_set()
    parent_window.wait_window(new_window)
    
# Moved to app.py
def btn_get_gemini_api_click_external(): # Renamed from btn_get_gemini_api_click
    url = "https://ai.google.dev/gemini-api/docs"
    webbrowser.open_new_tab(url)
    
# Hàm này giữ nguyên như đã tạo ở câu trả lời trước
def btn_get_gemini_api_click():
    url = "https://ai.google.dev/gemini-api/docs"
    webbrowser.open_new_tab(url)

def btn_save_gemini_api_click(txt_widget, parent_window=None):
    """
    Lưu danh sách API key từ textbox vào Firebase cho người dùng đang đăng nhập.
    """
    global API_KEY_LIST, API_KEY, DICT_USER_INFO, db

    if not DICT_USER_INFO or not DICT_USER_INFO[0].get('mssv'):
        messagebox.showwarning("Cảnh báo", "Bạn chưa đăng nhập. Không thể lưu API Keys.")
        return
    
    current_user_uid = DICT_USER_INFO[0]['mssv']
    api_keys_text = txt_widget.get("1.0", tk.END).strip()
    new_api_keys = [line.strip() for line in api_keys_text.split('\n') if line.strip()]

    try:
        # **SỬA ĐỔI**: Thêm token vào lệnh update()
        db.child("users").child(current_user_uid).update({"gemini_api_keys": new_api_keys}, token=CURRENT_USER_TOKEN)

        # CẬP NHẬT TRẠNG THÁI ỨNG DỤNG LOCAL
        global API_KEY_LIST, API_KEY
        API_KEY_LIST = new_api_keys
        API_KEY = API_KEY_LIST[0] if API_KEY_LIST else ''
        update_model()

        messagebox.showinfo("Thành công", "Đã lưu API Keys lên tài khoản của bạn thành công!")
        if parent_window:
            parent_window.destroy()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu API Keys lên Firebase: {e}")

    
def update_user_info(username='', mssv='', password='', token=''):
    global DICT_USER_INFO, CURRENT_USER_TOKEN
    
    # Đảm bảo DICT_USER_INFO là một list có ít nhất một phần tử
    if not DICT_USER_INFO or not isinstance(DICT_USER_INFO, list):
        DICT_USER_INFO = [{}]
    
    # Cập nhật thông tin
    DICT_USER_INFO[0]['username'] = username
    DICT_USER_INFO[0]['mssv'] = mssv
    DICT_USER_INFO[0]['password'] = password
    
    # Lưu token vào biến toàn cục
    CURRENT_USER_TOKEN = token
    print(f"DEBUG: Đã cập nhật và lưu token người dùng.")
    
def export_log_to_json():
    """Mở hộp thoại 'Lưu file' và sao chép file log.json đến vị trí người dùng chọn."""
    global DICT_USER_INFO
    
    # Đường dẫn đến file log nguồn
    source_log_path = os.path.join(PATH_LOG, 'log.json')
    
    # 1. Kiểm tra xem file log có tồn tại không
    if not os.path.exists(source_log_path):
        messagebox.showwarning("Không tìm thấy log", "Không có dữ liệu log nào để export.")
        return
        
    # 2. Tạo tên file gợi ý dựa trên thông tin người dùng
    try:
        name_ = DICT_USER_INFO[0]['username']
        mssv_ = DICT_USER_INFO[0]['mssv']
        default_filename = create_file_log_name(name_, mssv_)
    except (IndexError, KeyError):
        # Nếu không có thông tin user, dùng tên mặc định
        default_filename = "tutor_ai_log.json"

    # 3. Mở hộp thoại "Save As"
    destination_path = filedialog.asksaveasfilename(
        initialfile=default_filename,
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Lưu file log học tập"
    )
    
    # 4. Nếu người dùng chọn một vị trí và nhấn Save
    if destination_path:
        try:
            # Sao chép file log đến đích
            shutil.copy(source_log_path, destination_path)
            messagebox.showinfo("Thành công", f"Đã export log thành công!\n\nĐường dẫn: {destination_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file log: {e}")    
    
def open_help_file():
    """Mở file Help.mhtml bằng trình duyệt mặc định."""
    try:
        # Xây dựng đường dẫn đầy đủ đến file help
        help_file_path = os.path.join(PATH_DATA, 'Help.mhtml')

        if os.path.exists(help_file_path):
            # Chuyển đổi đường dẫn file thành URI để trình duyệt mở chính xác
            uri = pathlib.Path(help_file_path).as_uri()
            webbrowser.open(uri)
        else:
            messagebox.showerror("Không tìm thấy file", f"Không tìm thấy file hướng dẫn tại:\n{help_file_path}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể mở file hướng dẫn: {e}")
       
def show_about_dialog(parent_window):
    about_window = Toplevel(parent_window)
    about_window.title("Giới thiệu Tutor AI")
    about_window.resizable(False, False)

    # Đường dẫn đến logo
    logo_path = os.path.join(PATH_IMG, 'LOGO_UDA.png')
    try:
        # --- BẮT ĐẦU THAY ĐỔI ---
        img = PILImage.open(logo_path)
        original_width, original_height = img.size

        # Lấy chiều rộng mục tiêu là 120px từ trang đăng nhập
        target_width = 120
        
        # Tính chiều cao mới để giữ đúng tỷ lệ ảnh
        target_height = int(target_width * original_height / original_width)
        
        # Thay đổi kích thước ảnh với chất lượng cao (LANCZOS)
        img_resized = img.resize((target_width, target_height), PILImage.Resampling.LANCZOS)
        
        logo_img = ImageTk.PhotoImage(img_resized)
        logo_label = Label(about_window, image=logo_img)
        logo_label.image = logo_img  # Giữ tham chiếu
        logo_label.pack(pady=10)
        # --- KẾT THÚC THAY ĐỔI ---

    except FileNotFoundError:
        Label(about_window, text="Không tìm thấy file logo 'LOGO_UDA.png'").pack(pady=10)
    except Exception as e:
        print(f"Lỗi hiển thị logo: {e}")
        Label(about_window, text=f"Lỗi hiển thị logo: {e}").pack(pady=10)

    about_text = """Giới thiệu sản phẩm Tutor AI
    Tên sản phẩm: Tutor AI
    Phiên bản: 1.0
    Đơn vị phát triển: Trường Đại học Đông Á

    Thông tin liên hệ
    Cơ sở Đà Nẵng:
    Địa chỉ: 33 Xô Viết Nghệ Tĩnh, P. Hòa Cường Nam, Q. Hải Châu, TP. Đà Nẵng
    SĐT: 0236.3519.929 - 0236.3519.991
    E-mail: vanthu@donga.edu.vn

    Cơ sở Đắk Lắk:
    Đơn vị: Hội đồng tuyển sinh Trường Đại học Đông Á Đắk Lắk
    Địa chỉ: Số 40 Phạm Hùng, P. Tân An, tỉnh Đắk Lắk
    Hotline: 0262.3518.989
    Email: tuyensinhdaklak@donga.edu.vn"""

    text_area = scrolledtext.ScrolledText(about_window, height=18, width=70, wrap='word', font=("Arial", 10))
    text_area.insert('1.0', about_text)
    text_area.config(state='disabled')
    text_area.pack(padx=10, pady=10)

    about_window.transient(parent_window)
    about_window.grab_set()
    parent_window.wait_window(about_window)

def on_custom_language_select(event, lang_variable):
    """
    Hàm được gọi khi người dùng chọn ngôn ngữ ở tab Bài tập Tự do.
    Cập nhật các biến global để đồng bộ với hệ thống prompt.
    """
    global CURRENT_COURSE_LANGUAGE, CURRENT_EXERCISE_LANGUAGE
    
    selected_lang = lang_variable.get()
    
    # Ánh xạ lựa chọn từ Combobox sang ngôn ngữ mà hệ thống hiểu
    lang_map = {
        "C": "c",
        "Java": "java",
        "Python": "python",
        "Không": "text"  # Dùng "text" cho trường hợp không chuyên biệt
    }
    
    lang_code = lang_map.get(selected_lang, "text")
    
    # Cập nhật các biến toàn cục
    CURRENT_COURSE_LANGUAGE = lang_code
    CURRENT_EXERCISE_LANGUAGE = lang_code
    
    print(f"DEBUG (Custom Tab): Language changed to: {lang_code}")

# def start_main_app(window):
#     """
#     Hàm này chứa toàn bộ logic dựng giao diện chính và gán sự kiện,
#     được gọi sau khi các dữ liệu nền đã được tải xong.
#     """
#     # Các biến global cần thiết
#     global json_course, model, history, queue, event_args, IS_LOGGED_IN, API_KEY_LIST, API_KEY, CURRENT_USER_TOKEN, DICT_USER_INFO
    
#     # ========== CÁC HÀM NỘI BỘ (giữ nguyên) ==========
#     def update_ui_for_login_status():
#         """Cập nhật toàn bộ giao diện dựa trên trạng thái đăng nhập (đã login hay là khách)."""
#         # Kích hoạt menu Gemini API cho mọi đối tượng
#         menubar.entryconfig("Gemini API", state="normal")
        
#         if IS_LOGGED_IN and DICT_USER_INFO:
#             username = DICT_USER_INFO[0].get('username', 'User')
#             login_logout_button.config(command=logout, text=f"👤 Xin chào, {username}!")
            
#             # Kích hoạt các tính năng cần đăng nhập
#             tool_menu.entryconfig("Nộp bài", state="normal")
#             file_menu.entryconfig("Export Log ra file JSON...", state="normal")
#         else:
#             login_logout_button.config(command=open_login_window, text="🚀 Đăng nhập / Đăng ký")
            
#             # Vô hiệu hóa các tính năng cần đăng nhập
#             tool_menu.entryconfig("Nộp bài", state="disabled")
#             file_menu.entryconfig("Export Log ra file JSON...", state="disabled")
    
#     def open_login_window():
#         """Mở cửa sổ đăng nhập và xử lý kết quả."""
#         global IS_LOGGED_IN, API_KEY_LIST, API_KEY
        
#         login_app = LoginApp(window, auth, db, update_user_info, update_api_key, PATH_JSON_CONFIG)
        
#         if login_app.result == 'ok':
#             IS_LOGGED_IN = True
            
#             try:
#                 current_user_uid = DICT_USER_INFO[0]['mssv']
#                 user_data = db.child("users").child(current_user_uid).get(token=CURRENT_USER_TOKEN)
                
#                 user_keys = user_data.val().get('gemini_api_keys') if user_data.val() else None

#                 if user_keys: # Ưu tiên key của người dùng nếu có
#                     print(f"DEBUG: Tìm thấy {len(user_keys)} API key cá nhân. Đang áp dụng...")
#                     API_KEY_LIST[:] = user_keys
#                     # Tìm key hoạt động trong danh sách của người dùng
#                     working_key = find_working_api_key(API_KEY_LIST)
#                     if working_key:
#                         API_KEY = working_key
#                     else:
#                         messagebox.showwarning("Cảnh báo API Key", "Không tìm thấy key nào hoạt động trong danh sách API cá nhân của bạn. Tạm thời sử dụng key mặc định.")
#                         # Nếu key cá nhân không hoạt động, quay lại dùng key mặc định
#                         load_app_data()
#                 else:
#                     # Nếu người dùng không có key, không cần làm gì cả, vì app đang dùng key mặc định rồi
#                     print("DEBUG: Người dùng chưa có API key cá nhân, tiếp tục dùng key mặc định.")

#             except Exception as e:
#                 print(f"Lỗi khi tải API key cá nhân: {e}")
#             finally:
#                 # Cập nhật lại model với API key mới nhất (của user hoặc mặc định)
#                 update_model()

#             # Tải danh sách môn học
#             load_all_course_data(course_combobox)
#         else:
#             IS_LOGGED_IN = False
        
#         update_ui_for_login_status()

#     def logout():
#         """Đăng xuất người dùng và reset về trạng thái khách."""
#         global IS_LOGGED_IN
#         if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất?"):
#             IS_LOGGED_IN = False
#             history.clear()
#             load_app_data()
#             update_model()
#             update_ui_for_login_status()

#     # ========== BẮT ĐẦU DỰNG GIAO DIỆN CHÍNH ==========
    
#     # --- Cấu hình layout chính của cửa sổ ---
#     # Row 0: Header (chứa Toolbar và nút Login)
#     # Row 1: PanedWindow (chứa 3 cột chính)
#     window.grid_rowconfigure(1, weight=1) 
#     window.grid_columnconfigure(0, weight=1) 

#     # --- KHUNG HEADER (Chứa cả Toolbar và Nút Đăng nhập) ---
#     fr_header = tk.Frame(window)
#     fr_header.grid(row=0, column=0, sticky='ew', padx=5, pady=(5,0))
    
#     toolbar = tk.Frame(fr_header)
#     toolbar.pack(side=tk.LEFT, padx=5, pady=2)

#     login_logout_button = tk.Button(fr_header, font=("Arial", 10, "bold"), fg="blue", relief="flat", justify="right")
#     login_logout_button.pack(side=tk.RIGHT, padx=10)

#     # --- MENU BAR (giữ nguyên) ---
#     menubar = tk.Menu(window)
#     window.config(menu=menubar)
#     # (code tạo menubar của bạn giữ nguyên...)
#     file_menu = tk.Menu(menubar, tearoff=0)
#     menubar.add_cascade(label="File", menu=file_menu)
#     file_menu.add_command(label="Export Log ra file JSON...", command=export_log_to_json)
#     file_menu.add_separator()
#     file_menu.add_command(label="Exit", command=lambda: window_on_closing(window))
#     tool_menu = tk.Menu(menubar, tearoff=0)
#     menubar.add_cascade(label="Function", menu=tool_menu)
#     menubar.add_command(label="Gemini API", command=lambda: open_gemini_api_window(window))
#     help_menu = tk.Menu(menubar, tearoff=0)
#     menubar.add_cascade(label="Trợ giúp", menu=help_menu)
#     help_menu.add_command(label="Hướng dẫn sử dụng", command=open_help_file)
#     help_menu.add_command(label="About", command=lambda: show_about_dialog(window))

#     # --- PANED WINDOW (chia 3 cột) ---
#     paned_window = ttk.PanedWindow(window, orient=tk.HORIZONTAL)
#     paned_window.grid(row=1, column=0, sticky='nswe', padx=5, pady=5) # Đặt vào row=1
    
#     fr_left = tk.Frame(paned_window) 
#     paned_window.add(fr_left, weight=1) 
#     fr_center = tk.Frame(paned_window) 
#     paned_window.add(fr_center, weight=2) 
#     fr_right = tk.Frame(paned_window) 
#     paned_window.add(fr_right, weight=1) 
    
#     def set_initial_sashes_after_zoom():
#         # (hàm này giữ nguyên)
#         window.update_idletasks() 
#         current_paned_width = paned_window.winfo_width()
#         min_width_left = 300
#         min_width_center = 500
#         min_width_right = 300 
#         total_desired_width = min_width_left + min_width_center + min_width_right
#         if current_paned_width >= total_desired_width: 
#             sash_pos_0 = min_width_left
#             sash_pos_1 = min_width_left + min_width_center
#         else:
#             sash_pos_0 = int(current_paned_width * (min_width_left / total_desired_width))
#             sash_pos_1 = int(current_paned_width * ((min_width_left + min_width_center) / total_desired_width))
#         paned_window.sashpos(0, sash_pos_0)
#         paned_window.sashpos(1, sash_pos_1)

#     # === DÁN LẠI TOÀN BỘ CODE DỰNG NỘI DUNG 3 CỘT VÀ TOOLBAR LOGIC VÀO ĐÂY ===

#     # --- LOGIC CỦA TOOLBAR ---
#     icon_size = (24, 24)
#     icons = {} 
#     def load_icon(name, path):
#         try:
#             full_path = os.path.join(PATH_IMG, path)
#             icons[name] = ImageTk.PhotoImage(Image.open(full_path).resize(icon_size))
#         except Exception as e:
#             print(f"Lỗi tải icon '{path}': {e}")
#             icons[name] = None
    
#     load_icon("import_word", "import.png")
#     load_icon("update_course", "upload.png")
#     load_icon("submit_exercise", "send.png")
#     load_icon("gemini_api", "settings.png")
#     load_icon("help", "help.png")
    
#     def create_toolbar_button(parent, icon_name, text_tooltip, command):
#         btn = tk.Button(parent, image=icons.get(icon_name), command=command, relief=tk.FLAT, width=30, height=30)
#         btn.pack(side=tk.LEFT, padx=1, pady=1)
#         Tooltip(btn, text_tooltip)
#         return btn

#     #     # ========== KHUNG BÊN TRÁI (fr_left) ==========
#     fr_left.rowconfigure(0, weight=1)
#     fr_left.columnconfigure(0, weight=1)
    
#     notebook_left = ttk.Notebook(fr_left)
#     notebook_left.grid(row=0, column=0, sticky='nswe', padx=2, pady=2)
    
#     # --- Tab 1: Bài tập Tự do ---
#     fr_tab_custom = tk.Frame(notebook_left)
#     notebook_left.add(fr_tab_custom, text='Bài tập Tự do')
#     fr_tab_custom.rowconfigure(2, weight=1) 
#     fr_tab_custom.columnconfigure(0, weight=1)

#     lang_frame = tk.Frame(fr_tab_custom)
#     lang_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(5,0))
#     tk.Label(lang_frame, text="Chọn ngôn ngữ (tùy chọn):", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 5))
#     lang_var = tk.StringVar()
#     lang_combobox = ttk.Combobox(lang_frame, textvariable=lang_var, values=["Không", "C", "Java", "Python"], state="readonly", width=15)
#     lang_combobox.pack(side=tk.LEFT)
#     lang_combobox.set("Không")
#     lang_combobox.bind("<<ComboboxSelected>>", lambda event: on_custom_language_select(event, lang_var))

#     tk.Label(fr_tab_custom, text="Nhập đề bài hoặc yêu cầu của bạn:", font=("Arial", 11)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
#     txt_custom_exercise = scrolledtext.ScrolledText(fr_tab_custom, wrap=tk.WORD, font=("Arial", 11), height=10)
#     txt_custom_exercise.grid(row=2, column=0, sticky='nswe', padx=5)
#     btn_start_custom_exercise = tk.Button(fr_tab_custom, text="Bắt đầu & Hướng dẫn", font=("Arial", 11, "bold"))
#     btn_start_custom_exercise.grid(row=3, column=0, pady=10)
    
#     # --- Tab 2: Bài tập theo Môn học ---
#     fr_tab_course = tk.Frame(notebook_left)
#     notebook_left.add(fr_tab_course, text='Bài tập theo Môn học')
#     fr_tab_course.rowconfigure(0, weight=1)
#     fr_tab_course.columnconfigure(0, weight=1)

#     fr_nav = tk.Frame(fr_tab_course)
#     fr_nav.grid(row=0, column=0, sticky='nswe')
#     fr_nav.rowconfigure(2, weight=1)
#     fr_nav.columnconfigure(0, weight=1)

#     tk.Label(fr_nav, text="Chọn môn học:", font=("Arial", 11)).grid(row=0, column=0, sticky='w', padx=5)
#     course_var = tk.StringVar()
#     # course_combobox = ttk.Combobox(fr_nav, textvariable=course_var, font=("Arial", 11), state="readonly")
#     # course_combobox.grid(row=1, column=0, sticky='ew', padx=5, pady=2) 
#     # available_course_names = list(COURSE_FILE_MAP.keys())
#     # course_combobox['values'] = available_course_names

#     course_combobox = ttk.Combobox(fr_nav, textvariable=course_var, font=("Arial", 11), state="readonly")
#     course_combobox.grid(row=1, column=0, sticky='ew', padx=5, pady=2) 
#     # Không cần gán 'values' ở đây nữa, hàm load_all_course_data sẽ làm việc này
#     # ...
    
#     fr_lesson_tree = tk.Frame(fr_nav)
#     fr_lesson_tree.grid(row=2, column=0, sticky='nswe') 
#     fr_lesson_tree.rowconfigure(0, weight=1)
#     fr_lesson_tree.columnconfigure(0, weight=1)

#     tree = ttk.Treeview(fr_lesson_tree, columns=("status", "score"), show="tree headings") 
#     tree.heading("#0", text="Buổi và tên bài", anchor='w')
#     tree.column("#0", minwidth=200) 
#     tree.heading("status", text="Trạng thái", anchor='center')
#     tree.column("status", width=80, stretch=False, anchor='center')
#     tree.heading("score", text="Điểm", anchor='center')
#     tree.column("score", width=60, stretch=False, anchor='center')
#     tree.grid(row=0, column=0, sticky='nswe')
            
#     # ========== KHUNG Ở GIỮA (fr_center) ==========
#     fr_center.rowconfigure(0, weight=1)
#     fr_center.columnconfigure(0, weight=1)
    
#     fr_input = tk.Frame(fr_center)
#     fr_input.grid(row=0, column=0, sticky="nswe")
#     fr_input.rowconfigure(1, weight=1)
#     fr_input.columnconfigure(0, weight=1)

#     tk.Label(fr_input, text='Bài làm', font=("Arial", 12, "bold"), fg="white", bg="green").grid(row=0, column=0, sticky="ew")
#     txt_input = CodeEditor(fr_input, font=("Consolas", 14), highlighter="monokai", wrap="word")
#     txt_input.grid(row=1, column=0, sticky='nswe', padx=5, pady=5)
#     txt_input.configure(background="white", foreground="black", insertbackground="black")
#     update_code_editor_language(txt_input, CURRENT_COURSE_LANGUAGE)
    
#     fr_input_btn = tk.Frame(fr_input)
#     fr_input_btn.grid(row=2, column=0, sticky='ew', pady=5)
#     fr_input_btn.columnconfigure([0,1,2], weight=1)
    
#     btn_run_code = tk.Button(fr_input_btn, text='▶ Chạy code', font=("Arial", 11))
#     btn_run_code.grid(row=0, column=0)
#     btn_send = tk.Button(fr_input_btn, text='💬 Chấm bài & Đánh giá', font=("Arial", 11))
#     btn_send.grid(row=0, column=1)
#     btn_help = tk.Button(fr_input_btn, text='💡 AI Giúp đỡ', font=("Arial", 11))
#     btn_help.grid(row=0, column=2)

#     # ========== KHUNG BÊN PHẢI (fr_right) ==========
#     fr_right.rowconfigure(0, weight=1)
#     fr_right.columnconfigure(0, weight=1)
    
#     fr_response = tk.Frame(fr_right)
#     fr_response.grid(row=0, column=0, sticky="nswe")
#     fr_response.rowconfigure(1, weight=1)
#     fr_response.columnconfigure(0, weight=1)
    
#     tk.Label(fr_response, text='AI phản hồi', font=("Arial", 12, "bold"), fg="white", bg="green").grid(row=0, column=0, sticky='ew')
#     txt_output = HTMLLabel(fr_response, background="white", wrap="word")
#     txt_output.grid(row=1, column=0, sticky='nswe', padx=5, pady=(0,5))
    
#     tk.Label(fr_response, text='Đánh giá', font=("Arial", 12, "bold"), fg="white", bg="green").grid(row=2, column=0, sticky='ew')
#     fr_info = tk.Frame(fr_response)
#     fr_info.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
#     fr_info.columnconfigure([0,1,2,3], weight=1)
    
#     tk.Label(fr_info, text='Level:', font=("Arial", 12)).grid(row=0, column=0, sticky='e')
#     lbl_level = tk.Label(fr_info, text='-', font=("Arial", 12, "bold"), fg="blue")
#     lbl_level.grid(row=0, column=1, sticky='w')
#     tk.Label(fr_info, text='Score:', font=("Arial", 12)).grid(row=0, column=2, sticky='e')
#     lbl_score = tk.Label(fr_info, text='-', font=("Arial", 12, "bold"), fg="red")
#     lbl_score.grid(row=0, column=3, sticky='w')   
    
#     # ========== LOGIC & SỰ KIỆN ==========
#     event_args = {
#         "window": window, "tree": tree, "fr_tree": fr_lesson_tree, 
#         "queue": queue, "output": txt_output, 
#         "fr_info": {'level': lbl_level, 'score': lbl_score}, 
#         "input_widget": txt_input, "custom_input": txt_custom_exercise,
#         "notebook": notebook_left # <<< THÊM DÒNG NÀY
#     }

#     def on_select_wrapper(event, args):
#         if not IS_LOGGED_IN:
#             open_login_window()
#             return
#         on_select(event, args)
    
#     btn_run_code.config(command=lambda: btn_run_code_click(event_args))
#     btn_send.config(command=lambda: btn_send_click(event_args))
#     btn_help.config(command=lambda: btn_help_click(event_args))
#     btn_start_custom_exercise.config(command=lambda: start_custom_exercise(event_args))

#     tree.bind("<<TreeviewSelect>>", lambda event: on_select_wrapper(event, event_args))
#     course_combobox.bind("<<ComboboxSelected>>", lambda event: on_course_select(event, tree, course_var, input_widget=txt_input, fr_lesson_tree_widget=fr_lesson_tree))

#     tool_menu.add_command(label="Import từ Word (.docx)", command=lambda: handle_import_docx(course_combobox, course_var))
#     tool_menu.add_command(label="Tạo giới thiệu ảnh", command=lambda: btn_create_img_description_click({'model': model, 'frame': fr_center}))
#     tool_menu.add_command(label="Cập nhật bài tập", command=lambda: btn_upload_course_click({'frame': fr_center}))
#     tool_menu.add_command(label="Nộp bài", command=lambda: btn_submit_exercise_click({'frame': fr_center}))
#     tool_menu.add_command(label="Xóa Cache", command=lambda: btn_clear_cache_click(event_args))
    
#     # --- KHỞI TẠO TRẠNG THÁI & HIỂN THỊ ---
#     window.protocol("WM_DELETE_WINDOW", lambda: window_on_closing(window))
#     window.deiconify()
#     window.state('zoomed')
    
#     window.after(200, set_initial_sashes_after_zoom)

#     update_model()
#     update_ui_for_login_status()
#     update_response(window, queue)

def start_main_app(window):
    """
    Hàm này chứa toàn bộ logic dựng giao diện chính và gán sự kiện,
    được gọi sau khi các dữ liệu nền đã được tải xong.
    """
    # Các biến global cần thiết
    global json_course, model, history, queue, IS_LOGGED_IN, API_KEY_LIST, API_KEY, CURRENT_USER_TOKEN, DICT_USER_INFO
    
    # ========== CÁC HÀM NỘI BỘ (giữ nguyên) ==========
    def update_ui_for_login_status():
        """Cập nhật toàn bộ giao diện dựa trên trạng thái đăng nhập (đã login hay là khách)."""
        # Kích hoạt menu Gemini API cho mọi đối tượng
        menubar.entryconfig("Gemini API", state="normal")
        
        if IS_LOGGED_IN and DICT_USER_INFO:
            username = DICT_USER_INFO[0].get('username', 'User')
            login_logout_button.config(command=logout, text=f"👤 Xin chào, {username}!")
            
            # Kích hoạt các tính năng cần đăng nhập
            tool_menu.entryconfig("Nộp bài", state="normal")
            file_menu.entryconfig("Export Log ra file JSON...", state="normal")
        else:
            login_logout_button.config(command=open_login_window, text="🚀 Đăng nhập / Đăng ký")
            
            # Vô hiệu hóa các tính năng cần đăng nhập
            tool_menu.entryconfig("Nộp bài", state="disabled")
            file_menu.entryconfig("Export Log ra file JSON...", state="disabled")
    
    def open_login_window():
        """Mở cửa sổ đăng nhập và xử lý kết quả."""
        global IS_LOGGED_IN, API_KEY_LIST, API_KEY
        
        login_app = LoginApp(window, auth, db, update_user_info, update_api_key, PATH_JSON_CONFIG)
        
        if login_app.result == 'ok':
            IS_LOGGED_IN = True
            
            try:
                current_user_uid = DICT_USER_INFO[0]['mssv']
                user_data = db.child("users").child(current_user_uid).get(token=CURRENT_USER_TOKEN)
                
                user_keys = user_data.val().get('gemini_api_keys') if user_data.val() else None

                if user_keys: # Ưu tiên key của người dùng nếu có
                    print(f"DEBUG: Tìm thấy {len(user_keys)} API key cá nhân. Đang áp dụng...")
                    API_KEY_LIST[:] = user_keys
                    # Tìm key hoạt động trong danh sách của người dùng
                    working_key = find_working_api_key(API_KEY_LIST)
                    if working_key:
                        API_KEY = working_key
                    else:
                        messagebox.showwarning("Cảnh báo API Key", "Không tìm thấy key nào hoạt động trong danh sách API cá nhân của bạn. Tạm thời sử dụng key mặc định.")
                        # Nếu key cá nhân không hoạt động, quay lại dùng key mặc định
                        load_app_data()
                else:
                    # Nếu người dùng không có key, không cần làm gì cả, vì app đang dùng key mặc định rồi
                    print("DEBUG: Người dùng chưa có API key cá nhân, tiếp tục dùng key mặc định.")

            except Exception as e:
                print(f"Lỗi khi tải API key cá nhân: {e}")
            finally:
                # Cập nhật lại model với API key mới nhất (của user hoặc mặc định)
                update_model()

            # Tải danh sách môn học
            load_all_course_data(course_combobox)
        else:
            IS_LOGGED_IN = False
        
        update_ui_for_login_status()

    def logout():
        """Đăng xuất người dùng và reset về trạng thái khách."""
        global IS_LOGGED_IN
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất?"):
            IS_LOGGED_IN = False
            history.clear()
            load_app_data()
            update_model()
            update_ui_for_login_status()

    # ========== BẮT ĐẦU DỰNG GIAO DIỆN CHÍNH ==========
    
    window.grid_rowconfigure(1, weight=1) 
    window.grid_columnconfigure(0, weight=1) 

    # --- KHUNG HEADER (Chứa cả Toolbar và Nút Đăng nhập) ---
    fr_header = tk.Frame(window)
    fr_header.grid(row=0, column=0, sticky='ew', padx=5, pady=(5,0))
    
    toolbar = tk.Frame(fr_header)
    toolbar.pack(side=tk.LEFT, padx=5, pady=2)

    login_logout_button = tk.Button(fr_header, font=("Arial", 10, "bold"), fg="blue", relief="flat", justify="right")
    login_logout_button.pack(side=tk.RIGHT, padx=10)

    # --- MENU BAR (giữ nguyên) ---
    menubar = tk.Menu(window)
    window.config(menu=menubar)
    # (code tạo menubar của bạn giữ nguyên...)
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Export Log ra file JSON...", command=export_log_to_json)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=lambda: window_on_closing(window))
    tool_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Function", menu=tool_menu)
    menubar.add_command(label="Gemini API", command=lambda: open_gemini_api_window(window))
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Trợ giúp", menu=help_menu)
    help_menu.add_command(label="Hướng dẫn sử dụng", command=open_help_file)
    help_menu.add_command(label="About", command=lambda: show_about_dialog(window))

    # --- LOGIC TẠO TOOLBAR ICON (SỬA LỖI GARBAGE COLLECTION) ---
    icon_size = (24, 24)
    # 1. Tạo một thuộc tính trên cửa sổ chính để lưu trữ an toàn các icon
    window.icons = {} 

    def load_icon(name, path):
        try:
            full_path = os.path.join(PATH_IMG, path)
            # 2. Lưu trực tiếp vào thuộc tính của cửa sổ
            window.icons[name] = ImageTk.PhotoImage(Image.open(full_path).resize(icon_size))
        except Exception as e:
            print(f"Lỗi tải icon '{path}': {e}")
            window.icons[name] = None
    
    # Tải tất cả các icon cần thiết
    load_icon("import_word", "import.png")
    load_icon("update_course", "upload.png")
    load_icon("submit_exercise", "send.png")
    load_icon("gemini_api", "settings.png")
    load_icon("help", "help.png")
    
    def create_toolbar_button(parent, icon_name, text_tooltip, command):
        # 3. Lấy icon từ thuộc tính của cửa sổ
        icon_image = window.icons.get(icon_name)
        
        btn = tk.Button(parent, image=icon_image, command=command, relief=tk.FLAT, width=30, height=30)
        btn.pack(side=tk.LEFT, padx=1, pady=1)
        
        # 4. Gán lại icon vào chính widget button - Đây là cách làm an toàn nhất
        btn.image = icon_image
        
        Tooltip(btn, text_tooltip)
        return btn

    # Tạo các nút trên toolbar (phần này giữ nguyên)
    create_toolbar_button(toolbar, "import_word", "Import bài tập từ Word (.docx)", lambda: handle_import_docx(course_combobox, course_var))
    create_toolbar_button(toolbar, "update_course", "Cập nhật bài tập từ Google Drive", lambda: btn_upload_course_click({'frame': fr_center}))
    create_toolbar_button(toolbar, "submit_exercise", "Nộp bài lên Google Drive", lambda: btn_submit_exercise_click({'frame': fr_center}))
    create_toolbar_button(toolbar, "gemini_api", "Quản lý Gemini API Keys", lambda: open_gemini_api_window(window))
    create_toolbar_button(toolbar, "help", "Hướng dẫn sử dụng", open_help_file)
    # =======================================================
    
    # --- PANED WINDOW (chia 3 cột) ---
    paned_window = ttk.PanedWindow(window, orient=tk.HORIZONTAL)
    paned_window.grid(row=1, column=0, sticky='nswe', padx=5, pady=5)
    
    fr_left = tk.Frame(paned_window) 
    paned_window.add(fr_left, weight=1) 
    fr_center = tk.Frame(paned_window) 
    paned_window.add(fr_center, weight=2) 
    fr_right = tk.Frame(paned_window) 
    paned_window.add(fr_right, weight=1) 
    
    def set_initial_sashes_after_zoom():
        # (hàm này giữ nguyên)
        window.update_idletasks() 
        current_paned_width = paned_window.winfo_width()
        min_width_left = 300
        min_width_center = 500
        min_width_right = 300 
        total_desired_width = min_width_left + min_width_center + min_width_right
        if current_paned_width >= total_desired_width: 
            sash_pos_0 = min_width_left
            sash_pos_1 = min_width_left + min_width_center
        else:
            sash_pos_0 = int(current_paned_width * (min_width_left / total_desired_width))
            sash_pos_1 = int(current_paned_width * ((min_width_left + min_width_center) / total_desired_width))
        paned_window.sashpos(0, sash_pos_0)
        paned_window.sashpos(1, sash_pos_1)
    
    # === TOÀN BỘ CODE DỰNG NỘI DUNG 3 CỘT VÀ GÁN SỰ KIỆN NẰM Ở ĐÂY ===
    #     #     # ========== KHUNG BÊN TRÁI (fr_left) ==========
    fr_left.rowconfigure(0, weight=1)
    fr_left.columnconfigure(0, weight=1)
    
    notebook_left = ttk.Notebook(fr_left)
    notebook_left.grid(row=0, column=0, sticky='nswe', padx=2, pady=2)
    
    # --- Tab 1: Bài tập Tự do ---
    fr_tab_custom = tk.Frame(notebook_left)
    notebook_left.add(fr_tab_custom, text='Bài tập Tự do')
    fr_tab_custom.rowconfigure(2, weight=1) 
    fr_tab_custom.columnconfigure(0, weight=1)

    lang_frame = tk.Frame(fr_tab_custom)
    lang_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(5,0))
    tk.Label(lang_frame, text="Chọn ngôn ngữ (tùy chọn):", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 5))
    lang_var = tk.StringVar()
    lang_combobox = ttk.Combobox(lang_frame, textvariable=lang_var, values=["Không", "C", "Java", "Python"], state="readonly", width=15)
    lang_combobox.pack(side=tk.LEFT)
    lang_combobox.set("Không")
    lang_combobox.bind("<<ComboboxSelected>>", lambda event: on_custom_language_select(event, lang_var))

    tk.Label(fr_tab_custom, text="Nhập đề bài hoặc yêu cầu của bạn:", font=("Arial", 11)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
    txt_custom_exercise = scrolledtext.ScrolledText(fr_tab_custom, wrap=tk.WORD, font=("Arial", 11), height=10)
    txt_custom_exercise.grid(row=2, column=0, sticky='nswe', padx=5)
    btn_start_custom_exercise = tk.Button(fr_tab_custom, text="Bắt đầu & Hướng dẫn", font=("Arial", 11, "bold"))
    btn_start_custom_exercise.grid(row=3, column=0, pady=10)
    
    # --- Tab 2: Bài tập theo Môn học ---
    fr_tab_course = tk.Frame(notebook_left)
    notebook_left.add(fr_tab_course, text='Bài tập theo Môn học')
    fr_tab_course.rowconfigure(0, weight=1)
    fr_tab_course.columnconfigure(0, weight=1)

    fr_nav = tk.Frame(fr_tab_course)
    fr_nav.grid(row=0, column=0, sticky='nswe')
    fr_nav.rowconfigure(2, weight=1)
    fr_nav.columnconfigure(0, weight=1)

    tk.Label(fr_nav, text="Chọn môn học:", font=("Arial", 11)).grid(row=0, column=0, sticky='w', padx=5)
    course_var = tk.StringVar()
    # course_combobox = ttk.Combobox(fr_nav, textvariable=course_var, font=("Arial", 11), state="readonly")
    # course_combobox.grid(row=1, column=0, sticky='ew', padx=5, pady=2) 
    # available_course_names = list(COURSE_FILE_MAP.keys())
    # course_combobox['values'] = available_course_names

    course_combobox = ttk.Combobox(fr_nav, textvariable=course_var, font=("Arial", 11), state="readonly")
    course_combobox.grid(row=1, column=0, sticky='ew', padx=5, pady=2) 
    # Không cần gán 'values' ở đây nữa, hàm load_all_course_data sẽ làm việc này
    # ...
    
    fr_lesson_tree = tk.Frame(fr_nav)
    fr_lesson_tree.grid(row=2, column=0, sticky='nswe') 
    fr_lesson_tree.rowconfigure(0, weight=1)
    fr_lesson_tree.columnconfigure(0, weight=1)

    tree = ttk.Treeview(fr_lesson_tree, columns=("status", "score"), show="tree headings") 
    tree.heading("#0", text="Buổi và tên bài", anchor='w')
    tree.column("#0", minwidth=200) 
    tree.heading("status", text="Trạng thái", anchor='center')
    tree.column("status", width=80, stretch=False, anchor='center')
    tree.heading("score", text="Điểm", anchor='center')
    tree.column("score", width=60, stretch=False, anchor='center')
    tree.grid(row=0, column=0, sticky='nswe')
            
    # ========== KHUNG Ở GIỮA (fr_center) ==========
    fr_center.rowconfigure(0, weight=1)
    fr_center.columnconfigure(0, weight=1)
    
    fr_input = tk.Frame(fr_center)
    fr_input.grid(row=0, column=0, sticky="nswe")
    fr_input.rowconfigure(1, weight=1)
    fr_input.columnconfigure(0, weight=1)

    tk.Label(fr_input, text='Bài làm', font=("Arial", 12, "bold"), fg="white", bg="green").grid(row=0, column=0, sticky="ew")
    txt_input = CodeEditor(fr_input, font=("Consolas", 14), highlighter="monokai", wrap="word")
    txt_input.grid(row=1, column=0, sticky='nswe', padx=5, pady=5)
    txt_input.configure(background="white", foreground="black", insertbackground="black")
    update_code_editor_language(txt_input, CURRENT_COURSE_LANGUAGE)
    
    fr_input_btn = tk.Frame(fr_input)
    fr_input_btn.grid(row=2, column=0, sticky='ew', pady=5)
    fr_input_btn.columnconfigure([0,1,2], weight=1)
    
    btn_run_code = tk.Button(fr_input_btn, text='▶ Chạy code', font=("Arial", 11))
    btn_run_code.grid(row=0, column=0)
    btn_send = tk.Button(fr_input_btn, text='💬 Chấm bài & Đánh giá', font=("Arial", 11))
    btn_send.grid(row=0, column=1)
    btn_help = tk.Button(fr_input_btn, text='💡 AI Giúp đỡ', font=("Arial", 11))
    btn_help.grid(row=0, column=2)

    # ========== KHUNG BÊN PHẢI (fr_right) ==========
    fr_right.rowconfigure(0, weight=1)
    fr_right.columnconfigure(0, weight=1)
    
    fr_response = tk.Frame(fr_right)
    fr_response.grid(row=0, column=0, sticky="nswe")
    fr_response.rowconfigure(1, weight=1)
    fr_response.columnconfigure(0, weight=1)
    
    tk.Label(fr_response, text='AI phản hồi', font=("Arial", 12, "bold"), fg="white", bg="green").grid(row=0, column=0, sticky='ew')
    txt_output = HTMLLabel(fr_response, background="white", wrap="word")
    txt_output.grid(row=1, column=0, sticky='nswe', padx=5, pady=(0,5))
    
    tk.Label(fr_response, text='Đánh giá', font=("Arial", 12, "bold"), fg="white", bg="green").grid(row=2, column=0, sticky='ew')
    fr_info = tk.Frame(fr_response)
    fr_info.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
    fr_info.columnconfigure([0,1,2,3], weight=1)
    
    tk.Label(fr_info, text='Level:', font=("Arial", 12)).grid(row=0, column=0, sticky='e')
    lbl_level = tk.Label(fr_info, text='-', font=("Arial", 12, "bold"), fg="blue")
    lbl_level.grid(row=0, column=1, sticky='w')
    tk.Label(fr_info, text='Score:', font=("Arial", 12)).grid(row=0, column=2, sticky='e')
    lbl_score = tk.Label(fr_info, text='-', font=("Arial", 12, "bold"), fg="red")
    lbl_score.grid(row=0, column=3, sticky='w')   
    
    # ========== LOGIC & SỰ KIỆN ==========
    event_args = {
        "window": window, "tree": tree, "fr_tree": fr_lesson_tree, 
        "queue": queue, "output": txt_output, 
        "fr_info": {'level': lbl_level, 'score': lbl_score}, 
        "input_widget": txt_input, "custom_input": txt_custom_exercise,
        "notebook": notebook_left # <<< THÊM DÒNG NÀY
    }

    def on_select_wrapper(event, args):
        if not IS_LOGGED_IN:
            open_login_window()
            return
        on_select(event, args)
    
    btn_run_code.config(command=lambda: btn_run_code_click(event_args))
    btn_send.config(command=lambda: btn_send_click(event_args))
    btn_help.config(command=lambda: btn_help_click(event_args))
    btn_start_custom_exercise.config(command=lambda: start_custom_exercise(event_args))

    tree.bind("<<TreeviewSelect>>", lambda event: on_select_wrapper(event, event_args))
    course_combobox.bind("<<ComboboxSelected>>", lambda event: on_course_select(event, tree, course_var, input_widget=txt_input, fr_lesson_tree_widget=fr_lesson_tree))

    tool_menu.add_command(label="Import từ Word (.docx)", command=lambda: handle_import_docx(course_combobox, course_var))
    tool_menu.add_command(label="Tạo giới thiệu ảnh", command=lambda: btn_create_img_description_click({'model': model, 'frame': fr_center}))
    tool_menu.add_command(label="Cập nhật bài tập", command=lambda: btn_upload_course_click({'frame': fr_center}))
    tool_menu.add_command(label="Nộp bài", command=lambda: btn_submit_exercise_click({'frame': fr_center}))
    tool_menu.add_command(label="Xóa Cache", command=lambda: btn_clear_cache_click(event_args))

    # --- KHỞI TẠO TRẠNG THÁI & HIỂN THỊ ---
    window.protocol("WM_DELETE_WINDOW", lambda: window_on_closing(window))
    window.deiconify()
    window.state('zoomed')
    
    window.after(200, set_initial_sashes_after_zoom)

    update_model()
    update_ui_for_login_status()
    update_response(window, queue)

def main():
    """Hàm khởi động chính của ứng dụng, chỉ hiển thị splash screen và tải dữ liệu."""
    root = tk.Tk()
    root.title("Tutor AI")
    root.withdraw() # Ẩn cửa sổ gốc

    # Hiển thị Splash Screen
    splash = SplashScreen(root)

    def load_heavy_data():
        """Hàm thực hiện các tác vụ nặng trong luồng chính (nhưng sau khi splash hiện)."""
        global firebase, auth, db
        print("Bắt đầu tải dữ liệu nền...")
        try:
            firebase = pyrebase.initialize_app(firebaseConfig)
            auth = firebase.auth()
            db = firebase.database()
            print("Khởi tạo Firebase thành công.")
        except Exception as e:
            print(f"Lỗi khởi tạo Firebase: {e}")
        
        load_app_data()
        print("Tải dữ liệu từ file hoàn tất.")
        
        root.after(0, on_loading_complete) # Lên lịch đóng splash và mở app

    def on_loading_complete():
        splash.destroy()
        start_main_app(root) # Bắt đầu dựng giao diện chính

    # Chạy hàm tải dữ liệu sau một khoảng trễ nhỏ để splash screen kịp hiển thị
    root.after(100, load_heavy_data)

    root.mainloop()
    
if __name__ == '__main__':
    main()