import sys
import os
import glob
import json
import re
import markdown
import traceback

# --- Import các thành phần của PyQt ---
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QHBoxLayout, QVBoxLayout, QSplitter,
    QTabWidget, QLabel, QComboBox, QTextEdit, QPushButton,
    QPlainTextEdit, QToolBar, QTreeWidget, QTreeWidgetItem,
    QTextBrowser, QGridLayout, QFileDialog, QMessageBox, QTreeWidgetItemIterator,
    QSizePolicy,
    QStackedWidget # <<<<<<<<<<<<<<< THÊM VÀO ĐÂY
)
from PyQt6.QtGui import QIcon, QAction
# Sửa thành dòng này
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

# --- Import các file logic ---
# Sửa thành dòng này
from usercustomize import PATH_IMG, PATH_DATA, PATH_EDIT_TOOLS
import google.generativeai as genai
from compiler_c import compile_code, compile_java, run_python

from PyQt6.QtWidgets import QFileDialog
from docx_importer import process_docx_to_json

import pyrebase
from login_gui import LoginApp # Import lớp LoginApp

from PyQt6.QtWidgets import QDialog

from login_gui_pyqt import LoginDialog # <<<<<<<<<< THÊM DÒNG NÀY

from api_key_dialog import ApiKeyDialog

from prompt.rule import create_main_rule

import html

#for image
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QDialog # Đảm bảo đã có dòng này

from PyQt6.QtGui import QFontMetrics # << THÊM QFontMetrics VÀO ĐÂY

#for editor code
#from code_editor import CodeEditor

from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerCPP, QsciLexerJava


# --- Khởi tạo cấu hình Firebase (dán vào đầu file, ngoài các class) ---
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

# Add this near your other global variables or imports
RE_RESPONSE_PROMPT = """
Phản hồi trước đó của bạn có JSON không hợp lệ và không thể được xử lý bằng `json.loads()` trong Python.
Lỗi cụ thể là: {error_message}

Vui lòng gửi lại toàn bộ phản hồi, sửa lại phần JSON để nó hợp lệ.
Toàn bộ phản hồi phải nằm trong block code ```json.
"""
INITIAL_SCORE = 10

# In app_pyqt.py, replace the old function with this one

# Trong file app_pyqt_working.py
# Thay thế hàm cũ bằng hàm này

# In app_pyqt_working.py, ensure this is your render function

def render_ai_json_markdown(response_text: str):
    """
    Parses the AI's response and extracts the raw Markdown text.
    The conversion to HTML is handled entirely by JavaScript in the client.
    """
    try:
        # Extract the raw markdown text from the DATA part
        data_match = re.search(r'\[START_DATA\](.*?)\[END_DATA\]', response_text, re.DOTALL)
        raw_markdown_text = data_match.group(1).strip() if data_match else ""

        # Extract and parse the INFO part
        info_match = re.search(r'\[START_INFO\](.*?)\[END_INFO\]', response_text, re.DOTALL)
        info_text = info_match.group(1).strip() if info_match else ""
        info_dict = {}
        if info_text:
            for line in info_text.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key == 'generated_steps':
                        info_dict[key] = [step.strip() for step in value.split('||')]
                    else:
                        info_dict[key] = value

        # Return the raw markdown, which will be processed by Marked.js and MathJax
        return raw_markdown_text, info_dict, None

    except Exception as err:
        print(f"--- ERROR PARSING RESPONSE (NEW FORMAT) ---")
        print(f"Error: {err}\nTraceback: {traceback.format_exc()}")
        error_html = (f"<h3>Error Parsing AI Response</h3>"
                      f"<p>The response format from the AI was incorrect.</p>")
        return error_html, {}, str(err)
    
# In app_pyqt_working.py

class GeminiWorker(QObject):
    finished = pyqtSignal(str, bool)
    error = pyqtSignal(str)

    def __init__(self, model, history):
        super().__init__()
        self.model = model
        self.history = history
        self.prompt = ""
        self.was_retry = False

    def run(self):
        try:
            message = [{'role': 'user', 'parts': [self.prompt]}]
            # History management can be simplified as well, this is a clean version
            self.history.extend(message)
            
            response = self.model.generate_content(self.history)
            original_text = response.text
            
            print("DEBUG: Raw AI Response Received:\n", original_text)
            
            # --- START OF THE FIX ---
            # REMOVE OR COMMENT OUT THE REGEX REPLACEMENT.
            # The multi-part text format makes this obsolete and it's what's
            # breaking your LaTeX formulas.
            # safe_response_text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', original_text)

            # Directly use the original text from the AI.
            safe_response_text = original_text
            # --- END OF THE FIX ---

            self.history.append({'role': 'model', 'parts': [original_text]})
            self.finished.emit(safe_response_text, self.was_retry)

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"--- ERROR IN GEMINI WORKER ---\n{error_details}")
            self.error.emit(str(e))

# THAY THẾ TOÀN BỘ LỚP CŨ BẰNG LỚP NÀY
class ClickableLabel(QLabel):
    """
    Một QLabel tùy chỉnh vừa có thể CLICK, vừa tự động RESIZE ảnh bên trong.
    """
    clicked = pyqtSignal()  # Tín hiệu cho việc click

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap()  # Biến để lưu trữ ảnh GỐC (chưa co giãn)

    def setOriginalPixmap(self, pixmap):
        """Lưu trữ ảnh gốc và hiển thị lần đầu."""
        self._pixmap = pixmap
        self.updatePixmap()

    def updatePixmap(self):
        """Co giãn ảnh gốc cho vừa với kích thước hiện tại của Label."""
        if not self._pixmap.isNull():
            # Co giãn ảnh gốc theo kích thước hiện tại của label, giữ nguyên tỷ lệ
            scaled_pixmap = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            # Dùng hàm setPixmap của lớp cha để hiển thị ảnh đã co giãn
            super().setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Bắt sự kiện khi kích thước của Label thay đổi (ví dụ: khi kéo splitter)."""
        self.updatePixmap()  # Gọi hàm để vẽ lại ảnh với kích thước mới
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        """Bắt sự kiện khi người dùng nhấn chuột vào label."""
        self.clicked.emit()
        super().mousePressEvent(event)

class ImageViewer(QDialog):
    """
    Một cửa sổ QDialog đơn giản để hiển thị một hình ảnh với kích thước lớn.
    Nó sẽ tự động co giãn ảnh cho vừa với màn hình.
    """
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Xem ảnh - " + os.path.basename(image_path))
        
        # Tạo label để chứa ảnh
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Tải ảnh gốc
        pixmap = QPixmap(image_path)
        
        # Lấy kích thước màn hình có sẵn để tránh cửa sổ quá lớn
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        
        # Co giãn ảnh cho vừa với 90% kích thước màn hình, giữ nguyên tỷ lệ
        scaled_pixmap = pixmap.scaled(
            int(screen_geometry.width() * 0.9),
            int(screen_geometry.height() * 0.9),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        
        # Thiết lập layout và kích thước cửa sổ
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        self.resize(scaled_pixmap.width() + 20, scaled_pixmap.height() + 20)
         
# --- Lớp Cửa sổ Chính ---

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Hàm toàn cục để bắt và xử lý tất cả các lỗi không được lường trước.
    Ngăn chương trình bị đóng đột ngột và hiển thị lỗi cho người dùng.
    """
    # Lấy chuỗi traceback chi tiết để in ra console cho việc debug
    traceback_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    print("--- LỖI TOÀN CỤC KHÔNG ĐƯỢC BẮT ---")
    print(traceback_details)
    print("-----------------------------------")

    # Tạo thông báo lỗi thân thiện cho người dùng
    error_message = (
        f"<b>Rất tiếc, một lỗi không mong muốn đã xảy ra!</b>"
        f"<p>Ứng dụng sẽ cố gắng tiếp tục hoạt động, nhưng một số chức năng có thể không ổn định. "
        f"Vui lòng lưu lại công việc của bạn và khởi động lại chương trình nếu cần thiết.</p>"
        f"<p><b>Chi tiết kỹ thuật:</b></p>"
        # Dùng html.escape để hiển thị an toàn thông điệp lỗi
        f"<pre>{html.escape(str(exc_value))}</pre>"
        f"<p><i>(Thông tin traceback đầy đủ đã được in ra trong cửa sổ dòng lệnh/terminal)</i></p>"
    )

    # Hiển thị hộp thoại lỗi nghiêm trọng cho người dùng
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Icon.Critical)
    error_box.setWindowTitle("Lỗi Hệ thống - Tutor AI")
    error_box.setTextFormat(Qt.TextFormat.RichText)
    error_box.setText(error_message)
    error_box.exec()
class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutor AI - V1.1")
        self.setGeometry(100, 100, 1600, 900)

        # --- BẮT ĐẦU SỬA LỖI ---
        # DI CHUYỂN KHỐI CODE NÀY TỪ CUỐI LÊN ĐẦU HÀM __init__
        self.chat_interface_ready = False
        self.js_call_queue = [] # Hàng đợi các lệnh JS sẽ được thực thi khi giao diện sẵn sàng
        # --- KẾT THÚC SỬA LỖI ---

        # --- Các biến trạng thái của ứng dụng ---
        self.COURSE_FILE_MAP = {}
        self.json_course = None
        self.current_exercise = None
        self.model = None
        self.history = []
        # XÓA BIẾN CŨ NÀY ĐI VÌ KHÔNG CÒN DÙNG
        # self.conversation_display_history = [] 
        self.main_rule = ""
        self.main_rule_lesson = ""
        self.prompt_template = ""
        self.current_course_language = "text"
        self.current_exercise_language = "text"
        
        self.API_KEY_LIST = []
        self.API_KEY = ""
        
        # --- Các biến trạng thái cho Firebase và người dùng ---
        self.firebase = None
        self.auth = None
        self.db = None
        self.user_info = {} # Lưu thông tin người dùng (uid, token, username)
        self.is_logged_in = False # Trạng thái đăng nhập
        
        # --- Các biến quản lý trạng thái giao diện ---
        self.current_session_index = -1
        self.current_exercise_index = -1
        self.editor_initialized = False 
        self.custom_editor_initialized = False
        self.highlighter = None

        # --- Xây dựng giao diện chính ---
        self.build_menus_and_toolbar()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Cấu hình QSplitter để layout ổn định ---
        # Lưu splitter làm thuộc tính của class để dễ truy cập
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Khởi tạo các khung chính
        self.fr_left = QWidget()
        self.fr_center = QWidget()
        self.fr_right = QWidget()

        # Thêm các khung vào splitter
        self.splitter.addWidget(self.fr_left)
        self.splitter.addWidget(self.fr_center)
        self.splitter.addWidget(self.fr_right)
        
        # Đặt kích thước ban đầu cho các khung
        self.splitter.setSizes([400, 800, 400])
        
        # CỐ ĐỊNH LAYOUT: Ra lệnh cho splitter ưu tiên không gian cho khung giữa
        # và giữ kích thước 2 khung bên cạnh ổn định.
        self.splitter.setStretchFactor(1, 1) # Khung giữa (index 1) sẽ co giãn
        self.splitter.setStretchFactor(0, 0) # Khung trái (index 0) không co giãn
        self.splitter.setStretchFactor(2, 0) # Khung phải (index 2) không co giãn
        # --- Kết thúc cấu hình QSplitter ---

        # Khai báo các editor và stack để chuyển đổi
        self.editor_stack = QStackedWidget()
        self.plain_code_editor = QPlainTextEdit() # Editor cho code
        self.rich_text_editor = QWebEngineView() # Editor cho văn bản có định dạng
        self.custom_editor_view = QWebEngineView()
        
        # Dựng nội dung chi tiết cho từng khung
        self.build_left_panel()
        self.build_center_panel()
        self.build_right_panel()
        
        # --- Hoàn tất thiết lập ---
        # Kết nối các tín hiệu (signals) tới các hành động (slots)
        self.connect_signals()
        # Tải dữ liệu ban đầu (khóa học, API keys,...)
        self.load_initial_data()
        
        # Cập nhật trạng thái editor cho tab "Bài tập Tự do" khi khởi động
        self.on_custom_language_select(self.lang_combobox.currentText())

        # Hiển thị cửa sổ ở chế độ toàn màn hình
        self.showMaximized()
        
        # self.chat_interface_ready = False
        # self.js_call_queue = [] # Hàng đợi các lệnh JS sẽ được thực thi khi giao diện sẵn sàng


    # Dán 3 hàm này vào trong class MainWindow của file app_pyqt_working.py

    def add_message_to_chat(self, html_content, message_type=""):
        """Gửi một tin nhắn mới vào giao diện chat một cách an toàn."""
        escaped_html = json.dumps(html_content)
        escaped_type = json.dumps(message_type)
        js_code = f"addMessage({escaped_html}, {escaped_type});"
        
        if self.chat_interface_ready:
            self.web_view.page().runJavaScript(js_code)
        else:
            self.js_call_queue.append(js_code)

    def clear_chat_interface(self):
        """Xóa toàn bộ nội dung chat một cách an toàn."""
        self.js_call_queue.clear()
        
        js_clear_code = "clearChat();"
        if self.chat_interface_ready:
            self.web_view.page().runJavaScript(js_clear_code)
        else:
            self.js_call_queue.append(js_clear_code)

    def on_chat_view_loaded(self, success):
        """Được kích hoạt khi QWebEngineView đã tải xong chat_view.html."""
        if success:
            print("✅ Giao diện chat đã sẵn sàng.")
            self.chat_interface_ready = True
            for js_code in self.js_call_queue:
                self.web_view.page().runJavaScript(js_code)
            self.js_call_queue.clear()
        else:
            print("❌ Lỗi: Không thể tải file chat_view.html.")
            
    # class MainWindow(QMainWindow):
    #   ... (code của bạn giữ nguyên) ...
    def save_last_working_key(self, key):
        """Lưu API key hoạt động gần nhất vào file config.json."""
        # Logic này cần được cập nhật để làm việc với cấu trúc config của bạn
        # Tạm thời chỉ in ra để xác nhận
        print(f"DEBUG: Cần cập nhật logic lưu key '{key}' vào config.json")

    def find_working_api_key(self, keys_to_check):
        """
        Kiểm tra danh sách các API key và trả về key đầu tiên hoạt động.
        """
        print("DEBUG: Bắt đầu tìm kiếm API key đang hoạt động...")
        for key in keys_to_check:
            try:
                genai.configure(api_key=key)
                # Thử tạo một model đơn giản để xác thực key
                genai.GenerativeModel('gemini-1.5-flash')
                print(f"DEBUG: Tìm thấy key hoạt động: ...{key[-4:]}")
                self.save_last_working_key(key) # Gọi phương thức của class
                return key
            except Exception as e:
                print(f"DEBUG: Key ...{key[-4:]} không hoạt động. Lỗi: {e}")
                continue # Thử key tiếp theo
        
        print("CẢNH BÁO: Không tìm thấy API key nào hoạt động trong danh sách.")
        return None # Trả về None nếu không có key nào hoạt động

    def reinitialize_gemini_model(self):
        """Khởi tạo lại model Gemini với danh sách key mới."""
        # Dòng này bây giờ sẽ hoạt động
        working_key = self.find_working_api_key(self.API_KEY_LIST) 
        if working_key:
            self.API_KEY = working_key
            genai.configure(api_key=self.API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            # CẬP NHẬT QUAN TRỌNG: Phải cập nhật model cho worker đang chạy
            if hasattr(self, 'worker'):
                self.worker.model = self.model
            print(f"Đã áp dụng API Key mới: ...{self.API_KEY[-4:]}")
        else:
            QMessageBox.critical(self, "Không có API Key", "Không có API Key nào trong danh sách mới hoạt động.")

    def update_user_info_callback(self, username, mssv, token):
        """Callback được gọi từ LoginApp để cập nhật thông tin người dùng."""
        self.is_logged_in = True
        self.user_info = {'username': username, 'uid': mssv, 'token': token}
        self.login_button.setText(f"👤 Xin chào, {username}!")
        print(f"Người dùng {username} (UID: {mssv}) đã đăng nhập.")

    def update_api_key_callback(self, uid):
        """
        Callback được gọi sau khi đăng nhập thành công để tải và áp dụng 
        API key cá nhân của người dùng từ Firebase.
        """
        if not self.db or not self.user_info.get('token'):
            print("DEBUG: Chưa sẵn sàng để tải API key (thiếu DB hoặc token).")
            return

        try:
            token = self.user_info['token']
            user_data = self.db.child("users").child(uid).get(token=token).val()
            user_keys = user_data.get('gemini_api_keys') if user_data else None

            if user_keys and isinstance(user_keys, list) and len(user_keys) > 0:
                print(f"DEBUG: Tìm thấy {len(user_keys)} API key cá nhân. Đang áp dụng...")
                # Cập nhật danh sách key của ứng dụng bằng key của người dùng
                self.API_KEY_LIST = user_keys
                # Gọi hàm để tìm key hoạt động và khởi tạo lại model
                self.reinitialize_gemini_model()
            else:
                print("DEBUG: Người dùng chưa có API key cá nhân, dùng key mặc định.")
                # Nếu người dùng không có key, chúng ta sẽ reset về key mặc định
                # được load lúc khởi động ứng dụng.
                self.load_default_api_keys() # Cần tạo hàm này
                self.reinitialize_gemini_model()
        
        except Exception as e:
            print(f"Lỗi khi tải API key cá nhân: {e}")
            # Nếu có lỗi, an toàn nhất là quay về dùng key mặc định
            self.load_default_api_keys()
            self.reinitialize_gemini_model()
    
    def load_default_api_keys(self):
        """Tải danh sách API key mặc định từ config.json."""
        try:
            with open(os.path.join(PATH_DATA, 'config.json'), "r", encoding="utf-8") as file:
                config = json.load(file)

            # Giả sử cấu trúc file config của bạn giống phiên bản Tkinter
            default_keys = config.get('api', [{}])[0].get('gemini_key', [])
            self.API_KEY_LIST = default_keys
            print(f"DEBUG: Đã tải {len(self.API_KEY_LIST)} API key mặc định.")
        except Exception as e:
            print(f"Lỗi khi tải API key mặc định từ config.json: {e}")
            self.API_KEY_LIST = [] # Reset về rỗng nếu có lỗi
          
    # --- Các hàm xây dựng giao diện (Build UI) ---
    def build_menus_and_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        self.action_import_word = QAction(QIcon(os.path.join(PATH_IMG, 'import.png')), "Import bài tập...", self)
        action_exit = QAction("Thoát", self)
        toolbar.addAction(self.action_import_word)
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(action_exit)
        tool_menu = menu.addMenu("&Function")
        tool_menu.addAction(self.action_import_word)
        
        # === THÊM ACTION MỚI ===
        self.action_manage_api_keys = QAction("Quản lý Gemini API...", self)
        tool_menu.addAction(self.action_manage_api_keys)
        # =======================
        
        action_exit.triggered.connect(self.close)
        
        # Thêm một khoảng trống để đẩy nút login sang phải
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # Nút Đăng nhập/Đăng xuất
        self.login_button = QPushButton("🚀 Đăng nhập")
        self.login_button.setStyleSheet("font-weight: bold; border: none; padding: 5px;")
        toolbar.addWidget(self.login_button)
        
        # === THÊM MENU TRỢ GIÚP ===
        help_menu = menu.addMenu("&Trợ giúp")
        action_about = QAction("Giới thiệu", self)
        help_menu.addAction(action_about)
        action_about.triggered.connect(self.on_about)

    def on_about(self):
        """Hiển thị hộp thoại Giới thiệu."""
        QMessageBox.about(
            self,
            "Giới thiệu Tutor AI",
            "<b>Tutor AI (PyQt Version)</b><br>"
            "Phiên bản: 2.0<br><br>"
            "Ứng dụng hỗ trợ học lập trình được chuyển đổi sang PyQt6.<br>"
            "Đơn vị phát triển: Trường Đại học Đông Á."
        )
        
    # Dán hàm này vào trong class MainWindow

    # Dán hàm này vào trong class MainWindow

    def run_gemini_in_thread(self, prompt, is_retry=False):
        """
        Tạo và chạy một thread riêng để gọi Gemini API,
        tránh làm treo giao diện người dùng.
        """
        self.thread = QThread()

        # ---- BẮT ĐẦU SỬA LỖI TẠI ĐÂY ----
        # Định nghĩa biến safe_prompt bằng chính prompt đầu vào.
        # Dòng này đã bị xóa nhầm trong quá trình dọn dẹp code trước đó.
        safe_prompt = prompt 
        # ---- KẾT THÚC SỬA LỖI ----

        # Khởi tạo Worker với model và history
        # Truyền vào `safe_prompt` đã được xử lý
        self.worker = GeminiWorker(self.model, self.history)
        self.worker.prompt = safe_prompt  # << Bây giờ dòng này sẽ hoạt động
        self.worker.was_retry = is_retry
        
        # Di chuyển worker sang thread mới
        self.worker.moveToThread(self.thread)

        # Kết nối các tín hiệu (signals)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_gemini_response)
        self.worker.error.connect(self.handle_gemini_error)
        
        # Tự động dọn dẹp thread và worker sau khi hoàn tất
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Bắt đầu thực thi thread
        self.thread.start()

    def disable_buttons(self):
        """Vô hiệu hóa các nút tương tác với AI."""
        # self.btn_run_code.setEnabled(False) # <-- XÓA HOẶC GHI CHÚ DÒNG NÀY
        self.btn_submit_code.setEnabled(False)
        self.btn_ai_help.setEnabled(False)

    def enable_buttons(self):
        """Kích hoạt lại các nút một cách thông minh dựa trên ngữ cảnh hiện tại."""
        self.btn_submit_code.setEnabled(True)
        self.btn_ai_help.setEnabled(True)

        is_runnable = False
        # Kiểm tra xem có bài tập nào đang được chọn không
        if self.current_exercise:
            # Nếu là bài tập tự do, quyết định dựa trên ComboBox
            if self.current_exercise.get('id') == 'custom_exercise':
                if self.lang_combobox.currentText() != "Không":
                    is_runnable = True
            # Nếu là bài tập theo môn học, quyết định dựa trên ngôn ngữ của môn học
            else:
                if self.current_course_language.lower() in ["c", "java", "python"]:
                    is_runnable = True

        self.btn_run_code.setEnabled(is_runnable)
    
    def on_custom_editor_load_finished(self, ok):
        """
        Khởi tạo CKEditor cho QWebEngineView ở cột bên trái (Bài tập tự do).
        Hàm này nhắm đến id="custom-editor".
        """
        if not ok or self.custom_editor_initialized:
            return

        self.custom_editor_initialized = True
        print("DEBUG: custom_editor.html đã tải. Bắt đầu tiêm CKEditor script...")

        try:
            with open(os.path.join(PATH_EDIT_TOOLS, 'ckeditor.js'), 'r', encoding='utf-8') as f:
                ckeditor_script = f.read()
        except FileNotFoundError:
            print("LỖI: Không tìm thấy file 'ckeditor.js'!")
            self.custom_editor_initialized = False
            return

        # Script này sẽ tìm đến div có id="custom-editor"
        init_script = """
            if (typeof ClassicEditor !== 'undefined') {
                ClassicEditor
                    .create( document.querySelector( '#custom-editor' ) )
                    .then( newEditor => {
                        window.customEditor = newEditor; // Lưu vào biến riêng
                        console.log( 'THÀNH CÔNG: CKEditor cho cột trái đã được khởi tạo!' );
                    } )
                    .catch( error => {
                        console.error( 'Lỗi khi khởi tạo custom editor:', error );
                    } );
            } else {
                console.error('LỖI: ClassicEditor không được định nghĩa cho custom editor.');
            }
        """
        # Chạy script để tạo editor
        self.custom_editor_view.page().runJavaScript(ckeditor_script, 
            lambda result: self.custom_editor_view.page().runJavaScript(init_script))
        
    def build_left_panel(self):
        layout = QVBoxLayout(self.fr_left)
        tabs = QTabWidget()
        tabs.setObjectName("LeftPanelTabs") 
        layout.addWidget(tabs)
        tab_custom = QWidget()
        tab_course = QWidget()
        tabs.addTab(tab_custom, "Bài tập Tự do")
        tabs.addTab(tab_course, "Bài tập theo Môn học")
        custom_layout = QVBoxLayout(tab_custom)
        custom_layout.addWidget(QLabel("Chọn ngôn ngữ lập trình (tùy chọn):"))
        self.lang_combobox = QComboBox()
        self.lang_combobox.addItems(["Không", "C", "Java", "Python"])

        # Sửa lại thành "Không" để hiển thị bộ Edittool khi khởi động
        self.lang_combobox.setCurrentText("Không") 

        custom_layout.addWidget(self.lang_combobox)
        # custom_layout.addWidget(QLabel("Nhập đề bài hoặc yêu cầu của bạn:"))
        # self.txt_custom_exercise = QTextEdit()
        # custom_layout.addWidget(self.txt_custom_exercise)
        # self.btn_start_custom = QPushButton("Bắt đầu & Hướng dẫn")
        
        custom_layout.addWidget(QLabel("Nhập đề bài hoặc yêu cầu của bạn:"))

        # --- THAY ĐỔI TẠI ĐÂY ---
        # 1. Tải file custom_editor.html
        custom_editor_path = os.path.join(PATH_EDIT_TOOLS, 'custom_editor.html')
        self.custom_editor_view.setUrl(QUrl.fromLocalFile(os.path.abspath(custom_editor_path)))
        
        # 2. Thêm QWebEngineView vào layout thay cho QTextEdit
        custom_layout.addWidget(self.custom_editor_view) 
        # --- KẾT THÚC THAY ĐỔI ---
        
        self.btn_start_custom = QPushButton("Bắt đầu & Hướng dẫn")        
        custom_layout.addWidget(self.btn_start_custom)
        self.build_course_tab(tab_course)
        
    def on_start_custom_exercise(self):
        """Xử lý khi nhấn nút "Bắt đầu" cho bài tập tự do."""
        def process_description(description):
            description = description.strip()
            if not description:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đề bài trước khi bắt đầu.")
                return

            print("Starting custom exercise...")
            
            self.current_exercise = {
                "id": "custom_exercise",
                "title": "Bài tập tự do",
                "description": description,
                "course_name": "Bài tập tự do",
                "score": INITIAL_SCORE  # Sử dụng hằng số
            }
            
            self.clear_current_editor_content()
            #self.start_new_ai_conversation(is_custom_exercise=True)

            # Xóa giao diện cũ và bắt đầu cuộc hội thoại AI mới
            self.clear_chat_interface()
            self.start_new_ai_conversation(is_custom_exercise=True)
            
            welcome_html_content = f"""
            <h3>Bắt đầu bài tập: {self.current_exercise.get('title', '')}</h3>
            <p>Hãy bắt đầu viết bài làm vào khung "Bài làm" ở giữa.</p>
            """
            
            self.add_message_to_chat(welcome_html_content, "👋 Chào mừng")
            
            # html_template = """
            # <!DOCTYPE html><html><head><meta charset="UTF-8"></head>
            # <body><div style='font-size:16px; font-family:Verdana'>{content}</div></body></html>
            # """
            # self.web_view.setHtml(html_template.format(content=welcome_html_content))
            
            self.lbl_level.setText("-")
            self.lbl_score.setText(str(INITIAL_SCORE)) # Cập nhật giao diện

        js_get_data = "window.customEditor ? window.customEditor.getData() : '';"
        self.custom_editor_view.page().runJavaScript(js_get_data, process_description)
        
    def build_course_tab(self, parent_tab):
        # Tạo layout chính cho tab này
        layout = QVBoxLayout(parent_tab)

        # 1. ComboBox chọn môn học (nằm ngoài StackedWidget)
        layout.addWidget(QLabel("Chọn môn học:"))
        self.course_combobox = QComboBox()
        layout.addWidget(self.course_combobox)

        # 2. Tạo QStackedWidget để chứa cây thư mục và chi tiết bài tập
        self.left_panel_stack = QStackedWidget()
        layout.addWidget(self.left_panel_stack, stretch=1)

        # 3. Tạo "Trang 0": Widget chứa cây thư mục
        tree_widget_container = QWidget()
        tree_layout = QVBoxLayout(tree_widget_container)
        tree_layout.setContentsMargins(0,0,0,0) # Bỏ khoảng trống thừa

        self.exercise_tree = QTreeWidget()
        self.exercise_tree.setHeaderLabels(["Buổi và tên bài", "Trạng thái", "Điểm"])
        self.exercise_tree.setColumnWidth(0, 200)
        tree_layout.addWidget(self.exercise_tree)

        # 4. Thêm trang cây thư mục vào QStackedWidget ở vị trí index 0
        self.left_panel_stack.addWidget(tree_widget_container)

    def navigate_to_next_exercise(self):
        """Finds the next exercise in the course and displays it."""
        if not self.current_exercise or not self.json_course:
            return

        current_id = self.current_exercise.get('id')
        found_current = False
        
        # Iterate through all exercises to find the next one
        for session in self.json_course.get("sessions", []):
            for exercise in session.get("exercises", []):
                if found_current:
                    # This is the exercise immediately after the current one
                    print(f"Navigating to next exercise: {exercise.get('title')}")
                    
                    # To display it, we need to find its corresponding QTreeWidget item
                    iterator = QTreeWidgetItemIterator(self.exercise_tree)
                    while iterator.value():
                        item = iterator.value()
                        item_data = item.data(0, Qt.ItemDataRole.UserRole)
                        if item_data and item_data.get('id') == exercise.get('id'):
                            # We found the tree item, now simulate a click on it
                            self.on_exercise_selected(item, 0)
                            return # Stop searching
                        iterator += 1
                    
                if exercise.get('id') == current_id:
                    found_current = True
        
        # If the loop finishes, it means we were at the last exercise
        QMessageBox.information(self, "Hoàn thành", "Chúc mừng! Bạn đã hoàn thành bài tập cuối cùng của khóa học.")
    
    # Trong class MainWindow
    def display_exercise_in_left_panel(self, exercise_data):
        """
        Tạo widget chi tiết bài tập với layout được tối ưu hóa.
        """
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        # 1. Hiển thị Tiêu đề (giữ nguyên)
        title_label = QLabel(exercise_data["title"])
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_label.setWordWrap(True)
        details_layout.addWidget(title_label)

        # 2. Hiển thị Mô tả đề bài (thay đổi tại đây)
        desc_browser = QTextBrowser()
        desc_browser.setOpenExternalLinks(True)
        description_html = exercise_data["description"].replace('\n', '<br>')
        desc_browser.setHtml(f"<p>{description_html}</p>")
        
        # --- THAY ĐỔI QUAN TRỌNG ---
        # Bỏ giới hạn chiều cao tối đa (dòng này đã bị xóa)
        # desc_browser.setMaximumHeight(200) 
        
        # Thêm stretch factor = 1 để widget này tự co giãn lấp đầy không gian
        details_layout.addWidget(desc_browser, 1) 
        # --- KẾT THÚC THAY ĐỔI ---

        # 3. Hiển thị hình ảnh (giữ nguyên)
        if "image" in exercise_data and exercise_data["image"]:
            for image_info in exercise_data["image"]:
                image_filename = image_info.get("link", "")
                image_path = os.path.join(PATH_IMG, image_filename)

                if os.path.exists(image_path):
                    image_label = ClickableLabel()
                    pixmap = QPixmap(image_path)
                    image_label.setOriginalPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_label.setCursor(Qt.CursorShape.PointingHandCursor)
                    image_label.clicked.connect(
                        lambda path=image_path: self.show_image_viewer(path)
                    )
                    
                    caption = image_info.get("image_title", "")
                    caption_label = QLabel(f'<i>{caption}</i>')
                    caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    details_layout.addWidget(image_label)
                    details_layout.addWidget(caption_label)
                else:
                    error_label = QLabel(f"<font color='red'>Lỗi: Không tìm thấy ảnh '{image_filename}'</font>")
                    details_layout.addWidget(error_label)

        # 4. Bỏ đi khoảng trống co giãn cũ (dòng này đã bị xóa)
        # details_layout.addStretch()

        # 5. Thêm các nút điều hướng (giữ nguyên)
        button_layout = QHBoxLayout()
        back_button = QPushButton("⬅ Quay lại")
        next_button = QPushButton("Bài tiếp theo ➡")
        button_layout.addWidget(back_button)
        button_layout.addStretch()
        button_layout.addWidget(next_button)
        details_layout.addLayout(button_layout)

        # Logic chuyển trang (giữ nguyên)
        new_page_index = self.left_panel_stack.addWidget(details_widget)
        self.left_panel_stack.setCurrentIndex(new_page_index)

        def go_back():
            self.left_panel_stack.setCurrentIndex(0)
            self.left_panel_stack.removeWidget(details_widget)
            details_widget.deleteLater()

        def go_to_next_exercise():
            self.navigate_to_next_exercise()

        back_button.clicked.connect(go_back)
        next_button.clicked.connect(go_to_next_exercise)

    # Thêm hàm mới này vào trong class MainWindow
    def show_image_viewer(self, image_path):
        """Mở cửa sổ ImageViewer để hiển thị ảnh được chọn."""
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy file ảnh tại:\n{image_path}")
            return
        
        # Tạo và hiển thị cửa sổ xem ảnh
        viewer = ImageViewer(image_path, self)
        viewer.exec()

    
    # THAY THẾ TOÀN BỘ HÀM build_center_panel CŨ BẰNG HÀM NÀY
    def build_center_panel(self):
        layout = QVBoxLayout(self.fr_center)
        title_label = QLabel("Bài làm")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        
        # 1. Cấu hình QScintilla Editor (THAY THẾ CHO CodeEditor)
        self.plain_code_editor = QsciScintilla()
        font = QFont("Consolas", 11) # Dùng font lập trình chuyên dụng
        self.plain_code_editor.setFont(font)
        self.plain_code_editor.setUtf8(True) # Hỗ trợ gõ tiếng Việt

        # --- CÁC TÍNH NĂNG CHUYÊN NGHIỆP ---
        # Cài đặt thụt lề (Indentation)
        self.plain_code_editor.setIndentationsUseTabs(False) # Dùng dấu cách thay cho tab
        self.plain_code_editor.setTabWidth(4)
        self.plain_code_editor.setIndentationGuides(True) # Hiển thị đường kẻ thụt lề
        self.plain_code_editor.setAutoIndent(True) # Tự động thụt lề khi xuống dòng

        # Cài đặt hiển thị số dòng (Line Numbers)
        font_metrics = QFontMetrics(font)
        self.plain_code_editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.plain_code_editor.setMarginWidth(0, font_metrics.horizontalAdvance("00000") + 6)
        self.plain_code_editor.setMarginsBackgroundColor(QColor("#f0f0f0"))

        # Tự động tô màu cặp ngoặc (Bracket Matching) - TÍNH NĂNG SỬA LỖI CỦA BẠN
        self.plain_code_editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.plain_code_editor.setMatchedBraceBackgroundColor(QColor("#a0e0e0"))   # Màu cho cặp ngoặc khớp
        self.plain_code_editor.setUnmatchedBraceBackgroundColor(QColor("#ffcccc")) # Màu cho ngoặc lỗi

        # 2. Cấu hình Rich Text Editor (CKEditor) - Giữ nguyên
        self.rich_text_editor.loadFinished.connect(self.on_editor_load_finished)
        editor_path = os.path.join(PATH_EDIT_TOOLS, 'editor.html')
        self.rich_text_editor.setUrl(QUrl.fromLocalFile(os.path.abspath(editor_path)))
        
        # 3. Thêm cả hai editor vào QStackedWidget
        self.plain_editor_index = self.editor_stack.addWidget(self.plain_code_editor)
        self.rich_editor_index = self.editor_stack.addWidget(self.rich_text_editor)
        
        layout.addWidget(title_label)
        layout.addWidget(self.editor_stack, stretch=1)
        
        # Phần các nút bấm giữ nguyên
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0,0,0,0)
        self.btn_run_code = QPushButton("▶ Chạy code")
        self.btn_submit_code = QPushButton("💬 Chấm bài & Đánh giá")
        self.btn_ai_help = QPushButton("💡 AI Giúp đỡ")
        button_layout.addWidget(self.btn_run_code)
        button_layout.addWidget(self.btn_submit_code)
        button_layout.addWidget(self.btn_ai_help)
        layout.addWidget(button_widget)

    
    def build_right_panel(self):
        layout = QVBoxLayout(self.fr_right)

        title_label = QLabel("AI Hướng dẫn")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title_label)

        self.web_view = QWebEngineView()
        # >>> KẾT NỐI TÍN HIỆU loadFinished
        self.web_view.loadFinished.connect(self.on_chat_view_loaded)
        # >>> TẢI FILE GIAO DIỆN CHAT
        chat_view_path = os.path.abspath("chat_view.html")
        self.web_view.setUrl(QUrl.fromLocalFile(chat_view_path))
        
        layout.addWidget(self.web_view, stretch=1)

        # Phần "Đánh giá" ở dưới cùng giữ nguyên
        eval_title = QLabel("Đánh giá")
        # ... (phần còn lại của hàm giữ nguyên) ...
        eval_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        eval_title.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(eval_title)
        
        eval_widget = QWidget()
        eval_layout = QGridLayout(eval_widget)
        layout.addWidget(eval_widget)
        
        eval_layout.addWidget(QLabel("Level:"), 0, 0)
        self.lbl_level = QLabel("-")
        self.lbl_level.setStyleSheet("font-weight: bold; color: blue;")
        eval_layout.addWidget(self.lbl_level, 0, 1)
        
        eval_layout.addWidget(QLabel("Score:"), 0, 2)
        self.lbl_score = QLabel("-")
        self.lbl_score.setStyleSheet("font-weight: bold; color: red;")
        eval_layout.addWidget(self.lbl_score, 0, 3)

    def toggle_login_status(self):
        """Giả lập việc đăng nhập và đăng xuất."""
        if not self.is_logged_in:
            # Giả lập đăng nhập thành công
            self.is_logged_in = True
            username = "thangtt" # Lấy tên user từ logic đăng nhập thật sau này
            self.login_button.setText(f"👤 Xin chào, {username}!")
            QMessageBox.information(self, "Đăng nhập", "Bạn đã đăng nhập thành công (giả lập).")
        else:
            # Giả lập đăng xuất
            reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn đăng xuất?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.is_logged_in = False
                self.login_button.setText("🚀 Đăng nhập / Đăng ký")
            
    def handle_login_logout(self):
        """Mở cửa sổ đăng nhập hoặc thực hiện đăng xuất."""
        if not self.is_logged_in:
            # Mở cửa sổ đăng nhập PyQt
            if not self.auth or not self.db:
                QMessageBox.critical(self, "Lỗi", "Kết nối Firebase chưa sẵn sàng.")
                return

            login_dialog = LoginDialog(self, self.auth, self.db)
            # login_dialog.exec() sẽ hiển thị cửa sổ và chờ cho đến khi nó được đóng
            if login_dialog.exec() == QDialog.DialogCode.Accepted:
                user_data = login_dialog.user_info
                
                # Cập nhật thông tin cơ bản
                self.update_user_info_callback(user_data['username'], user_data['uid'], user_data['token'])
                
                # === ĐÂY LÀ DÒNG QUAN TRỌNG ===
                # Kích hoạt việc tải API key từ Firebase cho user vừa đăng nhập
                self.update_api_key_callback(user_data['uid']) 
                # ============================
        else:
            # Logic đăng xuất (giữ nguyên)
            reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn đăng xuất?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.is_logged_in = False
                self.user_info = {}
                self.login_button.setText("🚀 Đăng nhập / Đăng ký")
                # === THÊM DÒNG NÀY ĐỂ RESET API VỀ MẶC ĐỊNH ===
                self.load_initial_data() 
                print("Đã đăng xuất và tải lại cấu hình mặc định.")
            
    # --- Các hàm logic và xử lý sự kiện (Logic and Slots) ---
    def connect_signals(self):
        self.btn_submit_code.clicked.connect(self.on_submit_code_click)
        self.btn_ai_help.clicked.connect(self.on_ai_help_click)
        self.exercise_tree.itemClicked.connect(self.on_exercise_selected)
        self.action_import_word.triggered.connect(self.on_import_word)
        self.btn_run_code.clicked.connect(self.on_run_code_click)
        self.lang_combobox.currentTextChanged.connect(self.on_custom_language_select)
        self.login_button.clicked.connect(self.handle_login_logout)
                
        # === THÊM KẾT NỐI MỚI ===
        self.action_manage_api_keys.triggered.connect(self.on_manage_api_keys)
        self.btn_start_custom.clicked.connect(self.on_start_custom_exercise)        
        self.custom_editor_view.loadFinished.connect(self.on_custom_editor_load_finished)

    def update_tree_item_score(self, exercise_id, score):
        """Chỉ cập nhật cột điểm của một item trong cây thư mục."""
        iterator = QTreeWidgetItemIterator(self.exercise_tree)
        while iterator.value():
            item = iterator.value()
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and isinstance(item_data, dict) and item_data.get('id') == exercise_id:
                item.setText(2, str(score)) # Chỉ cập nhật cột điểm
                break
            iterator += 1
            
    def on_manage_api_keys(self):
        """Mở cửa sổ quản lý API Key."""
        # API_KEY_LIST là danh sách key hiện tại đang dùng
        dialog = ApiKeyDialog(self, self.API_KEY_LIST, self.is_logged_in, self.user_info, self.db)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("API Keys đã được cập nhật.")
            # Cập nhật danh sách key và khởi tạo lại model
            self.API_KEY_LIST = dialog.saved_keys
            self.reinitialize_gemini_model()

    def load_initial_data(self):
        # === BẮT ĐẦU THÊM KHỐI CODE KHỞI TẠO FIREBASE ===
        try:
            self.firebase = pyrebase.initialize_app(firebaseConfig)
            self.auth = self.firebase.auth()
            self.db = self.firebase.database()
            print("DEBUG: Kết nối Firebase thành công.")
        except Exception as e:
            print(f"Lỗi khởi tạo Firebase: {e}")
            QMessageBox.critical(self, "Lỗi Firebase", f"Không thể kết nối đến Firebase: {e}")

        try:
            with open(os.path.join(PATH_DATA, 'rule.md'), 'r', encoding='utf-8') as f:
                self.main_rule = f.read()
            # === THÊM KHỐI CODE NÀY ===
            with open(os.path.join(PATH_DATA, 'rule_lesson.md'), 'r', encoding='utf-8') as f:
                self.main_rule_lesson = f.read()
            # ==========================
            with open(os.path.join(PATH_DATA, 'prompt.md'), 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
        except Exception as e:
            print(f"Lỗi tải các file rule hoặc prompt: {e}")
            
        try:
            with open(os.path.join(PATH_DATA, 'rule.md'), 'r', encoding='utf-8') as f:
                self.main_rule = f.read()
            # === ADD THIS BLOCK ===
            with open(os.path.join(PATH_DATA, 'prompt.md'), 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
            # ====================
        except Exception as e:
            print(f"Lỗi tải rule.md hoặc prompt.md: {e}")
        
        # 1. Tải danh sách khóa học
        self.load_all_course_data()

        # 2. Tải danh sách key mặc định
        self.load_default_api_keys()

        # 3. Tìm key hoạt động và khởi tạo model lần đầu
        self.reinitialize_gemini_model()

    def setup_ai_thread(self):
        self.thread = QThread()
        self.worker = GeminiWorker(self.model, self.history)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_gemini_response)
        self.worker.error.connect(self.handle_gemini_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

    def _ensure_context(self):
        """
        Checks if an exercise context exists. If not, and the user is in the
        Custom Exercise tab, it creates the context on the fly.
        """
        # If an exercise is already selected (from the course tab or "Start" button), do nothing.
        if self.current_exercise:
            return True

        # Check if the active tab is "Bài tập Tự do"
        if self.notebook_left.tabText(self.notebook_left.currentIndex()) == "Bài tập Tự do":
            description = self.txt_custom_exercise.toPlainText().strip()
            if not description:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đề bài trong tab 'Bài tập Tự do' trước.")
                return False
            
            # Automatically create the "virtual exercise" context
            self.current_exercise = {
                "id": "custom_exercise",
                "title": "Bài tập tự do",
                "description": description,
                "course_name": "Bài tập tự do"
            }
            
            # Automatically get the language from the combobox
            selected_lang_text = self.lang_combobox.currentText()
            lang_map = {"C": "c", "Java": "java", "Python": "python", "Không": "text"}
            self.current_exercise_language = lang_map.get(selected_lang_text, "text")
            
            # Start a new AI conversation session
            self.start_new_ai_conversation()
            
            return True
        
        # If no context can be found, show a general error
        QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một bài tập hoặc bắt đầu một bài tập tự do.")
        return False
    
    # THAY THẾ TOÀN BỘ HÀM on_submit_code_click CŨ BẰNG HÀM NÀY

    def on_submit_code_click(self):
        """Xử lý khi người dùng nhấn nút Chấm bài & Đánh giá."""
        def process_submission(user_content):
            if not self.current_exercise or not user_content.strip():
                if not self.current_exercise:
                    QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một bài tập trước.")
                else:
                    QMessageBox.warning(self, "Thông báo", "Vui lòng nhập bài làm trước khi nộp.")
                self.enable_buttons()
                return

            # Chỉ lấy điểm hiện tại và gửi đi, KHÔNG CỘNG/TRỪ gì cả.
            current_score = self.current_exercise.get('score', 10)
            course_name = self.json_course.get('course_name', 'Không xác định') if self.json_course else 'Bài tập tự do'
            
            grading_instructions = (
                f"Phân tích và đánh giá bài làm của người học dưới đây. "
                f"**Tuyệt đối KHÔNG ĐƯỢC đưa ra đáp án đúng.** "
                f"Thay vào đó, hãy đặt câu hỏi gợi mở để người học tự suy nghĩ và tìm ra lỗi sai."
            )
            student_submission_block = (
                f"# Bài làm của người học:\n"
                f"```{self.current_exercise_language}\n{user_content}\n```\n"
            )
            
            full_prompt = self.prompt_template.format(
                exercise_context=(
                    f"Môn học: {course_name}\n"
                    f"Bài tập: {self.current_exercise.get('title', 'N/A')}\n"
                    f"Đề bài: {self.current_exercise.get('description', 'N/A')}\n"
                ),
                current_score=current_score+1,
                step_by_step_guidance=grading_instructions,
                student_submission=student_submission_block
            )

            lang = self.current_course_language.lower()
            rule_base = self.main_rule_lesson if (self.current_exercise.get('id') == 'custom_exercise' or lang not in ["c", "java", "python"]) else self.main_rule
            final_prompt = create_main_rule(rule_base, full_prompt, course_name, self.current_exercise_language)
            
            self.run_gemini_in_thread(final_prompt)

        self.disable_buttons()
        self.get_current_editor_content(process_submission)
        
    # Tìm đến hàm này trong class MainWindow

    def start_new_ai_conversation(self, is_custom_exercise=False):
        """
        Xóa lịch sử cũ và thiết lập một cuộc hội thoại mới với bộ quy tắc đã được xử lý.
        """
        self.history.clear()
        
        # ---- BẮT ĐẦU SỬA LỖI TẠI ĐÂY ----
        # XÓA HOẶC GHI CHÚ DÒNG NÀY LẠI. Nó thuộc về hệ thống hiển thị cũ.
        # self.conversation_display_history.clear() 
        # ---- KẾT THÚC SỬA LỖI ----
        
        initial_prompt = ""
        
        if is_custom_exercise:
            # Đối với bài tập tự do, sử dụng rule_lesson.md
            lang = self.current_exercise_language if self.current_exercise_language != "text" else "chung"
            initial_prompt = self.main_rule_lesson.replace('{language_placeholder}', lang)
        elif self.json_course:
            # Đối với bài tập môn học, sử dụng rule.md
            course_name = self.json_course.get('course_name', 'Không xác định')
            course_lang = self.json_course.get('course_language', 'Không xác định')
            # Dùng hàm create_main_rule để điền thông tin vào rule.md
            # Lưu ý: tham số thứ hai (prompt) ta để rỗng vì đây chỉ là bước khởi tạo rule.
            initial_prompt = create_main_rule(self.main_rule, "", course_name, course_lang)

        if initial_prompt:
            initial_context = [
                {'role': 'user', 'parts': [initial_prompt]},
                {'role': 'model', 'parts': ["OK, tôi đã hiểu vai trò của mình và sẵn sàng hướng dẫn."]}
            ]
            self.history.extend(initial_context)
            print("DEBUG: Đã thiết lập vai trò Tutor AI vào lịch sử hội thoại.")
            
    # In app_pyqt_working.py, replace the entire on_ai_help_click function with this one.

    def on_ai_help_click(self):
        """
        Handles when the user clicks the AI Help button.
        This version removes the faulty string replacement that broke the prompt.
        """
        def process_help_request(user_content):
            if not self.current_exercise:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một bài tập trước.")
                self.enable_buttons()
                return

            # Score reduction logic
            if self.current_exercise.get('score', 0) > 0:
                self.current_exercise['score'] -= 1
            current_score = self.current_exercise.get('score', 0)
            
            # Update UI immediately
            self.lbl_score.setText(str(current_score))
            if self.current_exercise.get('id') != 'custom_exercise':
                self.update_tree_item_score(self.current_exercise.get('id'), str(current_score))
                
            course_name = self.json_course.get('course_name', 'Không xác định') if self.json_course else 'Bài tập tự do'
            
            guidance = self.current_exercise.get("guidance") or self.current_exercise.get("generated_guidance")
            
            guidance_prompt_block = ""
            base_guidance_instruction = "USER_REQUESTS_HELP\n\n"

            if guidance:
                # SCENARIO 1: Guidance exists
                print("DEBUG: Guidance found, asking AI to summarize based on existing steps.")
                # --- START OF FIX ---
                # The original guidance steps already contain newlines.
                # We join them with a newline character here to create a clean, multi-line string.
                formatted_guidance = "\n".join([f"{i+1}. {step}" for i, step in enumerate(guidance)])
                # The line below that replaced '\n' with '\\n' was incorrect and has been removed.
                # --- END OF FIX ---
                
                if user_content.strip():
                    guidance_prompt_block = (
                        base_guidance_instruction +
                        f"Dưới đây là các bước hướng dẫn giải bài tập này:\n{formatted_guidance}\n\n"
                        f"Dựa vào bài làm hiện tại của người học và các bước hướng dẫn trên, hãy đưa ra một gợi ý nhỏ "
                        f"hoặc đặt câu hỏi để giúp họ tiến tới bước tiếp theo. "
                        f"Tuyệt đối không viết code đáp án và không nhắc lại đề bài."
                    )
                else:
                    guidance_prompt_block = (
                        base_guidance_instruction +
                        f"**Nhiệm vụ của bạn là diễn giải lại các bước hướng dẫn đã có sẵn dưới đây một cách tổng quan cho người mới bắt đầu. TUYỆT ĐỐI KHÔNG TẠO RA CÁC BƯỚC MỚI.**\n\n"
                        f"**Các bước hướng dẫn có sẵn:**\n{formatted_guidance}\n\n"
                        f"**Yêu cầu:**\n"
                        f"- Bắt đầu phản hồi trực tiếp bằng mục 'Hướng dẫn tổng quát'.\n"
                        f"- Diễn giải lại các bước trên bằng ngôn ngữ thân thiện, dễ hiểu, mỗi bước trên một dòng riêng biệt.\n"
                        f"- Không đưa ra code đáp án và không nhắc lại đề bài."
                    )
            else:
                # SCENARIO 2: No guidance exists
                print("DEBUG: No guidance found, asking AI to generate smart steps.")
                self.is_awaiting_guidance = True
                guidance_prompt_block = (
                    base_guidance_instruction +
                    f"Bài tập này chưa có các bước hướng dẫn chi tiết. Nhiệm vụ của bạn là:\n"
                    f"1. Phân tích đề bài và tự tạo ra một danh sách các bước hướng dẫn chung nhất, KHÔNG được đưa ra lời giải.\n"
                    f"2. Trình bày các bước đó trong trường 'data' theo đúng định dạng Markdown sau:\n"
                    f"   - Bắt đầu trực tiếp bằng mục 'Hướng dẫn' (`**Hướng dẫn:**`).\n"
                    f"   - Liệt kê các bước dưới dạng một danh sách có thứ tự (numbered list) của Markdown. Quan trọng: Mỗi bước phải bắt đầu trên một dòng mới.\n"
                    f"3. Trong trường 'info' của JSON, BẮT BUỘC phải có khóa 'generated_steps' chứa một MẢNG các chuỗi string, mỗi chuỗi là một bước hướng dẫn."
                )

            student_submission_prompt = f"# Bài làm hiện tại của người học:\n```{self.current_exercise_language}\n{user_content}\n```" if user_content.strip() else ""
            
            full_prompt = self.prompt_template.format(
                exercise_context=(
                    f"Môn học: {course_name}\n"
                    f"Bài tập: {self.current_exercise.get('title', 'N/A')}\n"
                    f"Đề bài: {self.current_exercise.get('description', 'N/A')}\n"
                ),
                current_score=current_score,
                step_by_step_guidance=guidance_prompt_block,
                student_submission=student_submission_prompt
            )
            
            lang = self.current_course_language.lower()
            rule_base = self.main_rule_lesson if (self.current_exercise.get('id') == 'custom_exercise' or lang not in ["c", "java", "python"]) else self.main_rule
            final_prompt = create_main_rule(rule_base, full_prompt, course_name, self.current_exercise_language)
            
            self.run_gemini_in_thread(final_prompt)

        self.disable_buttons()
        self.get_current_editor_content(process_help_request)
        
    def on_editor_load_finished(self, ok):
        """
        Hàm này được gọi khi editor.html đã tải xong trong QWebEngineView.
        Nó sẽ "tiêm" mã nguồn CKEditor vào trang một cách tuần tự và an toàn.
        Sử dụng cờ self.editor_initialized để đảm bảo chỉ chạy một lần.
        """
        # --- THÊM LOGIC KIỂM TRA CỜ TẠI ĐÂY ---
        if not ok or self.editor_initialized:
            return # Thoát ngay nếu trang tải lỗi hoặc editor đã được tạo

        # Đặt cờ thành True để ngăn việc chạy lại
        self.editor_initialized = True
        # --- KẾT THÚC THAY ĐỔI ---

        print("DEBUG: editor.html đã tải. Bắt đầu tiêm CKEditor script...")

        try:
            with open(os.path.join("editTools", 'ckeditor.js'), 'r', encoding='utf-8') as f:
                ckeditor_script = f.read()
        except FileNotFoundError:
            print("LỖI: Không tìm thấy file 'ckeditor.js' trong thư mục editTools!")
            # Reset cờ nếu có lỗi để có thể thử lại ở lần tải trang sau (nếu có)
            self.editor_initialized = False 
            return

        init_script = """
            if (typeof ClassicEditor !== 'undefined') {
                ClassicEditor
                    .create( document.querySelector( '#editor' ), { language: 'vi' } )
                    .then( newEditor => {
                        window.editor = newEditor;
                        console.log( 'THÀNH CÔNG: CKEditor đã được khởi tạo!' );
                    } )
                    .catch( error => {
                        console.error( 'Lỗi khi khởi tạo editor:', error );
                    } );
            } else {
                console.error('LỖI KIỂM TRA: ClassicEditor không được định nghĩa.');
            }
        """
        self.rich_text_editor.page().runJavaScript(ckeditor_script, 
            lambda result: self.rich_text_editor.page().runJavaScript(init_script))
        
    def reset_and_clear_context(self):
        print("DEBUG: Đang reset và làm mới ngữ cảnh...")
        self.current_exercise = None
        self.is_awaiting_guidance = False
        self.current_exercise_index = -1
        self.history.clear()

        # Dọn dẹp các ô nhập liệu và hiển thị
        self.clear_current_editor_content()
        self.clear_chat_interface() # << THAY ĐỔI CHÍNH

        self.lbl_level.setText("-")
        self.lbl_score.setText("-")
        if hasattr(self, 'left_panel_stack'):
            self.left_panel_stack.setCurrentIndex(0)
            
    def handle_gemini_response(self, response_text, was_retry):
        # Luôn hiển thị phản hồi thô từ AI để debug
        print("DEBUG: Raw AI Response Received:\n", response_text)

        # Thử phân tích phản hồi
        raw_markdown, info, err = render_ai_json_markdown(response_text)

        if err:
            # Nếu có lỗi phân tích, chỉ hiển thị thông báo lỗi
            error_message = f"""
            <h3>⚠️ Lỗi Phân Tích Phản Hồi</h3>
            <p>AI đã trả về một phản hồi không đúng định dạng thẻ [START_DATA]...[END_INFO].</p>
            <p><b>Phản hồi gốc:</b></p>
            <pre>{html.escape(response_text)}</pre>
            """
            # Gửi Markdown thô (đã escape) để hàm JS không báo lỗi
            self.add_message_to_chat(error_message, "Lỗi Hệ thống")
        else:
            # Nếu không có lỗi, gửi Markdown thô cho JavaScript xử lý
            self.add_message_to_chat(raw_markdown, "💬 Tutor AI")

            # --- Logic cập nhật trạng thái chỉ chạy khi phân tích thành công ---
            # Xử lý logic tạo hướng dẫn (nếu có)
            if hasattr(self, 'is_awaiting_guidance') and self.is_awaiting_guidance:
                generated_steps = info.get("generated_steps")
                if generated_steps and isinstance(generated_steps, list):
                    if self.current_exercise:
                        self.current_exercise['generated_guidance'] = generated_steps
                        print(f"DEBUG: Đã lưu {len(generated_steps)} bước hướng dẫn do AI tạo.")
                self.is_awaiting_guidance = False

            # Cập nhật Level và Score
            self.lbl_level.setText(str(info.get('level', '-')))
            new_score = info.get('score')
            if new_score is not None and self.current_exercise:
                try:
                    self.current_exercise['score'] = int(new_score)
                    print(f"DEBUG: Điểm số nội bộ của bài tập '{self.current_exercise.get('title')}' đã được cập nhật thành {self.current_exercise['score']}.")
                except (ValueError, TypeError):
                    print(f"CẢNH BÁO: AI trả về điểm số không hợp lệ: {new_score}")

            if self.current_exercise:
                current_score_str = str(self.current_exercise.get('score', '-'))
                self.lbl_score.setText(current_score_str)
                if self.current_exercise.get('id') != 'custom_exercise':
                    status = "✓" if info.get('exercise_status') == 'completed' else "✗"
                    self.update_tree_item(self.current_exercise.get('id'), status, current_score_str)
            else:
                self.lbl_score.setText(str(info.get('score', '-')))

        # Kích hoạt lại các nút bấm
        self.enable_buttons()
        
    def on_run_code_click(self):
        """Xử lý khi người dùng nhấn nút Chạy code."""
    
        def run_code_process(content):
            # ... (Phần code lấy nội dung từ editor giữ nguyên)
            if self.editor_stack.currentIndex() == self.rich_editor_index:
                temp_doc = QTextDocument()
                temp_doc.setHtml(content)
                code = temp_doc.toPlainText().strip()
            else:
                code = content.strip()

            if not code:
                QMessageBox.information(self, "Thông báo", "Vui lòng nhập code để chạy.")
                self.enable_buttons()
                return

            # --- BẮT ĐẦU SỬA LỖI ---
            # Tự động xác định ngôn ngữ dựa trên ngữ cảnh
            language = ""
            # Nếu đang có một bài tập của môn học được chọn
            if self.current_exercise and self.current_exercise.get('id') != 'custom_exercise':
                language = self.current_course_language.lower()
            # Nếu không, đây là bài tập tự do, lấy ngôn ngữ từ combobox
            else:
                language = self.current_exercise_language.lower()
            # --- KẾT THÚC SỬA LỖI ---

            if language not in ["c", "java", "python"]:
                QMessageBox.information(self, "Thông báo", f"Chức năng chạy code không hỗ trợ cho ngôn ngữ '{language}'.")
                self.enable_buttons()
                return

            result = ""
            if language == "c": result = compile_code(code)
            elif language == "java": result = compile_java(code)
            elif language == "python": result = run_python(code)
            
            # html_result = f"<h3>Kết quả thực thi:</h3><pre>{html.escape(result)}</pre>"
            # self.web_view.setHtml(html_result)
            # self.enable_buttons()
            
            # Thay vì setHtml, hãy thêm kết quả vào chat
            html_result = f"<pre>{html.escape(result)}</pre>"
            self.add_message_to_chat(html_result, "⚙️ Kết quả thực thi")
            self.enable_buttons()

        self.disable_buttons()
        self.get_current_editor_content(run_code_process)

    # THAY THẾ TOÀN BỘ HÀM handle_gemini_response CŨ BẰNG HÀM NÀY
    
    def update_tree_item(self, exercise_id, status, score):
        """Tìm và cập nhật một item trong QTreeWidget dựa trên exercise_id."""
        iterator = QTreeWidgetItemIterator(self.exercise_tree)
        while iterator.value():
            item = iterator.value()
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and isinstance(item_data, dict) and item_data.get('id') == exercise_id:
                item.setText(1, status) # Cập nhật cột trạng thái
                item.setText(2, score)  # Cập nhật cột điểm
                # Cập nhật lại dữ liệu ẩn
                item_data['status'] = status
                item_data['score'] = int(score)
                item.setData(0, Qt.ItemDataRole.UserRole, item_data)
                break # Dừng lại khi đã tìm thấy
            iterator += 1
            
    # Thay thế hàm cũ bằng hàm này

    def handle_gemini_error(self, error_text):
        error_html = f"<h3>Lỗi hệ thống từ Gemini</h3><pre>{html.escape(error_text)}</pre>"
        self.add_message_to_chat(error_html, "❌ Lỗi AI")
        self.enable_buttons() # Kích hoạt lại các nút
        
    # THAY THẾ TOÀN BỘ HÀM on_exercise_selected CŨ BẰNG HÀM NÀY

    # THAY THẾ TOÀN BỘ HÀM on_exercise_selected CŨ BẰNG HÀM NÀY
    def on_exercise_selected(self, item, column):
        """
        Được gọi khi một mục trên cây thư mục được click.
        """
        exercise_data = item.data(0, Qt.ItemDataRole.UserRole)
        parent_item = item.parent()
        if not exercise_data or not isinstance(exercise_data, dict) or not parent_item:
            self.current_exercise = None
            self.current_session_index = -1
            self.current_exercise_index = -1
            return

        self.current_session_index = self.exercise_tree.indexOfTopLevelItem(parent_item)
        self.current_exercise_index = parent_item.indexOfChild(item)
        
        self.current_exercise = exercise_data

        # Luôn bắt đầu bài tập với điểm số mới, không dùng điểm cũ từ file JSON
        self.current_exercise['score'] = INITIAL_SCORE
        # Cập nhật lại dữ liệu điểm trong cây thư mục
        item.setText(2, str(INITIAL_SCORE))
        item.setData(0, Qt.ItemDataRole.UserRole, self.current_exercise)
        
        language = self.current_course_language.lower()
        is_programming_lang = language in ["c", "java", "python"]

        # Cập nhật các nút và hiển thị
        self.btn_run_code.setEnabled(is_programming_lang)
        self.display_exercise_in_left_panel(exercise_data)
        self.clear_current_editor_content()
        #self.start_new_ai_conversation(is_custom_exercise=False) 

        # Xóa giao diện cũ và bắt đầu cuộc hội thoại AI mới
        self.clear_chat_interface()
        self.start_new_ai_conversation(is_custom_exercise=False)

        # Hiển thị thông điệp chào mừng
        welcome_html_content = f"""
        <h3>Bắt đầu bài tập: {self.current_exercise.get('title', '')}</h3>
        <p>Đề bài đã được hiển thị ở khung bên trái.</p>
        <p>Hãy bắt đầu viết code/bài làm của bạn vào khung "Bài làm" ở giữa.</p>
        """
        self.add_message_to_chat(welcome_html_content, "👋 Chào mừng")
        # html_template = """
        # <!DOCTYPE html><html><head><meta charset="UTF-8"><title>AI Response</title>
        # </head>
        # <body><div style='font-size:16px; font-family:Verdana'>{content}</div></body></html>
        # """
        # full_html = html_template.format(content=welcome_html_content)
        # self.web_view.setHtml(full_html)
        self.lbl_level.setText("-")
        self.lbl_score.setText(str(exercise_data.get('score', '-')))

        # Chuyển đổi editor và kích hoạt tô màu cú pháp
        if is_programming_lang:
            self.editor_stack.setCurrentIndex(self.plain_editor_index)
            
            lexer = None
            if language == 'python':
                lexer = QsciLexerPython()
            elif language == 'java':
                lexer = QsciLexerJava()
            elif language == 'c':
                lexer = QsciLexerCPP()
            
            if lexer:
                lexer.setDefaultFont(self.plain_code_editor.font())
                self.plain_code_editor.setLexer(lexer)
        else:
            self.editor_stack.setCurrentIndex(self.rich_editor_index)
            self.plain_code_editor.setLexer(None) # Tắt tô màu
            self.editor_initialized = False
            self.rich_text_editor.reload()

    # THAY THẾ TOÀN BỘ HÀM get_current_editor_content CŨ BẰNG HÀM NÀY
    def get_current_editor_content(self, callback):
        """
        Hàm hợp nhất để lấy nội dung từ editor đang hoạt động.
        'callback' là hàm sẽ được gọi với nội dung trả về.
        """
        current_index = self.editor_stack.currentIndex()
        
        if current_index == self.plain_editor_index:
            # --- SỬA LỖI TẠI ĐÂY ---
            # QsciScintilla dùng phương thức .text() thay vì .toPlainText()
            content = self.plain_code_editor.text()
            callback(content)
            # --- KẾT THÚC SỬA LỖI ---
        elif current_index == self.rich_editor_index:
            # Editor là QWebEngineView, dùng JavaScript bất đồng bộ
            js_code = "window.editor ? window.editor.getData() : '';"
            self.rich_text_editor.page().runJavaScript(js_code, callback)
            
    def clear_current_editor_content(self):
        """Hàm hợp nhất để xóa nội dung của editor đang hoạt động."""
        current_index = self.editor_stack.currentIndex()
        
        if current_index == self.plain_editor_index:
            self.plain_code_editor.clear()
        elif current_index == self.rich_editor_index:
            js_code = "if (window.editor) { window.editor.setData(''); }"
            self.rich_text_editor.page().runJavaScript(js_code)
            
    # THAY THẾ TOÀN BỘ HÀM on_custom_language_select CŨ BẰNG HÀM NÀY
    def on_custom_language_select(self, text):
        lang_map = {"C": "c", "Java": "java", "Python": "python", "Không": "text"}
        lang_code = lang_map.get(text, "text")
        self.current_exercise_language = lang_code
        print(f"Ngôn ngữ tùy chọn đã đổi thành: {lang_code}")

        if text == "Không":
            self.editor_stack.setCurrentIndex(self.rich_editor_index)
            self.btn_run_code.setEnabled(False)
            print("DEBUG: Đã chuyển sang Rich Text Editor.")
        else:
            self.editor_stack.setCurrentIndex(self.plain_editor_index)
            self.btn_run_code.setEnabled(True)
            
            # KÍCH HOẠT TÔ MÀU CÚ PHÁP BẰNG LEXER CỦA QSCINTILLA
            lexer = None
            if lang_code == 'python':
                lexer = QsciLexerPython()
            elif lang_code == 'java':
                lexer = QsciLexerJava()
            elif lang_code == 'c':
                # QsciLexerCPP dùng cho cả C và C++
                lexer = QsciLexerCPP()
            
            if lexer:
                lexer.setDefaultFont(self.plain_code_editor.font())
                self.plain_code_editor.setLexer(lexer)
            else:
                self.plain_code_editor.setLexer(None) # Tắt tô màu nếu không phải ngôn ngữ lập trình

            print(f"DEBUG: Đã chuyển sang Plain Text Editor với tô màu cho {lang_code}.")
            
    def on_import_word(self):
        """Mở hộp thoại file, xử lý import từ DOCX và làm mới danh sách."""
        # Mở hộp thoại chọn file của PyQt
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file Word để import",
            "", # Thư mục bắt đầu
            "Word Documents (*.docx);;All files (*.*)"
        )

        if not file_path:
            return # Người dùng đã hủy

        success, message = process_docx_to_json(file_path, PATH_DATA)

        if success:
            # Dùng QMessageBox của PyQt để hiển thị thông báo
            QMessageBox.information(self, "Thành công", f"Đã import thành công và lưu tại:\n{message}")
            # Làm mới lại danh sách môn học trên giao diện
            self.load_all_course_data()
        else:
            QMessageBox.critical(self, "Lỗi Import", f"Không thể import file:\n{message}")

    def load_all_course_data(self):
        self.COURSE_FILE_MAP.clear()
        course_files = glob.glob(os.path.join(PATH_DATA, 'course_*.json'))
        for file_path in course_files:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    course_name = json.load(file).get("course_name")
                    if course_name: self.COURSE_FILE_MAP[course_name] = file_path
            except Exception as e: print(f"Lỗi khi quét file course {file_path}: {e}")
        available_courses = list(self.COURSE_FILE_MAP.keys())
        self.course_combobox.clear()

        # Tạm ngắt kết nối tín hiệu để tránh gọi 2 lần không cần thiết
        try: 
            self.course_combobox.currentTextChanged.disconnect(self.on_course_select)
        except TypeError: 
            pass # Bỏ qua nếu chưa có kết nối nào

        self.course_combobox.addItems(available_courses)
        
        # THAY ĐỔI BẮT ĐẦU TỪ ĐÂY
        if available_courses:
            first_course = available_courses[0]
            self.course_combobox.setCurrentText(first_course)
            # Chủ động gọi hàm xử lý cho môn học đầu tiên
            self.on_course_select(first_course) 
        # KẾT THÚC THAY ĐỔI

        # Kết nối lại tín hiệu để người dùng có thể chọn các môn khác
        self.course_combobox.currentTextChanged.connect(self.on_course_select)

    def on_course_select(self, course_name):
        self.reset_and_clear_context()
        file_path = self.COURSE_FILE_MAP.get(course_name)
        if not file_path: return
        try:
            with open(file_path, "r", encoding="utf-8") as file: self.json_course = json.load(file)
            self.current_course_language = self.json_course.get("course_language", "text").lower()
            self.current_exercise_language = self.current_course_language
            self.populate_tree(self.json_course)
        except Exception as e:
            print(f"Lỗi khi tải môn học {course_name}: {e}")
            self.exercise_tree.clear()

    def populate_tree(self, course_data):
        self.exercise_tree.clear()
        for session in course_data.get("sessions", []):
            session_item = QTreeWidgetItem(self.exercise_tree)
            session_item.setText(0, session.get("title", "Unknown Session"))
            for ex in session.get("exercises", []):
                exercise_item = QTreeWidgetItem(session_item)
                exercise_item.setText(0, ex.get("title", "Unknown Exercise"))
                exercise_item.setText(1, ex.get("status", "✗"))
                exercise_item.setText(2, str(ex.get("score", 0)))
                exercise_item.setData(0, Qt.ItemDataRole.UserRole, ex)
        self.exercise_tree.expandAll()

def json_sessions_to_markdown(data, session_idx, exercise_idx):
    """
    Trích xuất và định dạng thông tin của một bài tập cụ thể thành Markdown.
    """
    markdown_lines = []
    try:
        session = data['sessions'][session_idx]
        exercise = session['exercises'][exercise_idx]
        
        markdown_lines.append(f"## {session.get('title', '')}")
        markdown_lines.append(f"### {exercise.get('title', '')}")
        
        description = exercise.get('description', '')
        if description:
            markdown_lines.append("\n**Đề bài:**")
            markdown_lines.append(description)

        guidance = exercise.get('guidance', [])
        if guidance:
            markdown_lines.append("\n**Các bước hướng dẫn:**")
            for step in guidance:
                markdown_lines.append(f"- {step}")
        
        return "\n".join(markdown_lines)
    except (IndexError, KeyError) as e:
        print(f"Lỗi khi trích xuất markdown cho bài tập: {e}")
        return ""
    
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # --- KÍCH HOẠT BỘ XỬ LÝ LỖI TOÀN CỤC ---
    sys.excepthook = global_exception_handler
    # ----------------------------------------

    window = MainWindow()
    window.show()
    sys.exit(app.exec())