import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import tempfile
import platform
# from usercustomize import * # Bạn có thể đã import nó ở app.py, nếu không thì cần import ở đây
import shutil
import sys # Thêm dòng này để sys.frozen có thể hoạt động

# Giả định get_path và create_folder được định nghĩa hoặc import từ usercustomize.py
# Nếu usercustomize.py không được import, bạn cần định nghĩa chúng trực tiếp hoặc import từ nơi khác.
# Ví dụ đơn giản cho get_path nếu không dùng usercustomize:
def get_path(relative_path):
    if getattr(sys, 'frozen', False):
        # Khi đóng gói, base_dir là thư mục chứa file exe (ví dụ: dist/app)
        base_dir = os.path.dirname(sys.executable)
    else:
        # Trong môi trường dev, base_dir là thư mục chứa script
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(base_dir, relative_path))

def create_folder(path):
    os.makedirs(path, exist_ok=True)

# THAY ĐỔI LỚN TẠI ĐÂY: Sử dụng PATH_COMPILER làm gốc
# Giả sử PATH_COMPILER được truyền vào hoặc là biến global đã được định nghĩa
# Để đơn giản, tôi sẽ định nghĩa một biến tạm PATH_COMPILER ở đây,
# nhưng trong thực tế nó sẽ đến từ app.py hoặc một file cấu hình chung.
# (Bạn cần đảm bảo biến PATH_COMPILER này thực sự được truyền vào hoặc global từ app.py)
# Dưới đây là cách bạn có thể định nghĩa PATH_COMPILER trong compiler_c.py nếu nó không được truyền vào
# và bạn muốn nó hoạt động độc lập (ít khuyến khích nếu đã có PATH_COMPILER ở app.py)

# if getattr(sys, 'frozen', False):    
#     PATH_COMPILER_LOCAL = get_path('../compiler') # Giả định cấu trúc dist/app/../compiler
# else:   
#     PATH_COMPILER_LOCAL = get_path('compiler') # Giả định cấu trúc project_root/compiler

# KHỐI CODE BỊ LỖI
PATH_COMPILER_LOCAL = get_path('compiler')

# Đường dẫn đến các thành phần compiler/interpreter
# Dựa vào cấu trúc thư mục mà bạn đã copy vào thư mục "compiler"
ucrt_path = os.path.join(PATH_COMPILER_LOCAL, "ucrt64", "bin")
jdk_path = os.path.join(PATH_COMPILER_LOCAL, "jdk-23", "bin")
python_path = os.path.join(PATH_COMPILER_LOCAL, "python313") # Thư mục chứa python.exe

# Thêm các đường dẫn vào biến môi trường PATH
os.environ["PATH"] = f"{ucrt_path};{jdk_path};{python_path};" + os.environ["PATH"]

# Global DIR_TEMP
# if getattr(sys, 'frozen', False):
#     DIR_TEMP = get_path('temp') # Có thể là ../temp nếu bạn muốn nó nằm ngoài thư mục app
#     create_folder(DIR_TEMP)
# else:   
#     DIR_TEMP = get_path('temp') # Hoặc 'project/project4/temp' nếu cấu trúc thư mục của bạn yêu cầu
#     create_folder(DIR_TEMP)
DIR_TEMP = get_path('temp')
create_folder(DIR_TEMP)
    
def compile_code(code):
    with tempfile.TemporaryDirectory(dir=DIR_TEMP) as temp_dir:
        print(temp_dir)
        c_file = os.path.join(temp_dir, "program.c")
        with open(c_file, "w", encoding="utf-8") as f:
            f.write(code)
       
        exe_file = os.path.join(temp_dir, "program.exe") if platform.system() == "Windows" else os.path.join(temp_dir, "program")

        # GCC đã có trong PATH nhờ dòng os.environ["PATH"] ở trên
        compile_cmd = ["gcc", c_file, "-o", exe_file]

        try:
            subprocess.run(compile_cmd, capture_output=True, text=True, check=True)
            exe_file_ = os.path.join(DIR_TEMP,"program.exe") # Copy ra DIR_TEMP để dễ chạy
            shutil.copy(exe_file, exe_file_)
            
        except subprocess.CalledProcessError as e:
            if platform.system() == "Windows":
                error_bat = os.path.join(DIR_TEMP, "compile_error.bat")
                with open(error_bat, "w", encoding="utf-8") as f:
                    f.write(f"@echo off\n")
                    for line in e.stderr.splitlines():
                        f.write(f"echo {line}\n")
                    f.write("pause\n")
                subprocess.Popen(f'start cmd /k "{error_bat}"', shell=True)
                return "Lỗi biên dịch (xem CMD)..."
            else:
                return f"Lỗi biên dịch:\n{e.stderr}"
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["start","cmd", "/k", exe_file_], shell=True)
            elif platform.system() == "Linux":
                subprocess.Popen(["x-terminal-emulator", "-e", exe_file_])
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", "Terminal", exe_file_])
            else:
                return "Không hỗ trợ hệ điều hành này."
            return "Chạy chương trình trong terminal riêng..."
        except Exception as e:
            return f"Lỗi khi chạy chương trình: {e}"

def compile_java(code):
    temp_dir = tempfile.mkdtemp(dir=DIR_TEMP)
    print(f"DEBUG: Thư mục tạm thời: {temp_dir}")

    try:
        java_file = os.path.join(temp_dir, "Program.java")
        with open(java_file, "w", encoding="utf-8") as f:
            f.write(code)

        # javac đã có trong PATH
        compile_cmd = ["javac", java_file]
        try:
            subprocess.run(compile_cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            if platform.system() == "Windows":
                error_bat = os.path.join(temp_dir, "compile_error_java.bat")
                with open(error_bat, "w", encoding="utf-8") as f:
                    f.write(f"@echo off\n")
                    for line in e.stderr.splitlines():
                        f.write(f"echo {line}\n")
                    f.write("pause\n")
                subprocess.Popen(f'start cmd /k "{error_bat}"', shell=True)
                return "Lỗi biên dịch Java (xem CMD)..."
            else:
                return f"Lỗi biên dịch Java:\n{e.stderr}"
        
        # Chạy bằng java (cũng đã có trong PATH)
        if platform.system() == "Windows":
            cmd_command = f'java Program & pause'
            subprocess.Popen(["start", "cmd", "/k", cmd_command], shell=True, cwd=temp_dir)
        elif platform.system() == "Linux":
            subprocess.Popen(["x-terminal-emulator", "-e", "bash", "-c", f"java -cp . Program; read -p 'Press Enter to continue...'"], cwd=temp_dir)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", "Terminal", "bash", "-c", f"java -cp . Program; read -p 'Press Enter to continue...'"], cwd=temp_dir)
        else:
            return "Không hỗ trợ hệ điều hành này."
        
        return "Chạy chương trình Java trong terminal riêng..."
    except Exception as e:
        return f"Lỗi khi chạy chương trình Java: {e}"
    finally:
        pass
        
def run_python(code):
    temp_dir = tempfile.mkdtemp(dir=DIR_TEMP)
    print(f"DEBUG: Thư mục tạm thời: {temp_dir}")

    try:
        python_file = os.path.join(temp_dir, "program.py")
        with open(python_file, "w", encoding="utf-8") as f:
            f.write(code)

        # Đường dẫn đầy đủ đến python.exe từ python_path (đã được thêm vào PATH)
        python_exe_full_path = os.path.join(python_path, "python.exe") if platform.system() == "Windows" else os.path.join(python_path, "python")

        if platform.system() == "Windows":
            python_cmd_part = subprocess.list2cmdline([python_exe_full_path, python_file])
            full_cmd_to_run_in_new_cmd = f'{python_cmd_part} & pause'
            
            subprocess.Popen(
                ["start", "cmd", "/k", full_cmd_to_run_in_new_cmd],
                shell=True,
                cwd=temp_dir
            )
        elif platform.system() == "Linux":
            # Kiểm tra python_exe_full_path có tồn tại không. Nếu không, dùng 'python3' hoặc 'python'
            if os.path.exists(python_exe_full_path):
                 run_cmd = [python_exe_full_path, python_file]
            else:
                 run_cmd = ["python3", python_file] # Fallback
            subprocess.Popen(["x-terminal-emulator", "-e", "bash", "-c", f"{subprocess.list2cmdline(run_cmd)}; read -p 'Press Enter to continue...'"], cwd=temp_dir)
        elif platform.system() == "Darwin":
            if os.path.exists(python_exe_full_path):
                 run_cmd = [python_exe_full_path, python_file]
            else:
                 run_cmd = ["python3", python_file] # Fallback
            subprocess.Popen(["open", "-a", "Terminal", "bash", "-c", f"{subprocess.list2cmdline(run_cmd)}; read -p 'Press Enter to continue...'"], cwd=temp_dir)
        else:
            return "Không hỗ trợ hệ điều hành này."
        return "Chạy chương trình Python trong terminal riêng..."
    except FileNotFoundError:
        return f"Lỗi: Không tìm thấy trình thông dịch Python tại '{python_exe_full_path}'. Vui lòng kiểm tra cài đặt Python hoặc đường dẫn."
    except Exception as e:
        return f"Lỗi khi chạy chương trình Python: {e}"
    finally:
        pass