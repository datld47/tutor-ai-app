# import gdown
# import rarfile
# import os
# import threading
# from tkinter import messagebox
# from usercustomize import PATH_COMPILER, PATH_DOWNLOAD

# # --- THÊM DÒNG NÀY ---
# # THAY ĐỔI ĐƯỜNG DẪN NÀY cho phù hợp với máy của bạn
# UNRAR_PATH = r"compiler\UnRAR.exe" 
# # =====================

# def download_and_extract_compiler(compiler_name, url, status_callback):
#     """Tải và giải nén một compiler trong một luồng riêng biệt."""
    
#     def worker():
#         try:
#             # --- THÊM DÒNG NÀY ĐỂ CHỈ ĐỊNH PATH ---
#             if os.path.exists(UNRAR_PATH):
#                 rarfile.UNRAR_TOOL = UNRAR_PATH
#             else:
#                 messagebox.showerror("Lỗi WinRAR", f"Không tìm thấy UnRAR.exe tại đường dẫn:\n{UNRAR_PATH}\nVui lòng cài đặt WinRAR và cập nhật đường dẫn trong compiler_manager.py.")
#                 status_callback(f"✗ Lỗi: Không tìm thấy WinRAR.")
#                 return
#             # ========================================

#             # 1. Tải file .rar về thư mục download
#             status_callback(f"Đang tải {compiler_name}...")
#             rar_filename = f"{compiler_name}_compiler.rar"
#             download_path = os.path.join(PATH_DOWNLOAD, rar_filename)
            
#             gdown.download(url, download_path, quiet=False)
            
#             # 2. Giải nén vào thư mục compiler
#             status_callback(f"Đang giải nén {compiler_name}...")
#             with rarfile.RarFile(download_path) as rf:
#                 rf.extractall(path=PATH_COMPILER)
            
#             # 3. Dọn dẹp file .rar đã tải
#             os.remove(download_path)
            
#             status_callback(f"✓ Cài đặt {compiler_name} thành công!")
            
#         except Exception as e:
#             error_msg = f"✗ Lỗi khi cài đặt {compiler_name}: {e}"
#             status_callback(error_msg)
#             messagebox.showerror("Lỗi Tải", error_msg)

#     # Chạy tiến trình trong một luồng riêng để không làm treo giao diện
#     thread = threading.Thread(target=worker)
#     thread.daemon = True
#     thread.start()

import gdown
import rarfile
import os
import sys
import threading
from tkinter import messagebox
from usercustomize import PATH_COMPILER, PATH_DOWNLOAD

# Đường dẫn này nên trỏ đến file UnRAR.exe trong thư mục compiler
# sau khi ứng dụng được đóng gói.
UNRAR_PATH = os.path.join(PATH_COMPILER, "UnRAR.exe")

def download_and_extract_compiler(compiler_name, url, on_finish_callback):
    """Tải và giải nén một compiler trong một luồng riêng biệt."""
    
    def worker():
        # === KHỐI CODE MỚI: Xử lý lỗi console output khi đóng gói ===
        # Tạo một đối tượng giả lập console để hứng các output không mong muốn
        class DummyStream:
            def write(self, x): pass
            def flush(self, *args, **kwargs): pass

        # Nếu chạy dưới dạng file .exe và không có console, chuyển hướng output
        if getattr(sys, 'frozen', False) and sys.stdout is None:
            sys.stdout = DummyStream()
            sys.stderr = DummyStream()
        # =============================================================

        try:
            # Kiểm tra UnRAR tool
            if not os.path.exists(UNRAR_PATH):
                # Hiển thị lỗi này trước khi bắt đầu tải
                messagebox.showerror("Lỗi WinRAR", f"Không tìm thấy UnRAR.exe tại đường dẫn:\n{UNRAR_PATH}\nVui lòng đảm bảo UnRAR.exe được đóng gói cùng ứng dụng.")
                on_finish_callback(f"✗ Lỗi: Không tìm thấy UnRAR.exe.")
                return

            rarfile.UNRAR_TOOL = UNRAR_PATH

            # 1. Tải file .rar
            on_finish_callback(f"Đang tải {compiler_name}...")
            rar_filename = f"{compiler_name}_compiler.rar"
            download_path = os.path.join(PATH_DOWNLOAD, rar_filename)
            
            gdown.download(url, download_path, quiet=False)
            
            # 2. Giải nén
            on_finish_callback(f"Đang giải nén {compiler_name}...")
            with rarfile.RarFile(download_path) as rf:
                rf.extractall(path=PATH_COMPILER)
            
            # 3. Dọn dẹp
            os.remove(download_path)
            
            on_finish_callback(f"✓ Cài đặt {compiler_name} thành công!")
            
        except Exception as e:
            error_msg = f"✗ Lỗi khi cài đặt {compiler_name}: {e}"
            on_finish_callback(error_msg)
            # Không cần messagebox ở đây nữa vì on_finish_callback sẽ xử lý
            print(error_msg)

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()