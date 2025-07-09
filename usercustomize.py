import os
import sys
import shutil
import datetime
import random
import json
from pathlib import Path
from abc import ABC, abstractmethod

# #duong dan
# cwd= os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../'))
# # print(cwd)
# def get_path(path):
#     return os.path.abspath(os.path.join(cwd,f'./{path}'))
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def get_path(path):
    if getattr(sys, 'frozen', False):
        # Khi chạy từ file .exe đã đóng gói
        base_path = os.path.dirname(sys.executable)
    else:
        # Khi chạy từ mã nguồn
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
        
    return os.path.abspath(os.path.join(base_path, path))

# def get_path(relative_path_from_exe_dir): # Đổi tên tham số cho rõ nghĩa hơn
#     if getattr(sys, 'frozen', False):
#         base_path = os.path.dirname(sys.executable)
#     else:
#         # Khi chạy từ mã nguồn, base_path là thư mục chứa usercustomize.py
#         # Nếu app.py và data/ nằm ở cấp trên, cần điều chỉnh
#         # Giả sử usercustomize.py nằm trong venv/Lib/site-packages/
#         # và project root là 3 cấp trên:
#         # your_project_root/venv/Lib/site-packages/usercustomize.py
#         # Để về project_root: os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

#         # Tuy nhiên, nếu bạn muốn data/ nằm CÙNG CẤP với app.py trong dev env,
#         # thì base_path phải là thư mục chứa app.py.
#         # Cách đơn giản nhất là truyền relative_path_from_exe_dir đúng từ nơi gọi.
#         # Nếu app.py gọi get_path('data/config.json') thì base_path là thư mục của app.py.
#         # Nếu google_driver_api.py gọi get_path('data/credentials.json') thì base_path là thư mục của google_driver_api.py.
#         # Cách an toàn nhất là base_path luôn là thư mục gốc của project trong môi trường dev.
#         # (Bạn cần điều chỉnh này tùy thuộc vào cấu trúc dự án thực tế của bạn)

#         # CÁCH ĐƠN GIẢN HÓA VÀ AN TOÀN NHẤT cho DEVELOPMENT:
#         # Hãy dùng thư mục hiện tại của script đang chạy (app.py hoặc google_driver_api.py)
#         # như là base_path, và các đường dẫn như 'data/config.json' sẽ là tương đối với nó.
#         base_path = os.path.dirname(os.path.abspath(sys.argv[0])) # Lấy thư mục của script chính

#         # Nếu bạn muốn base_path luôn là thư mục gốc của dự án trong dev (nếu app.py không ở gốc)
#         # Bạn cần một biến global hoặc cách khác để xác định project root.
#         # Ví dụ (nếu usercustomize.py trong venv/Lib/site-packages):
#         # script_dir = os.path.dirname(os.path.abspath(__file__))
#         # base_path = os.path.abspath(os.path.join(script_dir, '..', '..', '..')) # 3 cấp lên project root

#     return os.path.abspath(os.path.join(base_path, relative_path_from_exe_dir))


def get_path_join(abspath,path):
    return os.path.abspath(os.path.join(abspath,f'./{path}'))

sys.path.append(get_path('user_library'))
sys.path.append(get_path('user_control'))
sys.path.append(get_path('project'))



#thao tac folder
def create_folder(folder_path):
    if os.path.exists(folder_path)==False:
         os.makedirs(folder_path)

def delete_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
       
def delete_folder_contents(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        os.makedirs(folder_path, exist_ok=True)

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        
def delete_all_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)