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

#for login
from login_gui import *

from datetime import datetime, timedelta

from google_driver_api import upload_file_to_driver,upload_file_course,download_file_course_from_driver,upload_img,extract_zip_overwrite,download_file_img_from_driver

##########Biến toàn cục #################################################################################
if getattr(sys, 'frozen', False):
    PATH_CATCH = get_path('../cache')
    PATH_LOG = get_path('../log')
    PATH_JSON_COURSE = get_path('../data/course.json')
    PATH_JSON_COURSE_UPDATE = get_path('../data/course_update.json')
    PATH_JSON_CONFIG = get_path('../data/config.json')
    PATH_JSON_RULE = get_path('../data/rule.md')
    PATH_IMG = get_path('../img')
    PATH_UPLOAD = get_path('../upload')
    PATH_STUDENT_LIST = get_path('../data/student.json')
    PATH_DOWNLOAD = get_path('../download')
else:
    PATH_CATCH = get_path('cache')
    PATH_LOG = get_path('log')
    PATH_JSON_COURSE = get_path('data/course.json')
    PATH_JSON_COURSE_UPDATE = get_path('data/course_update.json')
    PATH_JSON_CONFIG = get_path('data/config.json')
    PATH_JSON_RULE = get_path('data/rule.md')
    PATH_IMG = get_path('img')
    PATH_UPLOAD = get_path('upload')
    PATH_STUDENT_LIST = get_path('data/student.json')
    PATH_DOWNLOAD = get_path('download')

create_folder(PATH_CATCH)
create_folder(PATH_LOG)
create_folder(PATH_DOWNLOAD)
create_folder(PATH_UPLOAD)

APP_VERSION=''
CACHE_STATUS=0
STUDENT_LIST=[]
API_KEY_LIST=[]
API_KEY=''
ACCOUNT_ROLE=''
MODEL=NONE
DICT_USER_INFO=None
json_course=None
main_rule=''
model=None
history=[]
queue = Queue()
queue_log=Queue()
ID_EXERCISE=None
MAX_RETRY=2

###################################################################################################################
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

# class us_login(tk.Toplevel):
    
#         def __init__(self,parent, args, width=300,height=150):
#             super().__init__(parent)
#             self.title('Đăng nhập')
#             self.result='nok'
            
#             self.dict_user =args['dict_user']
#             self.student_list=args['student_list']
            
#             screen_width = self.winfo_screenwidth()
#             screen_height = self.winfo_screenheight()
#             # Tính vị trí giữa màn hình
#             x = (screen_width // 2) - (width // 2)
#             y = (screen_height // 2) - (height // 2)

#             # Đặt kích thước và vị trí cửa sổ
#             self.geometry(f"{width}x{height}+{x}+{y}")
      
#             #new_window.geometry()
#             self.transient(parent)  # Gắn cửa sổ mới vào cửa sổ chính
#             self.grab_set()       # Vô hiệu hóa tương tác với cửa sổ chính
            
#             self.columnconfigure(0,weight=1)
#             self.columnconfigure(1,weight=1)
#             self.rowconfigure(2,weight=1)
            
#             self.lbl_name=tk.Label(self,text='Đăng Nhập hệ thống',font=("Arial", 14),bg='green',fg='white')
#             self.lbl_name.grid(row=0,column=0,columnspan=2,sticky='nswe',pady=5)
            
#             self.lbl_mssv=tk.Label(self,text='ID sinh viên',font=("Arial", 12))
#             self.lbl_mssv.grid(row=1,column=0,sticky='ns')
            
#             self.txt_mssv=tk.Entry(self,font=("Arial", 12))
#             self.txt_mssv.grid(row=1,column=1,sticky='we',padx=5,pady=10)
            
#             if self.dict_user is not None:
#                 mssv=self.dict_user[0]['mssv']
#                 self.txt_mssv.delete(0, tk.END)
#                 self.txt_mssv.insert(0,mssv)
            
#             btn_submit=tk.Button(self,text='Đăng nhập',command=self.btn_submit_click,font=("Arial", 12))
#             btn_submit.grid(row=2,column=0,columnspan=2,sticky='n',pady=5)
                
#             self.protocol("WM_DELETE_WINDOW", self.on_close)
#             self.wait_window()
            
#         def on_close(self):
#             print('đóng cửa sổ')
#             self.result='nok'
#             self.destroy()
                    
#         def btn_submit_click(self):
#             mssv_=self.txt_mssv.get()
#             if mssv_=='':
#                 messagebox.showerror("Lỗi","Thông tin cần nhập đầy đủ")
#             else:
#                 print(mssv_)
#                 for student in self.student_list:
#                     if student['idsv']==mssv_:
#                         name_=student['name']
#                         id_=int(student['id'])
#                         self.dict_user[0]['mssv']=mssv_
#                         self.dict_user[0]['username']=name_
#                         update_user_info(name_,mssv_)
#                         update_api_key(id_)
#                         messagebox.showinfo('info',f'Đăng nhập thành công: Xin chào {name_}')
#                         self.result='ok'
#                         self.destroy()
#                         return
#                 messagebox.showerror('error',f'Đăng nhập không thành công')

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

def is_connected():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.ConnectionError as err:
        return False
    
def load_app_data():
    
    global STUDENT_LIST
    global API_KEY_LIST
    global API_KEY
    global MODEL
    global DICT_USER_INFO
    global json_course
    global main_rule
    global CACHE_STATUS
    global APP_VERSION
   
    with open(PATH_STUDENT_LIST, "r", encoding="utf-8") as file:
        try:
            STUDENT_LIST=json.load(file)
        except:
            STUDENT_LIST=[]

    with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as file:
        try:
            config=json.load(file)
            if not config['api'][0]['gemini_key']:
                API_KEY_LIST= [
                                    "AIzaSyDvCMr_GJMvGxFynOvLedw04rqJ6_iElF0",
                                    "AIzaSyAF5-pKkd-y_EJYRoOQbYgw7fAmNWtvsq4",
                                    "AIzaSyAxVA26qSbc3Hvg6Hdqti4HvxtU0wN1sqo",
                                    "AIzaSyDrCxX9U0zNXPVkU2SE9wpGeN0sSYwNJ2I",
                                    "AIzaSyAK4nsb74n2I51jt3sH9bqpuHMRlJntV6Q",
                                    "AIzaSyAeB3zypsW9cgqENXPt1QfwkSBL7Bm2BAM",
                                    "AIzaSyD5j90VdXoQCRiVWD0bMzhpSXiOIcWx_Mg",
                                    "AIzaSyAhl5OP4FG7m048BHjjiKhZSC4pFrMBpVo",
                                    "AIzaSyDy5z-BHwmPL8ItNJJ6IdNaWjw-l2bNR4E",
                                    "AIzaSyAi2miv5ixUjrMTrFehhPH62Efo6wMIMMA",
                                    "AIzaSyBEpoVLETjcehxmd7faIkU7lablGAm7k9k",
                                    "AIzaSyBP39bWjuKeCDYqzLlY1FBueSQH2wtGfDg",
                                    "AIzaSyBrLVKtuwIs11WjYVS-1VyYICpkxpcRLys",
                                    "AIzaSyAT7ghjymT6klV-uN_8zqaGapnxnHJO7FI",
                                    "AIzaSyDhUZ9TOsGH5oIj4xHVg7wTootfe0eJCjY",
                                    "AIzaSyAg85SyVh8bwmoAHD5ClMYPSZDYcUKZge8",
                                    "AIzaSyBgXlzFpaQJbAaj-_6DYeE4m-Q-fYq21GM",
                                    "AIzaSyDLBPmqFncpruW52U5jQvWsLbkeMsf6c0g",
                                    "AIzaSyB64OSSTmfiaAKokNhYIeG1xHAv1Vq4jEw",
                                    "AIzaSyB2rtw9IJH8U_T064-Egx-iq0l16vq9Bj0",
                                    "AIzaSyCcQ0B0xrMTrxfo_4FVvgVX059dHHu0WKA",
                                    "AIzaSyCMdYZUu20OuhGvg4GlkF9Tg1E-aCWuXgw",
                                    "AIzaSyDkI2K-mytvzdWm7isbcSATa0sELEtzuRU",
                                    "AIzaSyB0tadJbKusAxTbYQBkvTqulK2UkMU82sQ",
                                    "AIzaSyALNGPa7ub-cvNTBNz1oKKjU631yKHP3Hw",
                                    "AIzaSyApCym0pQaZFHKVZIABBrZdxpKV-mzCuZg",
                                    "AIzaSyBqmgmNPF76Ex5u7S0IWIP-tZyMVv_Bcxk",
                                    "AIzaSyBrx2NP9XH2wkimt9XItNe6g9lbIDg8A2c",
                                    "AIzaSyCZiYQ9rofcm3ndFDIPcpEXk3y0b2LbKLA",
                                    "AIzaSyCss_cuhhDcA2ScTtTJ9VttU7Zq35e3MOE",
                                    "AIzaSyBQM1j6IMi08CfToV96aS96XFCpcKUYyPE"                                    
                                ]
            else:
                API_KEY_LIST=config['api'][0]['gemini_key']
            
            API_KEY=API_KEY_LIST[0]
            MODEL=config['api'][1]['model']
            DICT_USER_INFO=config['user']
            CACHE_STATUS=config['system'][0]['cache_status']
            print(f'cache_status={CACHE_STATUS}')
            APP_VERSION=config['system'][1]['version']
            print(f'APP_VERSION={APP_VERSION}')
        except:
            API_KEY=''
            MODEL=''
            DICT_USER_INFO=None
    
    with open(PATH_JSON_COURSE, "r", encoding="utf-8") as file:
        try:
            json_course = json.load(file)
        except:
            json_course=None

    with open(PATH_JSON_RULE, "r", encoding="utf-8") as file:
        try:
            main_rule = file.read()
        except:
            main_rule=''

def update_course_from_course_update(path_course_update):
    global json_course
    if os.path.exists(path_course_update):
        with open(path_course_update, "r", encoding="utf-8") as file:
            try:
                json_course_update = json.load(file)
            except:
                json_course_update=None
                
        if json_course_update is not None:
            if json_course is not None:
                update_map = {}
                for session in json_course['sessions']:
                    for ex in session['exercises']:
                        update_map[ex['id']] = {
                            'status': ex['status'],
                            'score': ex['score']
                        }

                # Cập nhật lại vào course_update_data
                for session in json_course_update['sessions']:
                    for ex in session['exercises']:
                        ex_id = ex['id']
                        if ex_id in update_map:
                            ex['status'] = update_map[ex_id]['status']
                            ex['score'] = update_map[ex_id]['score']
                            
                with open(PATH_JSON_COURSE, 'w', encoding='utf-8') as f:
                    json.dump(json_course_update, f, indent=2, ensure_ascii=False)
                    delete_file(path_course_update)
            else:
                with open(PATH_JSON_COURSE, 'w', encoding='utf-8') as f:
                    json.dump(json_course_update, f, indent=2, ensure_ascii=False)
                    delete_file(path_course_update)
                            
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
    global json_course
    res=update_exercise(json_course,id, new_status,new_score)
    if res ==True:
        save_json_file(PATH_JSON_COURSE,json_course)
    else:
        print('cập nhập lỗi')
        
# def update_user_info(username='',mssv='',password=''):
#     global DICT_USER_INFO
#     print('-----')
#     print(username,mssv)
    
#     DICT_USER_INFO[0]['username']=username
#     DICT_USER_INFO[0]['mssv']=mssv
    
#     with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as file:
#         try:
#             config=json.load(file)
#             config['user'][0]['username']=username
#             config['user'][0]['mssv']=mssv
#             config['user'][0]['password']=password
#         except:
#             config=None
#     if config is not None:
#         save_json_file(PATH_JSON_CONFIG,config)
        
# def update_api_key(id_sv):
#     global API_KEY
#     global API_KEY_LIST
#     num_api_key=len(API_KEY_LIST)
#     index=id_sv%num_api_key
#     API_KEY=API_KEY_LIST[index]
#     print(f"idsv={id_sv} ; index={index} ; api_key={API_KEY}")
    
def update_model():
    global MODEL
    global API_KEY
    global model
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL)
               
def write_log(data):
    try:
        path_log = get_path_join(PATH_LOG,'log.json')
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
       messagebox.showerror("Lỗi ghi log",err)

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

    # Xử lý escape trong phần văn bản thường
    # def decode_unicode_escapes(m):
    #     try:
    #         return bytes(m.group(0), "utf-8").decode("unicode_escape")
    #     except:
    #         return m.group(0)

    # temp_text = temp_text.replace('\\\\', '\\')      # \\ -> \
    # temp_text = temp_text.replace('\\n', '\n')       # \n -> xuống dòng
    # temp_text = temp_text.replace('\\t', '\t')       # \t -> tab
    # # temp_text = re.sub(r'\\u[0-9a-fA-F]{4}', decode_unicode_escapes, temp_text)  # unicode

    # # Trả inline code và block code về vị trí
    # for placeholder, block in inline_placeholders:
    #     temp_text = temp_text.replace(placeholder, block)
    # for placeholder, block in placeholders:
    #     temp_text = temp_text.replace(placeholder, block)
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
    global ID_EXERCISE
    if ID_EXERCISE is not None:
        print('---cập nhập json_course---')
        print(info)
        status=info['exercise_status']
        if status=='completed':
            status=ExerciseStatus.COMPLETED
        else:
            status=ExerciseStatus.INCOMPLETE
        score=info['score']
        if status==ExerciseStatus.INCOMPLETE:
            score=score-10
        print(score)
        update_json_course(ID_EXERCISE,status,score)      
                
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
###
def btn_send_click(args):
    input=args['input']
    queue = args['queue']  # Lấy tham số queue từ args
    output = args['output']  # Lấy tham số label từ args
    prompt= input.get("1.0",tk.END).strip()
    if prompt:
        call_gemini_api_thread(prompt,queue,output)
        
def btn_clear_cache_click(args):
    input=args['input']
    output = args['output']         # Lấy tham số label từ args
    input.delete("1.0", tk.END) 
    output.delete("1.0", tk.END)    # Xóa từ dòng 1, cột 0 đến cuối
    history.clear()
    delete_all_files_in_folder(PATH_CATCH)
    messagebox.showinfo('info','Xóa Cache OK- Cần phải nạp lại bài tập')
    
def btn_load_rule_click(args):
    queue = args['queue']  # Lấy tham số queue từ args
    output = args['output']  # Lấy tham số label từ args
    history.clear()
    prompt=main_rule
    if prompt:
        call_gemini_api_thread(prompt,queue,output)
    print('load rule ok')

def btn_help_click(args):
    queue = args['queue']  # Lấy tham số queue từ args
    output = args['output']  # Lấy tham số label từ args
    fr_info=args['fr_info']
    prompt=help_promt
    if prompt:
        call_gemini_api_thread(prompt,queue,output,fr_info)
    
    print('load help ok')

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
    code_input=args['input']
    #output_display = args['output']         # Lấy tham số label từ args
    code = code_input.get("1.0", tk.END)
    if not code.strip():
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã C để chạy.")
        return
    #output_display.delete("1.0", tk.END)
    #compile_code(code)
    #for C
    #result=compile_code(code)
    
    #for java
    #result=compile_java(code)
    
    #for python
    result = run_python(code)
    
    #output_display.insert(tk.END,result)

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
    
# def on_select(event,args):
        
#     #{"tree":tree,"fr_tree":fr_lesson_tree,"queue":queue,"output":txt_output}
#     global json_course
#     global history 
#     global main_rule
#     global ID_EXERCISE   

#     tree=args['tree']
#     fr_lesson_tree=args['fr_tree']
#     queue=args['queue']
#     output=args['output']
#     fr_info=args['fr_info']
#     selected_item = tree.focus()
#     data = tree.item(selected_item)
#     values = data.get("values")
    
#     ID_EXERCISE=None
#     if values:
#         session_index=values[-2]
#         exercise_index = values[-1]
#         print(session_index,exercise_index)
#         exercise = json_course["sessions"][session_index]["exercises"][exercise_index]
#         ID_EXERCISE=exercise['id']
    
#         tree.grid_forget()

#         frame_content=tk.Frame(fr_lesson_tree)
#         frame_content.grid(row=0,column=0,sticky='nswe')
#         frame_content.columnconfigure(0,weight=1)
#         frame_content.rowconfigure(1,weight=1)
#         frame_content.rowconfigure(2,weight=1)
#         frame_content.rowconfigure(4,weight=1)
        
#         tk.Label(frame_content, text=exercise["title"],font=("Arial", 12)).grid(row=0,column=0,sticky='nswe')
#         txt=tk.Text(frame_content,font=("Arial", 12),height=10,width=40,wrap='word',bg='black',fg='white')
#         txt.grid(row=1,column=0,sticky='nswe')
#         txt.insert(tk.END, exercise["description"])
        
#         fr_pic=tk.Frame(frame_content,bg='gray')
#         fr_pic.grid(row=2,column=0,sticky='nswe')
        
#         #fr_pic.columnconfigure(0,weight=1)
#         fr_pic.rowconfigure(0,weight=0)
        
#         def btn_img_click(args):

#             new_window = tk.Toplevel(frame_content)
#             new_window.title(args['img_tittle'])
#             #new_window.geometry("500x400")  # Kích thước cửa sổ mới
#             new_window.transient(frame_content)  # Gắn cửa sổ mới vào cửa sổ chính
#             new_window.grab_set()       # Vô hiệu hóa tương tác với cửa sổ chính

#             new_window.rowconfigure(0,weight=1)
#             new_window.columnconfigure(0,weight=1)
            
#             tk_label_image=label_image(new_window,args['img_path'],args['img_tittle'])
#             tk_label_image.grid(row=0,column=0,sticky='nswe')
            
#             def on_close():
#                 print('đóng cửa sổ')
#                 new_window.destroy()
            
#             new_window.protocol("WM_DELETE_WINDOW", on_close)
#             new_window.wait_window()

        
#         btn_img=[]
#         for i,img in enumerate(exercise["image"]):
#             if(img['link']!=''):
#                 img_path_=  get_path_join(PATH_IMG,img['link'])
#                 img_title_= img['image_title']
#                 btn_img.append({'id':i,'img_tittle':img_title_,'img_path':img_path_ ,'btn':tk.Button(fr_pic,text=img_title_)})

#         for btn in btn_img:
#             id = btn['id']
#             btn['btn'].grid(row=0,column=id,sticky='w',padx='2')
#             btn['btn'].config(command=lambda: btn_img_click({'img_tittle':img_title_,'img_path':img_path_}))
            
            
#         tk.Label(frame_content, text="Hướng dẫn:",font=("Arial", 12), fg="white",bg="black").grid(row=3,column=0,sticky='nswe')
#         txt_guidance=tk.Text(frame_content,font=("Arial", 11),height=10,width=40,wrap='word')
#         txt_guidance.grid(row=4,column=0,sticky='nswe')
                
#         for g in exercise["guidance"]:
#             txt_guidance.insert(tk.END, "• " + g+"\n")
            
#         def back_to_tree():
#             frame_content.destroy()
#             tree.grid(row=0, column=0, sticky='nswe')
#             reload_tree(tree,json_course)
            
#         def help_from_AI(args):
#             lbl_note=args['label']
#             lbl_note.config(text="Đã upload bài tập lên AI", fg="blue")  # Thay đổi nội dung và màu chữ
#             history.clear()
#             print('clear cache ok')
#             print(f'sesion_index={session_index};exercise_index={exercise_index}')
#             prompt=create_main_rule(main_rule,json_sessions_to_markdown(json_course,session_index,exercise_index))
#             #print(prompt)
#             call_gemini_api_thread(prompt,queue,output,fr_info)
        
#         fr_button=tk.Frame(frame_content,bg='black')
#         fr_button.grid(row=5,column=0,sticky='nswe')
#         fr_button.columnconfigure(0,weight=1)
#         fr_button.columnconfigure(1,weight=1)
        
#         lbl_note=tk.Label(fr_button,text='Nhấn nút tải bài tập lên AI để bắt đầu bài mới',font=("Arial", 11),fg='red')
#         lbl_note.grid(row=1,column=0,columnspan=2,sticky='nswe')
        
#         tk.Button(fr_button, text="Quay lại",font=("Arial", 11), command=back_to_tree).grid(row=0, column=0, sticky='w', pady=10,padx=10)
#         tk.Button(fr_button, text="Tải bài tập lên AI",font=("Arial", 11), command=lambda:help_from_AI({'label':lbl_note})).grid(row=0, column=1, sticky='w', pady=10,padx=10)
       
def on_select(event,args):
        
    #{"tree":tree,"fr_tree":fr_lesson_tree,"queue":queue,"output":txt_output}
    global json_course
    global history 
    global main_rule
    global ID_EXERCISE   

    tree=args['tree']
    fr_lesson_tree=args['fr_tree']
    queue=args['queue']
    output=args['output']
    fr_info=args['fr_info']
    selected_item = tree.focus()
    data = tree.item(selected_item)
    values = data.get("values")
    
    ID_EXERCISE=None
    if values: # Kiểm tra xem đây có phải là một bài tập (leaf node) không
        session_index=values[-2]
        exercise_index = values[-1]
        print(session_index,exercise_index)
        exercise = json_course["sessions"][session_index]["exercises"][exercise_index]
        ID_EXERCISE=exercise['id']
    
        tree.grid_forget()

        frame_content=tk.Frame(fr_lesson_tree)
        frame_content.grid(row=0,column=0,sticky='nswe')
        frame_content.columnconfigure(0,weight=1)
        frame_content.rowconfigure(1,weight=1)
        frame_content.rowconfigure(2,weight=1)
        frame_content.rowconfigure(4,weight=1)
        
        tk.Label(frame_content, text=exercise["title"],font=("Arial", 12)).grid(row=0,column=0,sticky='nswe')
        txt=tk.Text(frame_content,font=("Arial", 12),height=10,width=40,wrap='word',bg='black',fg='white')
        txt.grid(row=1,column=0,sticky='nswe')
        txt.insert(tk.END, exercise["description"])
        
        fr_pic=tk.Frame(frame_content,bg='gray')
        fr_pic.grid(row=2,column=0,sticky='nswe')
        
        #fr_pic.columnconfigure(0,weight=1)
        fr_pic.rowconfigure(0,weight=0)
        
        def btn_img_click(args):

            new_window = tk.Toplevel(frame_content)
            new_window.title(args['img_tittle'])
            #new_window.geometry("500x400")  # Kích thước cửa sổ mới
            new_window.transient(frame_content)  # Gắn cửa sổ mới vào cửa sổ chính
            new_window.grab_set()       # Vô hiệu hóa tương tác với cửa sổ chính

            new_window.rowconfigure(0,weight=1)
            new_window.columnconfigure(0,weight=1)
            
            tk_label_image=label_image(new_window,args['img_path'],args['img_tittle'])
            tk_label_image.grid(row=0,column=0,sticky='nswe')
            
            def on_close():
                print('đóng cửa sổ')
                new_window.destroy()
            
            new_window.protocol("WM_DELETE_WINDOW", on_close)
            new_window.wait_window()

        
        btn_img=[]
        for i,img in enumerate(exercise["image"]):
            if(img['link']!=''):
                img_path_=  get_path_join(PATH_IMG,img['link'])
                img_title_= img['image_title']
                btn_img.append({'id':i,'img_tittle':img_title_,'img_path':img_path_ ,'btn':tk.Button(fr_pic,text=img_title_)})

        for btn in btn_img:
            id = btn['id']
            btn['btn'].grid(row=0,column=id,sticky='w',padx='2')
            btn['btn'].config(command=lambda: btn_img_click({'img_tittle':img_title_,'img_path':img_path_}))
            
            
        tk.Label(frame_content, text="Hướng dẫn:",font=("Arial", 12), fg="white",bg="black").grid(row=3,column=0,sticky='nswe')
        txt_guidance=tk.Text(frame_content,font=("Arial", 11),height=10,width=40,wrap='word')
        txt_guidance.grid(row=4,column=0,sticky='nswe')
                
        for g in exercise["guidance"]:
            txt_guidance.insert(tk.END, "• " + g+"\n")
            
        def back_to_tree():
            frame_content.destroy()
            tree.grid(row=0, column=0, sticky='nswe')
            reload_tree(tree,json_course)
            
        def help_from_AI(args):
            #lbl_note=args['label']
            #lbl_note.config(text="Đã upload bài tập lên AI", fg="blue")  # Thay đổi nội dung và màu chữ
            history.clear()
            print('clear cache ok')
            print(f'sesion_index={session_index};exercise_index={exercise_index}')
            prompt=create_main_rule(main_rule,json_sessions_to_markdown(json_course,session_index,exercise_index))
            #print(prompt)
            call_gemini_api_thread(prompt,queue,output,fr_info)
        
        fr_button=tk.Frame(frame_content,bg='black')
        fr_button.grid(row=5,column=0,sticky='nswe')
        fr_button.columnconfigure(0,weight=1)
        fr_button.columnconfigure(1,weight=1)
        
        #lbl_note=tk.Label(fr_button,text='Nhấn nút tải bài tập lên AI để bắt đầu bài mới',font=("Arial", 11),fg='red')
        lbl_note=tk.Label(fr_button,text='',font=("Arial", 11),fg='red')
        lbl_note.grid(row=1,column=0,columnspan=2,sticky='nswe')
        
        tk.Button(fr_button, text="Quay lại",font=("Arial", 11), command=back_to_tree).grid(row=0, column=0, sticky='w', pady=10,padx=10)
        
        # Lưu tham chiếu đến nút "Tải bài tập lên AI"
        #btn_load_exercise_to_ai = tk.Button(fr_button, text="Tải bài tập lên AI",font=("Arial", 11), command=lambda:help_from_AI({'label':lbl_note}))
        #btn_load_exercise_to_ai.grid(row=0, column=1, sticky='w', pady=10,padx=10)

        # *** THÊM DÒNG NÀY ĐỂ TỰ ĐỘNG NHẤN NÚT ***
        # Gọi command của nút ngay sau khi nó được tạo và cấu hình
        help_from_AI({'label':lbl_note}) # Gọi hàm tương ứng với nút
        
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

def main():
    global STUDENT_LIST, API_KEY_LIST, API_KEY, MODEL, DICT_USER_INFO, json_course, main_rule, model, history, queue, queue_log, APP_VERSION, ACCOUNT_ROLE, ID_EXERCISE
    
    load_app_data()
    print(DICT_USER_INFO)
    
    ##################################GUI###############################################################
    window = tk.Tk()
    window.title('app')
    # Đặt minsize của cửa sổ chính đủ lớn để chứa bố cục ban đầu
    window.minsize(1200, 700) 
    
    #yêu cầu đăng nhập (bỏ comment nếu muốn sử dụng login)
    # login = us_login(window, {'dict_user': DICT_USER_INFO, 'student_list': STUDENT_LIST})
    
    # if login.result == 'ok':
    if (1): # Tạm thời bỏ qua login để test GUI
        window.state('zoomed') # Phóng to cửa sổ, giữ thanh tiêu đề
        
        # Đảm bảo DICT_USER_INFO không None trước khi truy cập
        if DICT_USER_INFO and isinstance(DICT_USER_INFO, list) and len(DICT_USER_INFO) > 0:
            mssv = DICT_USER_INFO[0].get('mssv', '0')
            if mssv == '0' or mssv == '1':
                ACCOUNT_ROLE = 'ADMIN'
        else:
            print("DICT_USER_INFO không hợp lệ hoặc rỗng.")
            ACCOUNT_ROLE = 'GUEST' # Gán một vai trò mặc định

        update_model()

        # Cấu hình grid cho cửa sổ chính (window)
        window.grid_rowconfigure(1, weight=1) 
        window.grid_columnconfigure(0, weight=1) 
        
        # fr_header: header hiển thị nút điều khiển #############################################
        fr_header = tk.Frame(window)
        fr_header.grid(row=0, column=0, columnspan=3, sticky='nswe', pady=5)

        # fr_footer hiển thị thông tin footer #################################################
        fr_footer = tk.Frame(window)
        fr_footer.grid(row=2, column=0, columnspan=3, sticky='nswe')
        
        fr_header.columnconfigure(0, weight=1) 
        
        # Tạo PanedWindow
        paned_window = ttk.PanedWindow(window, orient=tk.HORIZONTAL)
        paned_window.grid(row=1, column=0, columnspan=3, sticky='nswe', padx=5, pady=5) 

        # fr_left: vùng trái trong PanedWindow #############################################
        fr_left = tk.Frame(paned_window, bg='lightgray') 
        paned_window.add(fr_left, weight=1) 

        # fr_center: vùng giữa trong PanedWindow ##########################################
        fr_center = tk.Frame(paned_window, bg='darkgray') 
        paned_window.add(fr_center, weight=2) 

        # fr_right: vùng phải trong PanedWindow #########################################
        fr_right = tk.Frame(paned_window, bg='gray') 
        paned_window.add(fr_right, weight=1) 

        # Định nghĩa hàm đặt sashpos
        def set_initial_sashes_after_zoom():
            window.update_idletasks() # Đảm bảo cửa sổ đã được cập nhật và phóng to
            
            current_paned_width = paned_window.winfo_width()
            
            min_width_left = 400
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
            print(f"DEBUG: PanedWidth: {current_paned_width}, Sash0: {paned_window.sashpos(0)}, Sash1: {paned_window.sashpos(1)}")

        # Gọi hàm này sau một khoảng thời gian ngắn để đảm bảo cửa sổ đã hoàn toàn phóng to
        window.after(200, set_initial_sashes_after_zoom) 
        
        # ------------------- Cấu hình các widget bên trong fr_header ---------------------
        fr_title = tk.Frame(fr_header, bg='green')
        fr_title.grid(row=0, column=0, sticky='nswe')
        fr_title.columnconfigure(0, weight=1) 
        
        tk.Label(fr_title, text='Kỹ thuật lập trình', font=("Arial", 14), 
                    fg="white", bg="green").grid(row=0, column=0, sticky='nswe')
        
        fr_control = tk.Frame(fr_header, bg='gray')
        fr_control.grid(row=1, column=0, sticky='nswe')
        
        # Các nút điều khiển trong fr_control (Đảm bảo chúng được tạo và gán biến)
        btn_exit = tk.Button(fr_control, text='Thoát', font=("Arial", 11), command=lambda: window_on_closing(window))
        btn_exit.grid(row=0, column=5, padx=5) 
        
        btn_refesh = tk.Button(fr_control, text='Làm mới')
        btn_refesh.grid(row=0, column=0, padx=5)
                
        btn_create_img_description = tk.Button(fr_control, text='Tạo giới thiệu ảnh')
        if ACCOUNT_ROLE == 'ADMIN':
            btn_create_img_description.grid(row=0, column=1, padx=5)

        btn_upload_course = tk.Button(fr_control, text='Cập nhập bài tập')
        if ACCOUNT_ROLE == 'ADMIN':
            btn_upload_course.grid(row=0, column=2, padx=5)
        
        btn_submit_exercise = tk.Button(fr_control, text="Nộp bài")
        btn_submit_exercise.grid(row=0, column=3, padx=5)
        
        btn_refesh_offline = tk.Button(fr_control, text='làm mới trực tiếp')
        if ACCOUNT_ROLE == 'ADMIN':
            btn_refesh_offline.grid(row=0, column=4, padx=5)

        # Các nút đã gây lỗi NameError trước đó, cần đảm bảo được định nghĩa và grid:
        btn_clear_cache = tk.Button(fr_control, text='Xóa Cache')
        btn_clear_cache.grid(row=0, column=6, padx=5) # Thay đổi column để không chồng chéo

        btn_load_rule = tk.Button(fr_control, text='load rule')
        btn_load_rule.grid(row=0, column=7, padx=5) # Đặt ở vị trí khác

        # Cấu hình footer
        fr_footer.columnconfigure(0, weight=1)
        
        fr_footer_tittle = tk.Frame(fr_footer)
        fr_footer_tittle.grid(row=0, column=0, sticky='nswe')
        
        fr_footer_tittle.columnconfigure(0, weight=1)
        tk.Label(fr_footer_tittle, text="Khoa điện-điện tử", font=("Arial", 14), 
                    fg="white", bg="green").grid(row=0, column=0, sticky='nswe')
        
        tk.Label(fr_footer, text=f'Version:{APP_VERSION}', font=("Arial", 14), fg="white", bg="green").grid(row=0, column=2, sticky='e')

        # ------------------- Bắt đầu phần tạo các frame và widget con ---------------------
        ##fr_nav (bên trong fr_left)
        fr_left.rowconfigure(0, weight=1)
        fr_left.columnconfigure(0, weight=1)
        
        fr_nav = tk.Frame(fr_left, bg='gray')
        fr_nav.grid(row=0, column=0, sticky='nswe')
        
        fr_nav.rowconfigure(1, weight=1)
        fr_nav.columnconfigure(0, weight=1)

        tk.Label(fr_nav, text="Danh sách bài tập", font=("Arial", 12), 
                    fg="white", bg="black").grid(row=0, column=0, sticky='nswe')
        
        fr_lesson_tree = tk.Frame(fr_nav, bg='yellow')
        fr_lesson_tree.grid(row=1, column=0, sticky='nswe')
        
        fr_lesson_tree.rowconfigure(0, weight=1)
        fr_lesson_tree.columnconfigure(0, weight=1)

        tree = ttk.Treeview(fr_lesson_tree, columns=("status", "score"), show="tree headings")
        tree.heading("status", text="Trạng thái", anchor='w')
        tree.heading("score", text="Điểm", anchor='w')
        tree.column("status", width=75, stretch=False)
        tree.column("score", width=75, stretch=False)
        
        tree.grid(row=0, column=0, sticky='nswe')
        #apply_treeview_style() # Uncomment nếu bạn đã định nghĩa hàm này

        #fr_input (bên trong fr_center)
        fr_center.rowconfigure(0, weight=3)
        fr_center.columnconfigure(0, weight=1)
        
        fr_input = tk.Frame(fr_center, bg='black')
        fr_input.grid(row=0, column=0, sticky="nswe")
        fr_input.grid_propagate(False) # Ngăn không cho frame co lại theo nội dung
        
        fr_input.rowconfigure(1, weight=1)
        fr_input.columnconfigure(0, weight=1)

        tk.Label(fr_input, text='Bài làm', font=("Arial", 12), 
                    fg="white", bg="black").grid(row=0, column=0)
        
        txt_input = CodeEditor(
                fr_input,
                language="c",               
                font=("Consolas", 14),
                highlighter="monokai",      # Sử dụng monokai nếu default gây lỗi
                blockcursor=True,
                cursor="xterm",             
                wrap="word")
        txt_input.grid(row=1, column=0, sticky='nswe', padx=5, pady=5)
        
        fr_input_btn = tk.Frame(fr_input, bg='black')
        fr_input_btn.grid(row=2, column=0, sticky='nswe')
        
        fr_input_btn.columnconfigure(0, weight=1)
        fr_input_btn.columnconfigure(1, weight=1)
        fr_input_btn.columnconfigure(2, weight=1)
        
        btn_run_code = tk.Button(fr_input_btn, text='run code', font=("Arial", 11))
        btn_run_code.grid(row=0, column=0, sticky='n')
    
        btn_send = tk.Button(fr_input_btn, text='Gửi đến AI', font=("Arial", 11))
        btn_send.grid(row=0, column=1, sticky='n')
        
        btn_help = tk.Button(fr_input_btn, text='AI Giúp đỡ', font=("Arial", 11))
        btn_help.grid(row=0, column=2, sticky='n')
        
        #fr_response (bên trong fr_right)
        fr_right.rowconfigure(0, weight=1)
        fr_right.columnconfigure(0, weight=1)
        
        fr_response = tk.Frame(fr_right, bg='black')
        fr_response.grid(row=0, column=0, sticky="nswe")
        
        fr_response.rowconfigure(0, weight=0)
        fr_response.rowconfigure(1, weight=1)
        fr_response.columnconfigure(0, weight=1)
        
        tk.Label(fr_response, text='AI phản hồi', font=("Arial", 12), 
                    fg="white", bg="black").grid(row=0, column=0, sticky='n')
        
        txt_output = HTMLLabel(fr_response)
        txt_output.grid(row=1, column=0, sticky='nswe')
        
        tk.Label(fr_response, text='Đánh giá', font=("Arial", 12), 
                    fg="white", bg="black").grid(row=2, column=0, sticky='n')
        
        fr_info = tk.Frame(fr_response)
        fr_info.grid(row=3, column=0, sticky='nswe')
        fr_info.columnconfigure(0, weight=1)
        fr_info.columnconfigure(1, weight=1)
        fr_info.columnconfigure(2, weight=1)
        fr_info.columnconfigure(3, weight=1)
        
        tk.Label(fr_info, text='Level:', font=("Arial", 12)).grid(row=0, column=0, sticky='w')
        lbl_level = tk.Label(fr_info, text='-', font=("Arial", 12))
        lbl_level.grid(row=0, column=1, sticky='w')
        tk.Label(fr_info, text='Score', font=("Arial", 12)).grid(row=0, column=2, sticky='w')
        lbl_socre = tk.Label(fr_info, text='-', font=("Arial", 12))
        lbl_socre.grid(row=0, column=3, sticky='w')   
        
        # ------------------- Kết thúc phần tạo các frame và widget con ---------------------

        ############################# Logic : event ####################
        # fr_control (các nút đã được tạo ở trên, bây giờ chỉ config command)
        btn_send.config(command=lambda: btn_send_click({'input': txt_input, 'queue': queue, 'output': txt_output}))
        btn_help.config(command=lambda: btn_help_click({'queue': queue, 'output': txt_output, 'fr_info': {'level': lbl_level, 'score': lbl_socre}}))
        btn_run_code.config(command=lambda: btn_run_code_click({'input': txt_input}))
        btn_clear_cache.config(command=lambda: btn_clear_cache_click({'input': txt_input, 'output': txt_output}))
        btn_load_rule.config(command=lambda: btn_load_rule_click({'queue': queue, 'output': txt_output})) # Đảm bảo nút này đã được tạo
        btn_refesh.config(command=lambda: btn_refesh_click({"tree": tree}))
        btn_create_img_description.config(command=lambda: btn_create_img_description_click({'model': model, 'frame': fr_center}))
        btn_submit_exercise.config(command=lambda: btn_submit_exercise_click({'frame': fr_center}))
        btn_upload_course.config(command=lambda: btn_upload_course_click({'frame': fr_center}))
        btn_refesh_offline.config(command=lambda: btn_refesh_offline_click({"tree": tree}))
        
        tree.bind("<<TreeviewSelect>>", lambda event: on_select(event, {"tree": tree, "fr_tree": fr_lesson_tree, "queue": queue, "output": txt_output, "fr_info": {'level': lbl_level, 'score': lbl_socre}}))
        if json_course is not None:
            tree_load(tree, json_course)
        else:
            messagebox.showerror("Error", "lỗi load file data")   
            
        #sự kiện
        window.protocol("WM_DELETE_WINDOW", lambda: window_on_closing(window))
        
        #load conversation
        if(CACHE_STATUS == 1):
            continue_conversation(txt_output, {'level': lbl_level, 'score': lbl_socre})
            
        update_response(window, queue)
        
        window.mainloop()
        
    else:
        print("Đăng nhập thất bại / Đóng cửa sổ login")
        window.destroy()
    
if __name__ == '__main__':
    main()