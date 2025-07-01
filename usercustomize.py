import os
import sys
import shutil
import datetime
import random
import json
from pathlib import Path
from abc import ABC, abstractmethod

#duong dan

#cwd= os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../'))
cwd = os.path.dirname(os.path.abspath(__file__))  # Thư mục chứa file usercustomize.py

print(cwd)
def get_path(path):
    return os.path.abspath(os.path.join(cwd,f'./{path}'))

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