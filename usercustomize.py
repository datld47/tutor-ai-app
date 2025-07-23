import os
import sys
import shutil

# ==============================================================================
# SECTION 1: TRUNG TÂM QUẢN LÝ ĐƯỜNG DẪN
# ==============================================================================

# Xác định xem ứng dụng đang chạy dưới dạng file .exe (đã đóng gói) hay file .py
IS_FROZEN = getattr(sys, 'frozen', False)

# --- Thư mục gốc cho dữ liệu CÓ THỂ GHI (log, cache, temp, download, data) ---
if IS_FROZEN:
    # Nếu đã cài đặt, tất cả dữ liệu người dùng phải nằm trong AppData\Local
    # Ví dụ: C:\Users\TenNguoiDung\AppData\Local\TutorAI
    WRITABLE_DATA_ROOT = os.path.join(os.getenv('LOCALAPPDATA'), 'TutorAI')
else:
    # Nếu đang phát triển, dữ liệu nằm ngay trong thư mục gốc của dự án
    # Giả sử file này (usercustomize.py) nằm ở thư mục gốc
    WRITABLE_DATA_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- Thư mục gốc cho các tài nguyên CHỈ ĐỌC (trình biên dịch, hình ảnh...) ---
if IS_FROZEN:
    # Nếu đã cài đặt, tài nguyên nằm trong thư mục cài đặt
    # Ví dụ: C:\Program Files\TutorAI
    READ_ONLY_ASSET_ROOT = os.path.dirname(sys.executable)
else:
    # Nếu đang phát triển, tài nguyên nằm trong thư mục gốc của dự án
    READ_ONLY_ASSET_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- Định nghĩa tất cả các đường dẫn một cách tập trung ---
# Đường dẫn có thể GHI
PATH_TEMP     = os.path.join(WRITABLE_DATA_ROOT, 'temp')
PATH_CACHE    = os.path.join(WRITABLE_DATA_ROOT, 'cache')
PATH_LOG      = os.path.join(WRITABLE_DATA_ROOT, 'log')
PATH_DOWNLOAD = os.path.join(WRITABLE_DATA_ROOT, 'download')
PATH_DATA     = os.path.join(WRITABLE_DATA_ROOT, 'data')
PATH_UPLOAD   = os.path.join(WRITABLE_DATA_ROOT, 'upload') # <-- DÒNG ĐƯỢC THÊM VÀO

# Đường dẫn chỉ ĐỌC
PATH_COMPILER = os.path.join(READ_ONLY_ASSET_ROOT, 'compiler')
PATH_IMG      = os.path.join(READ_ONLY_ASSET_ROOT, 'img')

# Khai báo đường dẫn cho thư mục chứa công cụ editor
PATH_EDIT_TOOLS = os.path.join(READ_ONLY_ASSET_ROOT, "editTools")

def initialize_app_folders():
    """
    Hàm này phải được gọi MỘT LẦN DUY NHẤT khi ứng dụng khởi động.
    Nó sẽ tạo tất cả các thư mục cần thiết tại đúng vị trí có quyền ghi.
    """
    print("Initializing writable application folders...")
    # Thêm PATH_UPLOAD vào danh sách này
    for path in [PATH_TEMP, PATH_CACHE, PATH_LOG, PATH_DOWNLOAD, PATH_DATA, PATH_UPLOAD]:
        os.makedirs(path, exist_ok=True)
    print(f"Folders initialized in: {WRITABLE_DATA_ROOT}")

# ==============================================================================
# SECTION 2: CÁC HÀM TIỆN ÍCH KHÁC (Không liên quan đến tạo thư mục)
# ==============================================================================

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
    if not os.path.exists(folder_path):
        return
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)