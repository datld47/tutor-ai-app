import sys
import os
import glob
import json
import re
import markdown

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
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView

# --- Import các file logic ---
from usercustomize import PATH_IMG, PATH_DATA
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

# --- Hàm xử lý Markdown ---
# def render_ai_json_markdown(response_text: str):
#     match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, flags=re.DOTALL)
#     if match: json_str = match.group(1)
#     else: json_str = response_text.strip()
#     try:
#         obj = json.loads(json_str)
#         markdown_text = obj["data"]
#         protected_text = markdown_text.replace('\\(', '@@INLINE_MATH_START@@').replace('\\)', '@@INLINE_MATH_END@@')
#         protected_text = protected_text.replace('\\[', '@@DISPLAY_MATH_START@@').replace('\\]', '@@DISPLAY_MATH_END@@')
#         html = markdown.markdown(protected_text, extensions=["fenced_code", "sane_lists"])
#         html = html.replace('@@INLINE_MATH_START@@', '\\(').replace('@@INLINE_MATH_END@@', '\\)')
#         html = html.replace('@@DISPLAY_MATH_START@@', '\\[').replace('@@DISPLAY_MATH_END@@', '\\]')
#         return html, obj.get('info', {}), None
#     except Exception as err:
#         return f"<pre>{response_text}</pre>", {}, err

# Replace the old function with this new, more robust version
def render_ai_json_markdown(response_text: str):
    print ("response_text: ", response_text)
    """
    Lấy văn bản gốc từ phản hồi JSON của AI và chuyển đổi nó sang định dạng HTML
    cơ bản bằng cách thay thế các ký tự xuống dòng.
    """
    try:
        # Bước 1: Trích xuất khối JSON từ phản hồi (giữ nguyên)
        match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, flags=re.DOTALL)
        json_str = match.group(1) if match else response_text.strip()

        obj = json.loads(json_str)
        data_text = obj.get("data", "")
        info = obj.get("info", {})

        # Bước 2: Chuyển đổi văn bản sang HTML an toàn
        # - html.escape() để các ký tự như '<' không bị lỗi
        # - replace('\n', '<br>') để xuống dòng chính xác
        final_html = html.escape(data_text).replace('\n', '<br>')

        # Các công thức MathJax như \(...\) sẽ không bị ảnh hưởng bởi quá trình này

        return final_html, info, None

    except json.JSONDecodeError as json_err:
        # Phần xử lý lỗi giữ nguyên như cũ
        print(f"--- LỖI PHÂN TÍCH JSON ---")
        print(f"Lỗi: Không thể phân tích JSON. Lỗi: {json_err}")
        error_html = (f"<h3>Lỗi Phân Tích Phản Hồi AI</h3>"
                      f"<p>Không thể đọc định dạng JSON. Vui lòng thử lại.</p>"
                      f"<b>Phản hồi gốc:</b><pre>{response_text}</pre>")
        return error_html, {}, str(json_err)

    except Exception as err:
        print(f"--- LỖI KHÔNG MONG MUỐN trong render_ai_json_markdown ---")
        return f"<pre>Lỗi không mong muốn: {err}</pre>", {}, str(err)

# --- Lớp Worker cho Thread ---
# class GeminiWorker(QObject):
#     #finished = pyqtSignal(str)
#     finished = pyqtSignal(str, bool)
#     error = pyqtSignal(str)
#     def __init__(self, model, history):
#         super().__init__()
#         self.model = model
#         self.history = history
#         self.prompt = ""
#         self.was_retry = False
#     def run(self):
#         try:
#             message = [{'role': 'user', 'parts': [self.prompt]}]
#             self.history.extend(message)
#             response = self.model.generate_content(self.history)
            
#             # === BẮT ĐẦU PHIÊN BẢN SỬA LỖI NÂNG CAO ===
            
#             # 1. Lấy văn bản gốc từ AI
#             original_text = response.text
            
#             # 2. Định nghĩa một hàm nhỏ để thêm dấu '\' vào phía trước chuỗi tìm thấy
#             def escape_mathjax_delimiters(match):
#                 # match.group(0) là toàn bộ chuỗi khớp với mẫu (ví dụ: '\(')
#                 # Chúng ta trả về một chuỗi mới với một dấu '\' được thêm vào trước
#                 return '\\' + match.group(0)

#             # 3. Mẫu regex để tìm chính xác các delimiter của MathJax
#             #    - \\( và \\) : Tìm chuỗi '\(' và '\)'
#             #    - \\\[ và \\\] : Tìm chuỗi '\[' và '\]'
#             #    Dấu | có nghĩa là "hoặc"
#             pattern = r'\\\(|\\\)|\\\[|\\\]'
            
#             # 4. Sử dụng re.sub() để tìm và thay thế một cách thông minh
#             #    Nó sẽ áp dụng hàm escape_mathjax_delimiters cho mỗi lần tìm thấy
#             safe_response_text = re.sub(pattern, escape_mathjax_delimiters, original_text)
        
#             self.history.append({'role': 'model', 'parts': [original_text]})
            
#             # << SỬA LẠI: Gửi đi cả 2 tham số
#             self.finished.emit(safe_response_text, self.was_retry) 
#         except Exception as e:
#             self.error.emit(str(e))

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
            self.history.extend(message)
            
            response = self.model.generate_content(self.history)
            original_text = response.text
            
            # === GIẢI PHÁP TỐI ƯU VÀ TOÀN DIỆN ===
            # Thay thế TẤT CẢ các ký tự '\' đơn bằng '\\' kép.
            # Cách này xử lý được mọi trường hợp LaTeX (\(, \frac, \sqrt, ...)
            # mà không cần dùng regex phức tạp.
            #safe_response_text = original_text.replace('\\', '\\\\')
            # === BỎ XỬ LÝ THAY THẾ, DÙNG TRỰC TIẾP PHẢN HỒI GỐC ===
            safe_response_text = original_text
            # =======================================

            self.history.append({'role': 'model', 'parts': [original_text]})
            self.finished.emit(safe_response_text, self.was_retry)

        except Exception as e:
            self.error.emit(str(e))
            
# --- Lớp Cửa sổ Chính ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutor AI (PyQt Version)")
        self.setGeometry(100, 100, 1600, 900)

        # --- Các biến trạng thái ---
        self.COURSE_FILE_MAP = {}
        self.json_course = None
        self.current_exercise = None
        self.model = None 
        self.history = []
        self.main_rule = ""
        self.main_rule_lesson = ""
        self.prompt_template = ""
        self.current_course_language = "text"
        self.current_exercise_language = "text"
        
        self.API_KEY_LIST = []
        self.API_KEY = ""
        
        # --- Xây dựng giao diện ---
        self.build_menus_and_toolbar()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        self.fr_left = QWidget()
        self.fr_center = QWidget()
        self.fr_right = QWidget()
        splitter.addWidget(self.fr_left)
        splitter.addWidget(self.fr_center)
        splitter.addWidget(self.fr_right)
        splitter.setSizes([400, 800, 400])
        self.build_left_panel()
        self.build_center_panel()
        self.build_right_panel()
        
        # --- Các biến trạng thái cho Firebase ---
        self.firebase = None
        self.auth = None
        self.db = None
        self.user_info = {} # Lưu thông tin người dùng (uid, token, username)
        
        # --- Thiết lập logic nền và kết nối sự kiện ---
        self.connect_signals()
        self.load_initial_data()
        
        # === THÊM DÒNG NÀY ĐỂ PHÓNG TO CỬA SỔ ===
        self.showMaximized()
        
        self.is_logged_in = False # Thêm biến trạng thái đăng nhập
        
        # === THÊM CÁC BIẾN NÀY ĐỂ LƯU VỊ TRÍ ===
        self.current_session_index = -1
        self.current_exercise_index = -1

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
        self.login_button = QPushButton("🚀 Đăng nhập / Đăng ký")
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
        custom_layout.addWidget(QLabel("Chọn ngôn ngữ (tùy chọn):"))
        self.lang_combobox = QComboBox()
        self.lang_combobox.addItems(["Không", "C", "Java", "Python"])
        custom_layout.addWidget(self.lang_combobox)
        custom_layout.addWidget(QLabel("Nhập đề bài hoặc yêu cầu của bạn:"))
        self.txt_custom_exercise = QTextEdit()
        custom_layout.addWidget(self.txt_custom_exercise)
        self.btn_start_custom = QPushButton("Bắt đầu & Hướng dẫn")
        custom_layout.addWidget(self.btn_start_custom)
        self.build_course_tab(tab_course)
        
    def on_start_custom_exercise(self):
        """
        Handles the 'Start & Guide' button click in the custom exercise tab.
        - Displays the user's description in the left panel.
        - Shows a welcome message in the right panel.
        """
        description = self.txt_custom_exercise.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đề bài trước khi bắt đầu.")
            return

        print("Starting custom exercise...")
        
        # 1. Create the virtual exercise object
        self.current_exercise = {
            "id": "custom_exercise",
            "title": "Bài tập tự do",
            "description": description,
            "course_name": "Bài tập tự do"
        }
        
        # 2. Display the description in the left panel using our existing function
        self.display_exercise_in_left_panel(self.current_exercise)

        # 3. Clear the code editor and start a new AI conversation
        self.code_editor.clear()
        # Gọi với is_custom_exercise=True để dùng rule_lesson.md
        self.start_new_ai_conversation(is_custom_exercise=True)

        # 4. Display a static welcome message in the right panel (instead of calling the AI)
        welcome_html_content = f"""
        <h3>Bắt đầu bài tập: {self.current_exercise.get('title', '')}</h3>
        <p>Đề bài của bạn đã được hiển thị ở khung bên trái.</p>
        <p>Hãy bắt đầu viết code/bài làm vào khung "Bài làm" ở giữa.</p>
        <p>Khi cần, hãy sử dụng các nút <b>💬 Chấm bài</b> hoặc <b>💡 AI Giúp đỡ</b>.</p>
        """
        
        # Update both response tabs with this welcome message
        #self.text_browser.setHtml(welcome_html_content)
        
        html_template = """
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>AI Response</title>
        </head>
        <body><div style='font-size:16px; font-family:Verdana'>{content}</div></body></html>
        """
        full_html = html_template.format(content=welcome_html_content)
        self.web_view.setHtml(full_html)
        
        # Clear the Level and Score labels
        self.lbl_level.setText("-")
        self.lbl_score.setText("-")

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
    
    def display_exercise_in_left_panel(self, exercise_data):
        """Creates the exercise detail widget and displays it in the QStackedWidget."""
        
        # --- Create widgets and layout for the detail page ---
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        # Exercise Title
        title_label = QLabel(exercise_data["title"])
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_label.setWordWrap(True)
        details_layout.addWidget(title_label)

        # Exercise Description (using QTextBrowser for simple HTML)
        desc_browser = QTextBrowser()
        description_html = exercise_data["description"].replace('\n', '<br>')
        desc_browser.setHtml(f"<p>{description_html}</p>")
        details_layout.addWidget(desc_browser, stretch=1)
        
        # --- START NEW BUTTON LAYOUT ---
        # Create a horizontal layout for the navigation buttons
        button_layout = QHBoxLayout()
        details_layout.addLayout(button_layout)

        # Back to List Button (renamed)
        back_button = QPushButton("⬅ Quay lại")
        button_layout.addWidget(back_button)
        
        # Add a spacer to push the "Next" button to the right
        button_layout.addStretch()

        # Next Exercise Button
        next_button = QPushButton("Bài tiếp theo ➡")
        button_layout.addWidget(next_button)
        # --- END NEW BUTTON LAYOUT ---

        # --- Logic for switching pages ---
        new_page_index = self.left_panel_stack.addWidget(details_widget)
        self.left_panel_stack.setCurrentIndex(new_page_index)

        # --- Connect signals for the buttons ---
        def go_back():
            self.left_panel_stack.setCurrentIndex(0)
            self.left_panel_stack.removeWidget(details_widget)
            details_widget.deleteLater()

        def go_to_next_exercise():
            # We'll implement this logic in the next step
            self.navigate_to_next_exercise()

        back_button.clicked.connect(go_back)
        next_button.clicked.connect(go_to_next_exercise)
        
    def build_center_panel(self):
        layout = QVBoxLayout(self.fr_center)
        title_label = QLabel("Bài làm")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        self.code_editor = QPlainTextEdit()
        self.code_editor.setStyleSheet("font-family: Consolas, Courier New; font-size: 14px;")
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0,0,0,0)
        self.btn_run_code = QPushButton("▶ Chạy code")
        self.btn_submit_code = QPushButton("💬 Chấm bài & Đánh giá")
        self.btn_ai_help = QPushButton("💡 AI Giúp đỡ")
        button_layout.addWidget(self.btn_run_code)
        button_layout.addWidget(self.btn_submit_code)
        button_layout.addWidget(self.btn_ai_help)
        layout.addWidget(title_label)
        layout.addWidget(self.code_editor, stretch=1)
        layout.addWidget(button_widget)

    
    # def build_right_panel(self):
    #     layout = QVBoxLayout(self.fr_right)
    #     tabs = QTabWidget()
    #     layout.addWidget(tabs, stretch=1)
        
    #     tab_view_here = QWidget()
    #     tab_extended = QWidget() 
        
    #     tabs.addTab(tab_extended, "Mở rộng") 
    #     tabs.addTab(tab_view_here, "Xem tại đây") 
        
    #     view_here_layout = QVBoxLayout(tab_view_here)
    #     self.text_browser = QTextBrowser()
    #     view_here_layout.addWidget(self.text_browser)
        
    #     extended_layout = QVBoxLayout(tab_extended)
    #     self.web_view = QWebEngineView()
    #     extended_layout.addWidget(self.web_view)

    #     # === THÊM DÒNG KHAI BÁO BIẾN BỊ THIẾU VÀO ĐÂY ===
    #     eval_title = QLabel("Đánh giá")
    #     # ===============================================

    #     eval_title.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
    #     layout.addWidget(eval_title)
    #     eval_widget = QWidget()
    #     eval_layout = QGridLayout(eval_widget)
    #     layout.addWidget(eval_widget)
    #     eval_layout.addWidget(QLabel("Level:"), 0, 0)
    #     self.lbl_level = QLabel("-")
    #     self.lbl_level.setStyleSheet("font-weight: bold; color: blue;")
    #     eval_layout.addWidget(self.lbl_level, 0, 1)
    #     eval_layout.addWidget(QLabel("Score:"), 0, 2)
    #     self.lbl_score = QLabel("-")
    #     self.lbl_score.setStyleSheet("font-weight: bold; color: red;")
    #     eval_layout.addWidget(self.lbl_score, 0, 3)
    
    def build_right_panel(self):
        # Layout chính cho toàn bộ khung bên phải
        layout = QVBoxLayout(self.fr_right)
        
        # 1. Tạo tiêu đề "AI Hướng dẫn" với style giống "Bài làm"
        title_label = QLabel("AI Hướng dẫn")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title_label)

        # 2. Thêm trực tiếp web_view vào layout, không cần dùng tab nữa
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view, stretch=1)
        
        # 3. Giữ nguyên phần "Đánh giá" ở dưới cùng
        eval_title = QLabel("Đánh giá")
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
    
    def on_submit_code_click(self):
        # Bước 1: Kiểm tra ngữ cảnh đã có hay chưa (đơn giản hơn)
        if not self.current_exercise:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một bài tập hoặc bắt đầu một bài tập tự do.")
            return
            
        user_code = self.code_editor.toPlainText().strip()
        if not user_code:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập code bài làm.")
            return

        # Bước 2: Tạo prompt một cách chính xác
        # KHÔNG tạo lại exercise_context, giữ nó là chuỗi rỗng
        exercise_context = "" 
        course_name_for_prompt = self.current_exercise.get('course_name', 'Bài tập')

        # Sử dụng yêu cầu nghiêm ngặt đã được kiểm chứng
        student_submission = (
            f"# Bài làm của người học:\n```{self.current_exercise_language}\n{user_code}\n```\n\n"
            f"# Yêu cầu cho AI:\n"
            f"Phân tích bài làm trên và chỉ đưa ra nhận xét. **Không được nhắc lại đề bài hay tiêu đề bài tập trong phản hồi.**\n"
            f"1. Nếu có lỗi: Chỉ ra loại lỗi và vị trí.\n"
            f"2. Thay vì đưa ra code sửa lỗi, hãy đặt một câu hỏi dẫn dắt.\n"
            f"3. Tuyệt đối không viết ra đáp án hoặc code hoàn chỉnh."
        )

        # KHÔNG dùng .replace('\n', '<br>')
        full_prompt = self.prompt_template.format(
            exercise_context=exercise_context,
            student_submission=student_submission
        )

        # # === BẮT ĐẦU LOGIC CHỌN RULE ===
        # if self.current_exercise.get('id') == 'custom_exercise':
        #     # Chế độ Bài tập tự do: Dùng rule_lesson.md
        #     final_prompt = self.main_rule_lesson + "\n\n" + full_prompt
        # else:
        #     # Chế độ Môn học: Dùng rule.md qua hàm create_main_rule
        #     final_prompt = create_main_rule(
        #         self.main_rule,
        #         full_prompt,
        #         course_name=course_name_for_prompt,
        #         course_language=self.current_exercise_language
        #     )
        # # === KẾT THÚC LOGIC CHỌN RULE ===
        
        # === BẮT ĐẦU LOGIC CHỌN RULE ĐÃ SỬA ===
        # Lấy ngôn ngữ của môn học hiện tại
        lang = self.current_course_language.lower()

        # Kiểm tra xem có phải chế độ tự do hoặc môn không phải lập trình
        if self.current_exercise.get('id') == 'custom_exercise' or lang not in ["c", "java", "python"]:
            # Dùng bộ quy tắc chung, không chuyên về lập trình
            print(f"DEBUG: Áp dụng quy tắc chung (rule_lesson.md) cho ngôn ngữ '{lang}'")
            final_prompt = self.main_rule_lesson + "\n\n" + full_prompt
        else:
            # Chỉ khi là môn học C, Java, Python mới dùng quy tắc lập trình
            print(f"DEBUG: Áp dụng quy tắc lập trình (rule.md) cho ngôn ngữ '{lang}'")
            final_prompt = create_main_rule(
                self.main_rule,
                full_prompt,
                course_name=course_name_for_prompt,
                course_language=self.current_exercise_language
            )
        # === KẾT THÚC LOGIC CHỌN RULE ĐÃ SỬA ===
        
        # Bước 3: Khởi chạy thread (giữ nguyên)
        self.thread = QThread()
        self.worker = GeminiWorker(self.model, self.history)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_gemini_response)
        self.worker.error.connect(self.handle_gemini_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.prompt = final_prompt
        self.thread.start()
        
        self.btn_submit_code.setEnabled(False)
        self.btn_ai_help.setEnabled(False)
    
    def start_new_ai_conversation(self, is_custom_exercise=False):
        """
        Xóa lịch sử cũ và thiết lập một cuộc hội thoại mới với bộ quy tắc đã được xử lý.
        """
        self.history.clear()
        
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
            
    def on_ai_help_click(self):
        if not self.current_exercise:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một bài tập hoặc bắt đầu một bài tập tự do.")
            return

        user_code = self.code_editor.toPlainText().strip()
        
        exercise_context = ""
        course_name_for_prompt = self.current_exercise.get('course_name', 'Bài tập')

        if user_code:
            student_submission = (
                f"# Bài làm hiện tại của người học:\n```{self.current_exercise_language}\n{user_code}\n```\n\n"
                f"# Yêu cầu của người học:\n"
                f"**Không nhắc lại đề bài.** Dựa vào bài làm hiện tại, hãy đưa ra một gợi ý nhỏ hoặc đặt câu hỏi dẫn dắt. "
                f"Tuyệt đối không viết code đáp án."
            )
        else:
            student_submission = (
                f"# Yêu cầu của người học:\n"
                f"**Không nhắc lại đề bài.** Hãy đưa ra gợi ý đầu tiên để bắt đầu bài tập này."
            )

        full_prompt = self.prompt_template.format(
            exercise_context=exercise_context,
            student_submission=student_submission
        )
            
        # # === BẮT ĐẦU LOGIC CHỌN RULE ===
        # if self.current_exercise.get('id') == 'custom_exercise':
        #     # Chế độ Bài tập tự do: Dùng rule_lesson.md
        #     final_prompt = self.main_rule_lesson + "\n\n" + full_prompt
        # else:
        #     # Chế độ Môn học: Dùng rule.md qua hàm create_main_rule
        #     final_prompt = create_main_rule(
        #         self.main_rule,
        #         full_prompt,
        #         course_name=course_name_for_prompt,
        #         course_language=self.current_exercise_language
        #     )
        # # === KẾT THÚC LOGIC CHỌN RULE ===
        
        # === BẮT ĐẦU LOGIC CHỌN RULE ĐÃ SỬA ===
        # Lấy ngôn ngữ của môn học hiện tại
        lang = self.current_course_language.lower()

        # Kiểm tra xem có phải chế độ tự do hoặc môn không phải lập trình
        if self.current_exercise.get('id') == 'custom_exercise' or lang not in ["c", "java", "python"]:
            # Dùng bộ quy tắc chung, không chuyên về lập trình
            print(f"DEBUG: Áp dụng quy tắc chung (rule_lesson.md) cho ngôn ngữ '{lang}'")
            final_prompt = self.main_rule_lesson + "\n\n" + full_prompt
        else:
            # Chỉ khi là môn học C, Java, Python mới dùng quy tắc lập trình
            print(f"DEBUG: Áp dụng quy tắc lập trình (rule.md) cho ngôn ngữ '{lang}'")
            final_prompt = create_main_rule(
                self.main_rule,
                full_prompt,
                course_name=course_name_for_prompt,
                course_language=self.current_exercise_language
            )
        # === KẾT THÚC LOGIC CHỌN RULE ĐÃ SỬA ===

        self.thread = QThread()
        self.worker = GeminiWorker(self.model, self.history)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_gemini_response)
        self.worker.error.connect(self.handle_gemini_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.prompt = final_prompt
        self.thread.start()
        
        self.btn_ai_help.setEnabled(False)
        self.btn_submit_code.setEnabled(False)

    def reset_and_clear_context(self):
        """
        Reset lại toàn bộ trạng thái và giao diện về mặc định.
        Được gọi khi chuyển đổi giữa các môn học hoặc chế độ học.
        """
        print("DEBUG: Đang reset và làm mới ngữ cảnh...")
        
        # 1. Reset các biến trạng thái
        self.current_exercise = None
        self.current_session_index = -1
        self.current_exercise_index = -1
        self.history.clear() # Xóa lịch sử hội thoại với AI

        # 2. Dọn dẹp các ô nhập liệu và hiển thị
        self.code_editor.clear()
        #self.text_browser.setHtml("<h3>Hãy chọn một bài tập để bắt đầu.</h3>")
        self.web_view.setHtml("<h3>Hãy chọn một bài tập để bắt đầu.</h3>")
        self.lbl_level.setText("-")
        self.lbl_score.setText("-")

        # 3. Đảm bảo panel trái luôn quay về màn hình danh sách (cây thư mục)
        if hasattr(self, 'left_panel_stack'):
            self.left_panel_stack.setCurrentIndex(0)
            
    def on_run_code_click(self):
        code = self.code_editor.toPlainText().strip()
        if not code: return
        lang = self.current_exercise_language.lower()
        result = ""
        if lang == "c": result = compile_code(code)
        elif lang == "java": result = compile_java(code)
        elif lang == "python": result = run_python(code)
        else: result = f"Ngôn ngữ '{lang}' không được hỗ trợ để chạy tự động."
        #self.text_browser.setHtml(f"<pre>{result}</pre>")
        self.web_view.setHtml(f"<html><body><pre>{html.escape(result)}</pre></body></html>")

    def handle_gemini_response(self, response_text, was_retry):
        # Hàm render bây giờ sẽ nhận được văn bản JSON an toàn
        html_content, info, err = render_ai_json_markdown(response_text)
        #print ("response_text: ", response_text)
        # Nếu vẫn có lỗi (dù rất hiếm), chỉ cần hiển thị nó ra
        if err:
            self.handle_gemini_error(f"Lỗi phân tích JSON: {err}\n\nPhản hồi gốc:\n{response_text}")
            return

        # Nếu không có lỗi, tiếp tục cập nhật giao diện như bình thường
        #self.text_browser.setHtml(html_content)
        
        html_template = """
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>AI Response</title>
        <script>
            MathJax = {{ tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] }} }};
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
        </head>
        <body><div style='font-size:16px; font-family:Verdana'>{content}</div></body></html>
        """
        full_html = html_template.format(content=html_content)
        self.web_view.setHtml(full_html)
        
        self.lbl_level.setText(str(info.get('level', '-')))
        self.lbl_score.setText(str(info.get('score', '-')))
        
        if self.current_exercise and self.current_exercise.get('id') != 'custom_exercise':
            status = "✓" if info.get('exercise_status') == 'completed' else "✗"
            score = str(info.get('score', 0))
            self.update_tree_item(self.current_exercise.get('id'), status, score)
            
        self.btn_submit_code.setEnabled(True)
        self.btn_ai_help.setEnabled(True)

    def handle_gemini_response(self, response_text, was_retry):
        html_content, info, err = render_ai_json_markdown(response_text)
        
        # === START OF NEW RETRY LOGIC ===
        if err and not was_retry:
            print("⚠️ Phản hồi JSON lỗi → Yêu cầu AI sửa lại.")
            
            # Create the re-prompt message
            re_prompt = RE_RESPONSE_PROMPT.format(error_message=str(err))

            # Start a new thread to ask for the correction
            self.thread = QThread()
            self.worker = GeminiWorker(self.model, self.history)
            self.worker.was_retry = True # Mark this as a retry attempt
            self.worker.moveToThread(self.thread)
            
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.handle_gemini_response)
            self.worker.error.connect(self.handle_gemini_error)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.worker.prompt = re_prompt
            self.thread.start()
            return # Stop processing the current bad response
        elif err and was_retry:
            print("❌ Phản hồi vẫn lỗi sau khi đã thử lại. Hiển thị lỗi.")
        # === END OF NEW RETRY LOGIC ===

        # If no error, or if the retry also failed, continue as normal
        #self.text_browser.setHtml(html_content)
        
        html_template = """
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>AI Response</title>
        <script>
            MathJax = {{ tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] }} }};
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
        </head>
        <body><div style='font-size:16px; font-family:Verdana'>{content}</div></body></html>
        """
        full_html = html_template.format(content=html_content)
        self.web_view.setHtml(full_html)
        
        # 3. Cập nhật Level và Score
        full_html = html_template.format(content=html_content)
        self.web_view.setHtml(full_html)
        self.lbl_level.setText(str(info.get('level', '-')))
        self.lbl_score.setText(str(info.get('score', '-')))
        if self.current_exercise and self.current_exercise.get('id') != 'custom_exercise':
            status = "✓" if info.get('exercise_status') == 'completed' else "✗"
            score = str(info.get('score', 0))
            self.update_tree_item(self.current_exercise.get('id'), status, score)
        self.btn_submit_code.setEnabled(True)
        self.btn_ai_help.setEnabled(True)
        
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
            
    def handle_gemini_error(self, error_text):
        self.web_view.setHtml(f"<h1>Lỗi</h1><p>{error_text}</p>")
        self.btn_submit_code.setEnabled(True)
        self.btn_ai_help.setEnabled(True)
        
    def on_exercise_selected(self, item, column):
        """
        Được gọi khi một mục trên cây thư mục được click.
        """
        exercise_data = item.data(0, Qt.ItemDataRole.UserRole)
        # === BẮT ĐẦU THAY ĐỔI ===
        # Lấy item cha (buổi học) để tìm session_index
        parent_item = item.parent()
        if not exercise_data or not isinstance(exercise_data, dict) or not parent_item:
            self.current_exercise = None
            self.current_session_index = -1
            self.current_exercise_index = -1
            return

        # Tìm index của session và exercise
        self.current_session_index = self.exercise_tree.indexOfTopLevelItem(parent_item)
        self.current_exercise_index = parent_item.indexOfChild(item)
        # === KẾT THÚC THAY ĐỔI ===

        self.current_exercise = exercise_data
        
        # 1. Display the detailed exercise description in the left panel
        self.display_exercise_in_left_panel(exercise_data)
        
        # 2. Clear old code/output and prepare for the new exercise
        self.code_editor.clear()
        # Gọi với is_custom_exercise=False để dùng rule.md
        self.start_new_ai_conversation(is_custom_exercise=False) 
        #self.history.clear()

        # === START OF MAJOR CHANGE ===
        # 3. Instead of calling the AI, display a static welcome message.
        welcome_html_content = f"""
        <h3>Bắt đầu bài tập: {self.current_exercise.get('title', '')}</h3>
        <p>Đề bài đã được hiển thị ở khung bên trái.</p>
        <p>Hãy bắt đầu viết code của bạn vào khung "Bài làm" ở giữa.</p>
        <p>Nếu bạn cần trợ giúp, hãy nhấn nút <b>💡 AI Giúp đỡ</b>.</p>
        """
        
        # Update both response tabs with this welcome message
        #self.text_browser.setHtml(welcome_html_content)
        
        # We create a full HTML page for the web view
        html_template = """
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>AI Response</title>
        </head>
        <body><div style='font-size:16px; font-family:Verdana'>{content}</div></body></html>
        """
        full_html = html_template.format(content=welcome_html_content)
        self.web_view.setHtml(full_html)
        
        # Clear the Level and Score labels
        self.lbl_level.setText("-")
        self.lbl_score.setText("-")
        # === END OF MAJOR CHANGE ===

    def on_custom_language_select(self, text):
        lang_map = {"C": "c", "Java": "java", "Python": "python", "Không": "text"}
        lang_code = lang_map.get(text, "text")
        self.current_exercise_language = lang_code
        print(f"Ngôn ngữ tùy chọn đã đổi thành: {lang_code}")

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
        self.course_combobox.addItems(available_courses)
        try: self.course_combobox.currentTextChanged.disconnect() 
        except TypeError: pass
        self.course_combobox.currentTextChanged.connect(self.on_course_select)
        if available_courses:
            self.course_combobox.setCurrentText(available_courses[0])

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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())