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