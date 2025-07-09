import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import tempfile
import platform
from usercustomize1 import *
import shutil

    
# Giả định các hàm get_path và create_folder từ usercustomize.py đã được định nghĩa hoặc thay thế
def get_path(relative_path):
    # Đây là một giả định, bạn cần đảm bảo hàm này hoạt động đúng trong môi trường của bạn
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(base_dir, relative_path))

def create_folder(path):
    os.makedirs(path, exist_ok=True)

# Thêm dòng này để đảm bảo gcc được nhận diện
# msys_path = os.path.abspath("msys64a/mingw64/bin")
# os.environ["PATH"] = f"{msys_path};" + os.environ["PATH"]
ucrt_path = os.path.abspath("compiler/ucrt64/bin")
os.environ["PATH"] = f"{ucrt_path};" + os.environ["PATH"]

# Đường dẫn đến thư mục bin của JDK bạn copy
jdk_path = os.path.abspath(r"compiler/jdk-23/bin")
os.environ["PATH"] = f"{jdk_path};" + os.environ["PATH"]

# Global DIR_TEMP
if getattr(sys, 'frozen', False):
    DIR_TEMP = get_path('../temp')
    create_folder(DIR_TEMP)
else:   
    DIR_TEMP = get_path('project/project4/temp')
    create_folder(DIR_TEMP)
    
def compile_code(code):
    with tempfile.TemporaryDirectory(dir=DIR_TEMP) as temp_dir:
        print(temp_dir)
        c_file = os.path.join(temp_dir, "program.c")
        with open(c_file, "w", encoding="utf-8") as f:
            f.write(code)
       
        exe_file = os.path.join(temp_dir, "program.exe") if platform.system() == "Windows" else os.path.join(temp_dir, "program")

        compile_cmd = ["gcc", c_file, "-o", exe_file]

        try:
            subprocess.run(compile_cmd, capture_output=True, text=True, check=True)
            exe_file_ = os.path.join(DIR_TEMP,"program.exe")
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
    # Tạo thư mục tạm thời thủ công thay vì dùng with
    temp_dir = tempfile.mkdtemp(dir=DIR_TEMP)
    print(f"DEBUG: Thư mục tạm thời: {temp_dir}")

    try:
        java_file = os.path.join(temp_dir, "Program.java")
        with open(java_file, "w", encoding="utf-8") as f:
            f.write(code)

        compile_cmd = ["javac", java_file]
        try:
            subprocess.run(compile_cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            if platform.system() == "Windows":
                error_bat = os.path.join(temp_dir, "compile_error_java.bat") # Sử dụng temp_dir ở đây
                with open(error_bat, "w", encoding="utf-8") as f:
                    f.write(f"@echo off\n")
                    for line in e.stderr.splitlines():
                        f.write(f"echo {line}\n")
                    f.write("pause\n")
                subprocess.Popen(f'start cmd /k "{error_bat}"', shell=True)
                return "Lỗi biên dịch Java (xem CMD)..."
            else:
                return f"Lỗi biên dịch Java:\n{e.stderr}"
        
        # Chạy bằng java
        if platform.system() == "Windows":
            cmd_command = f'java Program & pause'
            # Sử dụng popen để mở cửa sổ CMD mới, giữ nó mở, và chạy từ thư mục tạm thời
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
        # Quan trọng: Không xóa thư mục tạm thời ở đây nếu bạn muốn cửa sổ CMD vẫn mở
        # Việc xóa sẽ được thực hiện khi ứng dụng Python thoát, hoặc bạn có thể tạo một cơ chế dọn dẹp riêng
        # For now, to avoid the RecursionError with Popen, we will not delete it immediately.
        # It's generally better to let the OS handle temp folder cleanup on exit, or have a
        # separate cleanup mechanism for long-running apps.
        pass # Bỏ qua việc xóa thư mục tạm thời ở đây
        
def show_result_compile(args):
    code_input=args['input']
    output_display = args['output']  # Lấy tham số label từ args
    code = code_input.get("1.0", tk.END)
    if not code.strip():
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã C để chạy.")
        return
    output_display.delete("1.0", tk.END)
    
    #for C
    #result=compile_code(code)
    
    #for java
    result=compile_java(code)
    output_display.insert(tk.END,result)
    
def main():
    # # Giao diện người dùng
    root = tk.Tk()
    root.title("Trình chạy mã C")

    tk.Label(root, text="Nhập mã C:").pack()
    code_input = scrolledtext.ScrolledText(root, width=80, height=20)
    code_input.pack()

    tk.Button(root, text="Biên dịch và chạy", command=lambda:show_result_compile({'input':code_input,'output':output_display})).pack(pady=10)

    tk.Label(root, text="Kết quả đầu ra:").pack()
    output_display = scrolledtext.ScrolledText(root, width=80, height=10)
    output_display.pack()
    
    root.mainloop()

if __name__=='__main__':
    main()