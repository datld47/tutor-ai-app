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
# Sửa thành dòng này
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, QUrl, QUrlQuery
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

import time

from syntax_highlighter import Highlighter

#for image
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QDialog # Đảm bảo đã có dòng này

from PyQt6.QtGui import QFontMetrics # << THÊM QFontMetrics VÀO ĐÂY

import uuid 
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




    
# def render_ai_json_markdown(response_text: str):
#     """
#     Lấy văn bản gốc từ phản hồi JSON của AI và chuyển đổi nó từ định dạng
#     Markdown sang HTML để hiển thị đẹp hơn.
#     """
#     try:
#         match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, flags=re.DOTALL)
#         json_str = match.group(1) if match else response_text.strip()

#         obj = json.loads(json_str)
#         data_text = obj.get("data", "")
#         info = obj.get("info", {})

#         # --- THAY ĐỔI QUAN TRỌNG TẠI ĐÂY ---
#         # Sử dụng thư viện markdown để chuyển đổi sang HTML
#         # Thêm extension 'fenced_code' để hỗ trợ khối code (```) và 'tables' cho bảng
#         final_html = markdown.markdown(data_text, extensions=['fenced_code', 'tables'])

#         return final_html, info, None

#     except json.JSONDecodeError as json_err:
#         print(f"--- LỖI PHÂN TÍCH JSON ---")
#         print(f"Lỗi: Không thể phân tích JSON. Lỗi: {json_err}")
#         # Sử dụng html.escape để hiển thị an toàn phản hồi gốc khi có lỗi
#         error_html = (f"<h3>Lỗi Phân Tích Phản Hồi AI</h3>"
#                       f"<p>Không thể đọc định dạng JSON. Vui lòng thử lại.</p>"
#                       f"<b>Phản hồi gốc:</b><pre>{html.escape(response_text)}</pre>")
#         return error_html, {}, str(json_err)

#     except Exception as err:
#         print(f"--- LỖI KHÔNG MONG MUỐN trong render_ai_json_markdown ---")
#         return f"<pre>Lỗi không mong muốn: {err}</pre>", {}, str(err)

def render_ai_json_markdown(response_text: str):
    """
    Chuyển đổi văn bản phản hồi của AI từ Markdown sang HTML,
    đồng thời bảo vệ các công thức toán MathJax để chúng không bị lỗi.
    """
    print ("response_text:", response_text)
    try:
        # === BỔ SUNG LẠI PHẦN BỊ THIẾU TẠI ĐÂY ===
        # Tìm khối JSON trong phản hồi, kể cả khi có ```json ở đầu
        match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, flags=re.DOTALL)
        # Nếu tìm thấy khối JSON thì lấy nội dung bên trong, nếu không thì coi toàn bộ phản hồi là JSON
        json_str = match.group(1) if match else response_text.strip()
        # ============================================

        obj = json.loads(json_str)
        data_text = obj.get("data", "")
        info = obj.get("info", {})

        # --- LOGIC BẢO VỆ LATEX BẮT ĐẦU TỪ ĐÂY ---
        
        # Bước 1: Tìm và "bảo vệ" tất cả các công thức toán
        math_formulas = []
        def protect_math(match):
            math_formulas.append(match.group(0))
            return f"<math-placeholder-tutor-ai-{len(math_formulas)-1}></math-placeholder-tutor-ai>"

        # Thay thế công thức bằng placeholder
        #protected_text = re.sub(r'(\$\$[^\$]+\$\$|\$[^\$]+\$)', protect_math, data_text, flags=re.DOTALL)
        
        # CẬP NHẬT BIỂU THỨC REGEX ĐỂ NHẬN DIỆN TẤT CẢ CÁC ĐỊNH DẠNG
        # Regex mới này sẽ tìm: $$...$$, $...$, \[...\] (cho display), và \(...\) (cho inline)
        # Sử dụng *? để khớp không tham lam (non-greedy), giúp xử lý các trường hợp phức tạp hơn.
        pattern = r'(\$\$[^\$]*?\$\$|\\\[.*?\\\]|\$[^\$]*?\$|\\\(.*?\\\))'
        protected_text = re.sub(pattern, protect_math, data_text, flags=re.DOTALL)

        # Bước 2: Chuyển đổi phần còn lại sang HTML
        html_from_markdown = markdown.markdown(protected_text, extensions=['fenced_code', 'tables'])

        # Bước 3: Đưa các công thức toán gốc trở lại vào HTML
        final_html = html_from_markdown
        for i, formula in enumerate(math_formulas):
            placeholder = f"<math-placeholder-tutor-ai-{i}></math-placeholder-tutor-ai>"
            final_html = final_html.replace(placeholder, formula)

        return final_html, info, None

    except json.JSONDecodeError as json_err:
        print(f"--- LỖI PHÂN TÍCH JSON ---")
        print(f"Lỗi: Không thể phân tích JSON. Lỗi: {json_err}")
        error_html = (f"<h3>Lỗi Phân Tích Phản Hồi AI</h3>"
                      f"<p>Không thể đọc định dạng JSON. Vui lòng thử lại.</p>"
                      f"<b>Phản hồi gốc:</b><pre>{html.escape(response_text)}</pre>")
        return error_html, {}, str(json_err)

    except Exception as err:
        print(f"--- LỖI KHÔNG MONG MUỐN trong render_ai_json_markdown ---")
        # In ra lỗi cụ thể để dễ gỡ rối hơn
        import traceback
        traceback.print_exc()
        return f"<pre>Lỗi không mong muốn: {err}</pre>", {}, str(err)
    
class KekuleEditorDialog(QDialog):
    """
    Cửa sổ Dialog chứa trình soạn thảo hóa học Kekule.js.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Soạn Thảo Công Thức Hóa Học")
        self.setGeometry(150, 150, 900, 700)
        self.setMinimumSize(700, 500)
        self.svg_output_path = ""

        main_layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        kekule_editor_path = os.path.abspath(os.path.join(PATH_EDIT_TOOLS, 'kekule_editor.html'))
        self.web_view.setUrl(QUrl.fromLocalFile(kekule_editor_path))
        main_layout.addWidget(self.web_view, stretch=1)

        button_layout = QHBoxLayout()
        insert_button = QPushButton("Chèn vào bài viết")
        insert_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        insert_button.clicked.connect(self._on_insert_clicked)
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch(1)
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

    def _on_insert_clicked(self):
        self.web_view.page().runJavaScript("getStructureAsSvg();", self._process_svg_data)

    def _process_svg_data(self, svg_string):
        if not svg_string or '<svg' not in svg_string:
            QMessageBox.warning(self, "Thông báo", "Không có công thức nào để chèn.")
            return

        # Tạo tên file SVG duy nhất
        filename = f"chem_{uuid.uuid4().hex}.svg"
        filepath = os.path.join(PATH_IMG, filename)

        try:
            # Lưu chuỗi SVG vào file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(svg_string)
            self.svg_output_path = filepath
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file SVG:\n{e}")
            self.svg_output_path = ""
            self.reject()

    def get_svg_path(self):
        return self.svg_output_path
    
class MathEditorDialog(QDialog):
    """
    Cửa sổ Dialog chứa MathLive Editor.
    """
    def __init__(self, parent=None, initial_latex=""):
        super().__init__(parent)
        self.setWindowTitle("Chỉnh sửa Công thức Toán học")
        self.setGeometry(200, 200, 800, 600) # Kích thước mặc định
        self.setMinimumSize(600, 400) # Kích thước tối thiểu

        self.latex_output = "" # Để lưu trữ LaTeX khi đóng dialog

        main_layout = QVBoxLayout(self)

        # 1. MathLive Editor (QWebEngineView)
        self.math_web_view = QWebEngineView()
        self.math_web_view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # 📂 Đảm bảo đường dẫn này chính xác
        mathlive_editor_path = os.path.abspath(os.path.join(PATH_EDIT_TOOLS, 'mathlive_editor.html'))
        self.math_web_view.setUrl(QUrl.fromLocalFile(mathlive_editor_path))
        
        # Kết nối tín hiệu khi trang tải xong để khởi tạo và truyền dữ liệu
        self.math_web_view.loadFinished.connect(self._on_math_editor_loaded)
        
        main_layout.addWidget(self.math_web_view, stretch=1)

        # 2. Các nút điều khiển
        button_layout = QHBoxLayout()
        
        self.insert_button = QPushButton("Chèn vào Editor")
        self.insert_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 16px; border-radius: 5px;")
        self.insert_button.clicked.connect(self._on_insert_clicked)

        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px 16px; border-radius: 5px;")
        self.cancel_button.clicked.connect(self.reject) # Đóng dialog với kết quả QDialog.Rejected

        button_layout.addStretch(1) # Đẩy các nút sang phải
        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.initial_latex = initial_latex # Lưu trữ LaTeX ban đầu để truyền vào JS

    def _on_math_editor_loaded(self, ok):
        """
        Được gọi khi trang HTML của MathLive Editor đã tải xong.
        Truyền dữ liệu LaTeX ban đầu vào MathLive và thiết lập listener.
        """
        if not ok:
            print("Lỗi: Không thể tải mathlive_editor.html")
            return

        # ✅ THÊM DÒNG NÀY ĐỂ RA LỆNH CHO WIDGET NHẬN FOCUS
        self.math_web_view.setFocus() 

        # Gọi hàm JavaScript đã được định nghĩa trong HTML để đặt giá trị và focus
        js_call = f"window.setInitialLatexAndFocus(`{self.initial_latex}`);"
        self.math_web_view.page().runJavaScript(js_call)
        
        print("MathLive Editor đã sẵn sàng và được khởi tạo.")

    def _on_insert_clicked(self):
        """
        Lấy giá trị LaTeX từ MathLive Editor và chấp nhận dialog.
        """
        js_get_value = "window.mathEditorInstance.getValue();"
        self.math_web_view.page().runJavaScript(js_get_value, self._process_latex_value)

    def _process_latex_value(self, latex_value):
        """
        Callback để xử lý giá trị LaTeX nhận được từ JavaScript.
        """
        self.latex_output = latex_value
        self.accept() # Đóng dialog với kết quả QDialog.Accepted

    def get_latex_output(self):
        return self.latex_output
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
            #safe_response_text = original_text
            # =======================================
            
            original_text = response.text
            
            # Luôn tự động sửa lỗi escape để đảm bảo JSON hợp lệ, giúp ứng dụng ổn định.
            safe_response_text = original_text.replace('\\', '\\\\')            

            self.history.append({'role': 'model', 'parts': [original_text]})
            self.finished.emit(safe_response_text, self.was_retry)

        except Exception as e:
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
class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutor AI - V1.1")
        self.setGeometry(100, 100, 1600, 900)

        # --- Các biến trạng thái của ứng dụng ---
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
        
        # --- Các biến trạng thái cho Firebase và người dùng ---
        self.firebase = None
        self.auth = None
        self.db = None
        self.user_info = {} # Lưu thông tin người dùng (uid, token, username)
        self.is_logged_in = False # Trạng thái đăng nhập
        
        # >>> THÊM CÁC BIẾN QUẢN LÝ TRẠNG THÁI GIAO DIỆN CHAT
        self.chat_interface_ready = False
        self.js_call_queue = [] # Hàng đợi các lệnh JS
        # <<< KẾT THÚC
        
        # --- Các biến quản lý trạng thái giao diện ---
        self.current_session_index = -1        
        self.current_step_index = -1 
        self.editor_initialized = False 
        self.custom_editor_initialized = False
        self.highlighter = None

        # --- Xây dựng giao diện chính ---
        self.build_menus_and_toolbar()
        self.build_formatting_toolbar() 
        
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
        self.custom_exercise_editor = QWebEngineView()  # >>> THÊM DÒNG NÀY ĐỂ TẠO EDITOR MỚI CHO ĐỀ BÀI <<<
        
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

    def on_open_math_editor(self):
        """
        Mở MathEditorDialog và chèn công thức LaTeX vào CKEditor.
        """
        # Lấy nội dung hiện tại của CKEditor để truyền vào MathLive (nếu có LaTeX đã tồn tại)
        # CKEditor không có hàm trực tiếp để lấy LaTeX, nó chỉ xuất HTML.
        # Nếu bạn muốn chỉnh sửa LaTeX đã có, bạn cần một cách để trích xuất LaTeX từ HTML của CKEditor.
        # Với mục đích đơn giản, chúng ta sẽ mở MathLive trống hoặc với một giá trị mặc định.
        
        # Hoặc, nếu bạn muốn lấy LaTeX từ selection trong CKEditor:
        # js_get_selected_html = "window.editorInstance.model.document.selection.getSelectedContent().toHtml();"
        # self.rich_text_editor.page().runJavaScript(js_get_selected_html, self._process_selected_html_for_math)
        
        # Để đơn giản, chúng ta sẽ mở Math Editor với nội dung trống hoặc một ví dụ.
        initial_latex = "" # Hoặc lấy từ selection nếu bạn có logic phức tạp hơn
        
        dialog = MathEditorDialog(self, initial_latex=initial_latex)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            latex_content = dialog.get_latex_output()
            if latex_content:
                # Chèn LaTeX vào CKEditor
                # CKEditor không hỗ trợ trực tiếp chèn LaTeX và render.
                # Bạn cần một plugin MathType/MathJax cho CKEditor để làm điều này.
                # Nếu không, bạn sẽ chèn nó dưới dạng văn bản hoặc hình ảnh.
                # Cách đơn giản nhất là chèn nó dưới dạng chuỗi LaTeX hoặc sử dụng MathJax/KaTeX rendering.
                
                # Để hiển thị LaTeX trong CKEditor, bạn có thể chèn nó dưới dạng một chuỗi văn bản
                # và kỳ vọng CKEditor sẽ có plugin để render nó (ví dụ: MathType plugin).
                # Hoặc bạn có thể chèn nó dưới dạng hình ảnh sau khi render LaTeX thành hình ảnh (phức tạp hơn).
                
                # Cách 1: Chèn dưới dạng chuỗi LaTeX (CKEditor cần plugin để render)
                # latex_string_to_insert = f"\\({latex_content}\\)" # Dùng dấu ngoặc MathJax inline
                # js_insert_html = f"window.editorInstance.execute('insertHtml', '{latex_string_to_insert}');"
                # self.rich_text_editor.page().runJavaScript(js_insert_html)

                # Cách 2: Chèn dưới dạng HTML với MathJax/KaTeX rendering (nếu CKEditor không có plugin)
                # Đây là cách phổ biến nếu bạn muốn hiển thị ngay trong CKEditor.
                # Bạn cần đảm bảo CKEditor của bạn được cấu hình để tải MathJax/KaTeX.
                # Ví dụ:
                html_to_insert = f'<p>\\({latex_content}\\)</p>' # Dùng thẻ p và dấu ngoặc MathJax
                js_insert_html = f"window.editorInstance.model.change(writer => {{ writer.insertHtml('{html_to_insert}', writer.model.document.selection); }});"
                self.rich_text_editor.page().runJavaScript(js_insert_html)
                
                # Hoặc, nếu bạn muốn chèn vào PlainTextEdit:
                if self.editor_stack.currentIndex() == self.plain_editor_index:
                    current_text = self.plain_code_editor.toPlainText()
                    cursor = self.plain_code_editor.textCursor()
                    cursor.insertText(f"\\({latex_content}\\)") # Chèn LaTeX trực tiếp
                    self.plain_code_editor.setTextCursor(cursor)
                
                print(f"Đã chèn LaTeX: {latex_content}")
            else:
                print("Không có LaTeX nào được chèn.")

        # Đảm bảo CKEditor được focus lại sau khi đóng dialog
        self.rich_text_editor.page().runJavaScript("window.editorInstance.editing.view.focus();")

    # Nếu bạn muốn trích xuất HTML đã chọn và phân tích LaTeX từ đó (phức tạp hơn)
    # def _process_selected_html_for_math(self, html_content):
    #     # Logic để phân tích HTML và tìm chuỗi LaTeX (ví dụ: tìm các thẻ <span class="math-tex">)
    #     # Sau đó mở dialog với LaTeX đã tìm thấy.
    #     pass
    
    def build_formatting_toolbar(self):
        """Tạo một QToolBar riêng cho các chức năng định dạng văn bản."""
        self.formatting_toolbar = QToolBar("Formatting Toolbar")
        self.formatting_toolbar.setObjectName("FormattingToolbar")

        # Tạo các action (nút bấm)
        self.action_bold = QAction(QIcon(os.path.join(PATH_IMG, 'bold.png')), "In đậm (Ctrl+B)", self)
        self.action_italic = QAction(QIcon(os.path.join(PATH_IMG, 'italic.png')), "In nghiêng (Ctrl+I)", self)
        self.action_bulleted_list = QAction(QIcon(os.path.join(PATH_IMG, 'bulleted-list.png')), "Danh sách gạch đầu dòng", self)
        self.action_numbered_list = QAction(QIcon(os.path.join(PATH_IMG, 'numbered-list.png')), "Danh sách có thứ tự", self)

        self.action_superscript = QAction(QIcon(os.path.join(PATH_IMG, 'superscript.png')), "Chỉ số trên", self)
        self.action_subscript = QAction(QIcon(os.path.join(PATH_IMG, 'subscript.png')), "Chỉ số dưới", self)

        # Thêm các action vào toolbar
        self.formatting_toolbar.addAction(self.action_bold)
        self.formatting_toolbar.addAction(self.action_italic)
        self.formatting_toolbar.addSeparator()
        self.formatting_toolbar.addAction(self.action_bulleted_list)
        self.formatting_toolbar.addAction(self.action_numbered_list)
        
        self.formatting_toolbar.addAction(self.action_italic) # Nút đã có
        self.formatting_toolbar.addAction(self.action_superscript)
        self.formatting_toolbar.addAction(self.action_subscript)
        self.formatting_toolbar.addSeparator() # Ngăn cách
        
        # Mặc định ẩn toolbar này đi
        self.formatting_toolbar.setVisible(False)
        
        # Thêm toolbar này vào cửa sổ chính
        self.addToolBar(self.formatting_toolbar)

    def on_format_bold(self):
        self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('bold');")

    def on_format_italic(self):
        self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('italic');")

    def on_format_bulleted_list(self):
        self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('bulletedList');")

    def on_format_numbered_list(self):
        self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('numberedList');")
        
    def on_custom_editor_load_finished(self, ok):
        """Khởi tạo CKEditor cho ô nhập đề bài ở tab 'Bài tập Tự do'."""
        if not ok or self.custom_editor_initialized:
            return

        self.custom_editor_initialized = True
        print("DEBUG: custom_editor.html đã tải. Bắt đầu tiêm CKEditor script...")

        try:
            # Đọc script từ file vào một biến cục bộ
            with open(os.path.join(PATH_EDIT_TOOLS, 'ckeditor.js'), 'r', encoding='utf-8') as f:
                ckeditor_script = f.read()
        except FileNotFoundError:
            print(f"LỖI: Không tìm thấy file 'ckeditor.js' trong thư mục {PATH_EDIT_TOOLS}!")
            self.custom_editor_initialized = False
            return

        init_script = """
            if (typeof ClassicEditor !== 'undefined' && !window.customEditorInstance) {
                ClassicEditor
                    // Nhắm đúng vào ID mới
                    .create( document.querySelector( '#custom-editor' ) )
                    .then( newEditor => {
                        // Lưu vào biến JavaScript riêng
                        window.customEditorInstance = newEditor;
                        console.log('THÀNH CÔNG: CKEditor cho đề bài đã được khởi tạo!');
                    } )
                    .catch( error => { console.error('Lỗi khi khởi tạo custom editor:', error ); } );
            }
        """

        # SỬA LỖI TẠI ĐÂY:
        # 1. Dùng đúng tên biến: `self.custom_exercise_editor`
        # 2. Dùng biến cục bộ: `ckeditor_script` thay vì `self.ckeditor_script`
        self.custom_exercise_editor.page().runJavaScript(ckeditor_script,
            lambda result: self.custom_exercise_editor.page().runJavaScript(init_script))
        
    def on_chat_view_loaded(self, success):
        """
        Được kích hoạt khi QWebEngineView đã tải xong trang HTML.
        """
        if success:
            print("✅ Giao diện chat đã sẵn sàng.")
            self.chat_interface_ready = True
            # Thực thi tất cả các lệnh JS đã được xếp hàng trong khi chờ
            for js_code in self.js_call_queue:
                self.web_view.page().runJavaScript(js_code)
            self.js_call_queue.clear() # Dọn dẹp hàng đợi
        else:
            print("❌ Lỗi: Không thể tải file chat_view.html.")
            
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
          
    # (Thêm hàm này vào class MainWindow)
    def on_open_chem_editor(self):
        """
        Mở KekuleEditorDialog và chèn ảnh SVG vào CKEditor.
        """
        dialog = KekuleEditorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            image_path = dialog.get_svg_path()
            if image_path:
                # Chuyển đổi đường dẫn file thành URL mà QWebEngineView có thể hiểu
                # và chèn vào CKEditor dưới dạng thẻ <img>
                file_url = QUrl.fromLocalFile(os.path.abspath(image_path)).toString()
                
                # Dùng JavaScript để chèn HTML
                # Chúng ta dùng model.change để đảm bảo việc chèn được ghi nhận vào undo stack
                html_to_insert = f'<figure class="image"><img src="{file_url}" alt="Công thức hóa học"></figure>'
                js_code = f"""
                window.editorInstance.model.change(writer => {{
                    const viewFragment = window.editorInstance.data.processor.toView('{html_to_insert}');
                    const modelFragment = window.editorInstance.data.toModel(viewFragment);
                    window.editorInstance.model.insertContent(modelFragment);
                }});
                """
                self.rich_text_editor.page().runJavaScript(js_code)
                print(f"Đã chèn ảnh SVG từ: {image_path}")


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
        
        # Thêm action cho Math Editor
        self.action_math_editor = QAction(QIcon(os.path.join(PATH_IMG, 'math.png')), "Chèn công thức toán học", self)
        toolbar.addAction(self.action_math_editor)
        tool_menu.addAction(self.action_math_editor) # Thêm vào menu Function
        
        self.action_chem_editor = QAction(QIcon(os.path.join(PATH_IMG, 'chemistry.png')), "Soạn công thức hóa học", self)
        toolbar.addAction(self.action_chem_editor)
        
        # Thêm vào menu Function
        tool_menu.addAction(self.action_math_editor)
        tool_menu.addAction(self.action_chem_editor)
        
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

    def run_gemini_in_thread(self, prompt, is_retry=False):
        """
        Tạo và chạy một thread riêng để gọi Gemini API,
        tránh làm treo giao diện người dùng.
        """
        self.thread = QThread()
        # Khởi tạo Worker với model và history
        self.worker = GeminiWorker(self.model, self.history)
        
        # Gán các thuộc tính cho worker sau khi tạo
        self.worker.prompt = prompt
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

    def build_left_panel(self):
        layout = QVBoxLayout(self.fr_left)
        tabs = QTabWidget()
        tabs.setObjectName("LeftPanelTabs") 
        layout.addWidget(tabs)
        tab_custom = QWidget()
        tab_course = QWidget()
        tabs.addTab(tab_custom, "Bài tập Tự do")
        tabs.addTab(tab_course, "Bài tập theo Môn học")
        
        # --- Bố cục cho tab "Bài tập Tự do" ---
        custom_layout = QVBoxLayout(tab_custom)
        
        # Các widget ở trên cùng
        custom_layout.addWidget(QLabel("Chọn ngôn ngữ lập trình (tùy chọn):"))
        self.lang_combobox = QComboBox()
        self.lang_combobox.addItems(["Không", "C", "Java", "Python"])
        self.lang_combobox.setCurrentText("Không") 
        custom_layout.addWidget(self.lang_combobox)
        custom_layout.addWidget(QLabel("Nhập đề bài hoặc yêu cầu của bạn:"))
        
        # Thiết lập editor mới cho đề bài tự do
        editor_path = os.path.join(PATH_EDIT_TOOLS, 'custom_editor.html')
        self.custom_exercise_editor.setUrl(QUrl.fromLocalFile(os.path.abspath(editor_path)))
        
        # >>> THAY ĐỔI QUAN TRỌNG: Thêm stretch factor cho editor <<<
        custom_layout.addWidget(self.custom_exercise_editor, stretch=1)
        # <<< KẾT THÚC THAY ĐỔI
        
        # Nút bấm ở dưới cùng
        self.btn_start_custom = QPushButton("Bắt đầu & Hướng dẫn")
        custom_layout.addWidget(self.btn_start_custom)

        # Xây dựng nội dung cho tab "Bài tập theo Môn học"
        self.build_course_tab(tab_course)

    def on_start_custom_exercise(self):
        def process_description(description_html):
            # Chuyển HTML sang text thuần để kiểm tra rỗng
            temp_doc = QTextBrowser()
            temp_doc.setHtml(description_html)
            plain_text = temp_doc.toPlainText().strip()

            if not plain_text:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đề bài trước khi bắt đầu.")
                return

            print("Starting custom exercise...")

            self.current_exercise = {
                "id": "custom_exercise",
                "title": "Bài tập tự do",
                "description": description_html, # Lưu dưới dạng HTML
                "course_name": "Bài tập tự do"
            }

            self.display_exercise_in_left_panel(self.current_exercise)
            self.clear_current_editor_content()
            self.start_new_ai_conversation(is_custom_exercise=True)

            welcome_html_content = (
                f"<h3>Bắt đầu bài tập: {self.current_exercise.get('title', '')}</h3>"
                f"<p>Đề bài của bạn đã được hiển thị ở khung bên trái.</p>"
            )
            self.clear_chat_interface()
            self.add_message_to_chat(welcome_html_content, "👋 Chào mừng")

            self.lbl_level.setText("-")
            self.lbl_score.setText("-")

        # Dùng JavaScript để lấy nội dung HTML từ CKEditor
        js_code = "window.customEditorInstance ? window.customEditorInstance.getData() : '';"
        self.custom_exercise_editor.page().runJavaScript(js_code, process_description)

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
        
    # def build_center_panel(self):
    #     layout = QVBoxLayout(self.fr_center)
    #     title_label = QLabel("Bài làm")
    #     title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #     title_label.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        
    #     # --- THAY ĐỔI LỚN BẮT ĐẦU TỪ ĐÂY ---
        
    #     # 1. Cấu hình Plain Text Editor (cho code)
    #     self.plain_code_editor.setStyleSheet("font-family: Consolas, Courier New; font-size: 14px;")

    #     # 2. Cấu hình Rich Text Editor (CKEditor)
    #     self.rich_text_editor.loadFinished.connect(self.on_editor_load_finished)
    #     editor_path = os.path.join(PATH_EDIT_TOOLS, 'editor.html')
    #     self.rich_text_editor.setUrl(QUrl.fromLocalFile(os.path.abspath(editor_path)))
        
    #     # 3. Thêm cả hai editor vào QStackedWidget
    #     # Lưu lại index để dễ dàng chuyển đổi
    #     self.plain_editor_index = self.editor_stack.addWidget(self.plain_code_editor)
    #     self.rich_editor_index = self.editor_stack.addWidget(self.rich_text_editor)
        
    #     # Mặc định hiển thị editor cho code
    #     #self.editor_stack.setCurrentIndex(self.plain_editor_index)
        
    #     # 4. Thêm QStackedWidget vào layout chính
    #     layout.addWidget(title_label)
    #     layout.addWidget(self.editor_stack, stretch=1) # Thay thế editor cũ bằng stack
        
    #     # --- KẾT THÚC THAY ĐỔI ---
        
    #     # Phần các nút bấm giữ nguyên
    #     button_widget = QWidget()
    #     button_layout = QHBoxLayout(button_widget)
    #     button_layout.setContentsMargins(0,0,0,0)
    #     self.btn_run_code = QPushButton("▶ Chạy code")
    #     self.btn_submit_code = QPushButton("💬 Chấm bài & Đánh giá")
    #     self.btn_ai_help = QPushButton("💡 AI Giúp đỡ")
    #     button_layout.addWidget(self.btn_run_code)
    #     button_layout.addWidget(self.btn_submit_code)
    #     button_layout.addWidget(self.btn_ai_help)
    #     layout.addWidget(button_widget)
    
    def build_center_panel(self):
        layout = QVBoxLayout(self.fr_center)
        title_label = QLabel("Bài làm")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        
        # 1. Cấu hình Plain Text Editor (cho code)
        self.plain_code_editor.setStyleSheet("font-family: Consolas, Courier New; font-size: 14px;")

        # --- BẮT ĐẦU CẬP NHẬT TẠI ĐÂY ---
        # Cài đặt độ rộng của phím Tab tương đương 4 dấu cách
        font = self.plain_code_editor.font()
        font_metrics = QFontMetrics(font)
        # Lấy chiều rộng (bằng pixel) của 8 ký tự ' '
        tab_stop_width = font_metrics.horizontalAdvance(' ' * 8) 
        self.plain_code_editor.setTabStopDistance(tab_stop_width)
        # --- KẾT THÚC CẬP NHẬT ---

        # 2. Cấu hình Rich Text Editor (CKEditor)
        # ... (phần còn lại của hàm giữ nguyên)
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

    # THAY THẾ 3 HÀM CŨ BẰNG 3 HÀM MỚI NÀY
    def add_message_to_chat(self, html_content, message_type=""):
        """Gửi một tin nhắn mới vào giao diện chat một cách an toàn."""
        escaped_html = json.dumps(html_content)
        escaped_type = json.dumps(message_type)
        js_code = f"addAiMessage({escaped_html}, {escaped_type});"
        
        if self.chat_interface_ready:
            self.web_view.page().runJavaScript(js_code)
        else:
            self.js_call_queue.append(js_code)

    # def update_pinned_step_display(self, step_text="Hãy chọn một bài tập để bắt đầu."):
    #     """Cập nhật nội dung được ghim một cách an toàn."""
    #     content = f"<strong>Bước hiện tại:</strong> {html.escape(step_text)}"
    #     escaped_content = json.dumps(content)
    #     js_code = f"updatePinnedStep({escaped_content});"
        
    #     if self.chat_interface_ready:
    #         self.web_view.page().runJavaScript(js_code)
    #     else:
    #         self.js_call_queue.append(js_code)
    
    # THAY THẾ HÀM CŨ BẰNG HÀM NÀY

    # def update_pinned_step_display(self, step_text=""): # Đặt giá trị mặc định là chuỗi rỗng
    #     """Cập nhật nội dung được ghim một cách an toàn."""
    #     # Chỉ hiển thị nếu có nội dung
    #     if step_text:
    #         content = f"<strong>Bước hiện tại:</strong> {html.escape(step_text)}"
    #     else:
    #         content = "" # Nếu không có text, nội dung sẽ là rỗng
        
    #     escaped_content = json.dumps(content)
    #     js_code = f"updatePinnedStep({escaped_content});"
        
    #     if self.chat_interface_ready:
    #         self.web_view.page().runJavaScript(js_code)
    #     else:
    #         self.js_call_queue.append(js_code)
    
    # Trong file app_pyqt.py, thay thế hàm cũ

    def update_pinned_step_display(self, step_text=""): # Giá trị mặc định là rỗng
        """
        Cập nhật nội dung được ghim.
        Gửi một chuỗi rỗng sẽ ẩn thanh ghim đi.
        """
        content = ""
        if step_text: # Chỉ tạo nội dung nếu step_text không rỗng
            content = f"<strong>Bước hiện tại:</strong> {html.escape(step_text)}"
        
        escaped_content = json.dumps(content)
        js_code = f"updatePinnedStep({escaped_content});"
        
        if self.chat_interface_ready:
            self.web_view.page().runJavaScript(js_code)
        else:
            # Đảm bảo lệnh này được thêm vào hàng đợi nếu giao diện chưa sẵn sàng
            self.js_call_queue.append(js_code)

    def clear_chat_interface(self):
        """Xóa toàn bộ nội dung chat và reset phần ghim một cách an toàn."""
        # Luôn xóa hàng đợi cũ trước khi thực hiện hành động mới
        self.js_call_queue.clear() 
        
        js_clear_code = "document.getElementById('chat-container').innerHTML = '';"
        if self.chat_interface_ready:
            self.web_view.page().runJavaScript(js_clear_code)
        else:
            self.js_call_queue.append(js_clear_code)
            
        # Luôn reset phần ghim sau khi xóa
        self.update_pinned_step_display()
        
    def build_right_panel(self):
        layout = QVBoxLayout(self.fr_right)

        title_label = QLabel("AI Hướng dẫn")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title_label)

        self.web_view = QWebEngineView()
        self.web_view.loadFinished.connect(self.on_chat_view_loaded)
        
        # # >>> THAY ĐỔI QUAN TRỌNG: Tải file giao diện chat
        # chat_view_path = os.path.abspath("chat_view.html")
        # self.web_view.setUrl(QUrl.fromLocalFile(chat_view_path))
        # # <<< KẾT THÚC THAY ĐỔI
        
        # === THAY ĐỔI QUAN TRỌNG ĐỂ VÔ HIỆU HÓA CACHE ===
        chat_view_path = os.path.abspath("chat_view.html")
        # Tạo một URL cơ sở từ đường dẫn file
        url = QUrl.fromLocalFile(chat_view_path)
        # Tạo một đối tượng query và thêm vào một tham số ngẫu nhiên dựa trên thời gian
        query = QUrlQuery()
        query.addQueryItem("_v", str(time.time())) # Ví dụ: ?_v=1678886400.123
        # Gán query vào URL
        url.setQuery(query)
        # Tải URL đã có tham số ngẫu nhiên
        self.web_view.setUrl(url)
        # ===============================================
        
        layout.addWidget(self.web_view, stretch=1)

        # Phần "Đánh giá" ở dưới cùng giữ nguyên
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
    
    def on_format_superscript(self):
        self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('superscript');")

    def on_format_subscript(self):
        self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('subscript');")
        
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

        # >>> THÊM DÒNG NÀY ĐỂ KẾT NỐI TÍN HIỆU CHO EDITOR BÊN TRÁI <<<
        self.custom_exercise_editor.loadFinished.connect(self.on_custom_editor_load_finished)
        # <<< KẾT THÚC THÊM

        # Kết nối cho thanh công cụ định dạng (đã có từ trước, giữ nguyên)
        self.action_bold.triggered.connect(self.on_format_bold)
        self.action_italic.triggered.connect(self.on_format_italic)
        self.action_bulleted_list.triggered.connect(self.on_format_bulleted_list)
        self.action_numbered_list.triggered.connect(self.on_format_numbered_list)
        
        self.action_math_editor.triggered.connect(self.on_open_math_editor) #kêt nối math
        
        self.action_superscript.triggered.connect(self.on_format_superscript)
        self.action_subscript.triggered.connect(self.on_format_subscript)
        
        self.action_math_editor.triggered.connect(self.on_open_math_editor) # Dòng này đã có

        # KẾT NỐI NÚT MỚI
        self.action_chem_editor.triggered.connect(self.on_open_chem_editor)

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

    # THAY THẾ TOÀN BỘ HÀM on_submit_code_click CŨ BẰNG HÀM NÀY

    def on_submit_code_click(self):
        """Xử lý khi người dùng nhấn nút Chấm bài & Đánh giá."""

        def process_submission(user_content):
            if not self.current_exercise:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một bài tập trước.")
                self.enable_buttons()
                return
            
            if not user_content.strip():
                QMessageBox.warning(self, "Thông báo", "Vui lòng nhập bài làm trước khi nộp.")
                self.enable_buttons()
                return
            
            course_name = self.json_course.get('course_name', 'Không xác định') if self.json_course else 'Bài tập tự do'
            
            # --- BẮT ĐẦU SỬA LỖI ---
            # Tách riêng phần chỉ thị cho AI và phần bài làm của người học
            
            # 1. Tạo chỉ thị cho AI (sẽ được đưa vào placeholder {step_by_step_guidance})
            grading_instructions = (
                f"Phân tích và đánh giá bài làm của người học dưới đây. "
                f"Đưa ra nhận xét, chỉ ra điểm đúng, điểm sai (nếu có). "
                f"Nếu bài làm chưa hoàn thiện, hãy đặt câu hỏi gợi mở để người học tự sửa. "
                f"Tuyệt đối không viết code đáp án. "
                f"Lưu ý: Không cần nhắc lại tên bài tập hay đề bài trong phần phản hồi."
            )

            # 2. Tạo khối bài làm của người học (sẽ được đưa vào placeholder {student_submission})
            student_submission_block = (
                f"# Bài làm của người học:\n"
                f"```{self.current_exercise_language}\n{user_content}\n```\n"
            )
            
            # 3. Ghép vào mẫu prompt chính với đầy đủ các placeholder
            full_prompt = self.prompt_template.format(
                exercise_context=(
                    f"Môn học: {course_name}\n"
                    f"Bài tập: {self.current_exercise.get('title', 'N/A')}\n"
                    f"Đề bài: {self.current_exercise.get('description', 'N/A')}\n\n"
                ),
                step_by_step_guidance=grading_instructions,
                student_submission=student_submission_block
            )
            # --- KẾT THÚC SỬA LỖI ---

            # Logic chọn quy tắc và gọi thread giữ nguyên
            lang = self.current_course_language.lower()
            rule_base = self.main_rule_lesson if (self.current_exercise.get('id') == 'custom_exercise' or lang not in ["c", "java", "python"]) else self.main_rule
            
            final_prompt = create_main_rule(rule_base, full_prompt, course_name, self.current_exercise_language)
            
            if 'score' in self.current_exercise and self.current_exercise.get('score', 0) > 0:
                self.current_exercise['score'] -= 1

            self.run_gemini_in_thread(final_prompt)

        self.disable_buttons()
        self.get_current_editor_content(process_submission)
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
            
    # Trong class MainWindow
    def on_ai_help_click(self):
        """
        Xử lý khi người dùng nhấn nút AI Giúp đỡ.
        Hàm này sẽ kiểm tra xem đã có hướng dẫn chưa để đưa ra prompt phù hợp.
        """
        def process_help_request(user_content):
            if not self.current_exercise:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một bài tập trước.")
                self.enable_buttons()
                return

            course_name = self.json_course.get('course_name', 'Không xác định') if self.json_course else 'Bài tập tự do'
            
            guidance = self.current_exercise.get("guidance") or self.current_exercise.get("generated_guidance")
            
            guidance_prompt_block = ""

            if guidance:
                # KỊCH BẢN 1: ĐÃ CÓ HƯỚNG DẪN (Cập nhật prompt tại đây)
                print("DEBUG: Đã có hướng dẫn, yêu cầu AI tóm tắt theo các bước có sẵn.")
                formatted_guidance = "\n".join([f"{i+1}. {step}" for i, step in enumerate(guidance)])
                
                if user_content.strip():
                    # Logic khi người dùng đã viết code (giữ nguyên)
                    guidance_prompt_block = (
                        f"Dưới đây là các bước hướng dẫn giải bài tập này:\n{formatted_guidance}\n\n"
                        f"Dựa vào bài làm hiện tại của người học và các bước hướng dẫn trên, hãy đưa ra một gợi ý nhỏ "
                        f"hoặc đặt câu hỏi để giúp họ tiến tới bước tiếp theo. "
                        f"Tuyệt đối không viết code đáp án và không nhắc lại đề bài."
                    )
                else:
                    # --- PROMPT MỚI, NGHIÊM NGẶT HƠN KHI TÓM TẮT ---
                    guidance_prompt_block = (
                        f"**Nhiệm vụ của bạn là diễn giải lại các bước hướng dẫn đã có sẵn dưới đây một cách tổng quan cho người mới bắt đầu. TUYỆT ĐỐI KHÔNG TẠO RA CÁC BƯỚC MỚI.**\n\n"
                        f"**Các bước hướng dẫn có sẵn:**\n{formatted_guidance}\n\n"
                        f"**Yêu cầu:**\n"
                        f"- Bắt đầu phản hồi trực tiếp bằng mục 'Hướng dẫn tổng quát'.\n\n"
                        f"- Diễn giải lại các bước trên bằng ngôn ngữ thân thiện, dễ hiểu, mỗi bước trên một dòng riêng biệt.\n"
                        f"- Không đưa ra code đáp án và không nhắc lại đề bài."            
                        f"   `\"**Hướng dẫn:**\\n\\n1. Đây là bước một.\\n2. Đây là bước hai."
                    )
                    # --- KẾT THÚC CẬP NHẬT ---
            else:
                # KỊCH BẢN 2: CHƯA CÓ HƯỚNG DẪN (Giữ nguyên logic)
                print("DEBUG: Chưa có hướng dẫn, yêu cầu AI tạo ra các bước thông minh hơn.")
                self.is_awaiting_guidance = True
                guidance_prompt_block = (
                    f"Bài tập này chưa có các bước hướng dẫn chi tiết. Nhiệm vụ của bạn là:\n"
                    f"1. Phân tích đề bài và tự tạo ra một danh sách các bước hướng dẫn chung nhất, KHÔNG được đưa ra lời giải. **QUY TẮC SƯ PHẠM CỐT LÕI: Luôn đề xuất giải pháp tối giản nhất. Đối với các bài tập chỉ yêu cầu in ra dữ liệu cố định (static data), TUYỆT ĐỐI KHÔNG hướng dẫn tạo biến. Thay vào đó, hãy hướng dẫn người học sử dụng trực tiếp lệnh `print()` với các giá trị chuỗi/số.**\n"
                    f"2. Trình bày các bước đó trong trường 'data' theo đúng định dạng Markdown sau:\n"
                    f"   - **KHÔNG lặp lại tên bài tập hay đề bài.**\n"
                    f"   - Bắt đầu trực tiếp bằng mục 'Hướng dẫn' (`**Hướng dẫn:**`).\n"
                    f"   - Liệt kê các bước dưới dạng danh sách có thứ tự (1., 2., 3.), **MỖI BƯỚC PHẢI CÓ KÝ TỰ XUỐNG DÒNG (\\n) ở cuối.**\n"                    
                    f"3. Trong trường 'info' của JSON, BẮT BUỘC phải có khóa 'generated_steps' chứa một MẢNG các chuỗi string, mỗi chuỗi là một bước hướng dẫn.\n"
                    f"   `\"**Hướng dẫn:**\\n\\n1. Đây là bước một.\\n2. Đây là bước hai."
                )

            # ... (Phần còn lại của hàm giữ nguyên)
            student_submission_prompt = f"# Bài làm hiện tại của người học:\n```{self.current_exercise_language}\n{user_content}\n```" if user_content.strip() else ""
            full_prompt = self.prompt_template.format(
                exercise_context=(
                    f"Môn học: {course_name}\n"
                    f"Bài tập: {self.current_exercise.get('title', 'N/A')}\n"
                    f"Đề bài: {self.current_exercise.get('description', 'N/A')}\n"
                ),
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
        Sử dụng cờ self.editor_initialized để đảm bảo chỉ chạy một lần.
        """
        # >>> THAY ĐỔI: Thêm điều kiện kiểm tra cờ ở ngay đầu
        if not ok or self.editor_initialized:
            return # Thoát ngay nếu trang tải lỗi hoặc editor đã được tạo
        
        # Đặt cờ thành True để ngăn việc chạy lại
        self.editor_initialized = True
        # <<< KẾT THÚC THAY ĐỔI

        print("DEBUG: editor.html đã tải. Bắt đầu tiêm CKEditor script...")

        try:
            with open(os.path.join("editTools", 'ckeditor.js'), 'r', encoding='utf-8') as f:
                ckeditor_script = f.read()
        except FileNotFoundError:
            print("LỖI: Không tìm thấy file 'ckeditor.js' trong thư mục editTools!")
            self.editor_initialized = False # Reset cờ nếu có lỗi để thử lại
            return

        init_script = """
            if (typeof ClassicEditor !== 'undefined' && !window.editorInstance) {
                ClassicEditor
                    // <<< SỬA TẠI ĐÂY: Bỏ toàn bộ khối cấu hình {...} đi
                    .create( document.querySelector( '#editor' ) )
                    .then( newEditor => {
                        window.editorInstance = newEditor;
                        console.log( 'THÀNH CÔNG: CKEditor chính đã được khởi tạo!' );
                    } )
                    .catch( error => {
                        console.error( 'Lỗi khi khởi tạo editor chính:', error );
                    } );
            }
        """
        self.rich_text_editor.page().runJavaScript(ckeditor_script, 
            lambda result: self.rich_text_editor.page().runJavaScript(init_script))
        
    def reset_and_clear_context(self):
        """
        Reset lại trạng thái và giao diện về mặc định mà không tải lại trang.
        """
        print("DEBUG: Đang reset và làm mới ngữ cảnh...")

        # 1. Reset các biến trạng thái
        self.current_exercise = None
        self.is_awaiting_guidance = False
        self.current_session_index = -1
        self.current_exercise_index = -1
        self.current_step_index = -1 # <<<<<<<<<<<<<<< THÊM DÒNG NÀY

        # 2. Dọn dẹp các ô nhập liệu và hiển thị
        self.clear_current_editor_content()
        self.clear_chat_interface() 

        self.lbl_level.setText("-")
        self.lbl_score.setText("-")

        if hasattr(self, 'left_panel_stack'):
            self.left_panel_stack.setCurrentIndex(0)
            

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
            
            # >>> THAY ĐỔI TẠI ĐÂY
            html_result = f"<pre>{html.escape(result)}</pre>"
            self.add_message_to_chat(html_result, "⚙️ Kết quả thực thi")
            self.enable_buttons()
            # <<< KẾT THÚC THAY ĐỔI
            
            # html_result = f"<h3>Kết quả thực thi:</h3><pre>{html.escape(result)}</pre>"
            # self.web_view.setHtml(html_result)
            # self.enable_buttons()

        self.disable_buttons()
        self.get_current_editor_content(run_code_process)

    # THAY THẾ TOÀN BỘ HÀM CŨ BẰNG HÀM NÀY
    def handle_gemini_response(self, response_text, was_retry):
        html_content, info, err = render_ai_json_markdown(response_text)

        if err and not was_retry:
            print("⚠️ Phản hồi JSON lỗi → Yêu cầu AI sửa lại.")
            re_prompt = RE_RESPONSE_PROMPT.format(error_message=str(err))
            self.run_gemini_in_thread(re_prompt, is_retry=True)
            return

        if err and was_retry:
            print("❌ Phản hồi vẫn lỗi sau khi đã thử lại.")

        message_type = "⚠️ Lỗi Phân Tích" if err else info.get("message_type", "💬 Tutor AI")
        self.add_message_to_chat(html_content, message_type)

        self.lbl_level.setText(str(info.get('level', '-')))
        self.lbl_score.setText(str(info.get('score', '-')))

        if self.current_exercise and self.current_exercise.get('id') != 'custom_exercise':
            status = "✓" if info.get('exercise_status') == 'completed' else "✗"
            score = str(info.get('score', 0))
            self.update_tree_item(self.current_exercise.get('id'), status, score)

            # --- LOGIC CẬP NHẬT GHIM ĐÃ SỬA LỖI ---
            if info.get('exercise_status') == 'completed':
                # Nếu toàn bộ bài tập hoàn thành, ghim thông báo hoàn thành.
                completion_text = "Chúc mừng bạn đã hoàn thành bài tập! Hãy nhấn 'Bài tiếp theo'."
                self.update_pinned_step_display(completion_text)
                self.current_step_index = -1 # Đánh dấu là đã xong
            # (Trong tương lai, chúng ta sẽ thêm logic xử lý khi một BƯỚC hoàn thành ở đây)
            # --- KẾT THÚC SỬA LỖI ---

        self.enable_buttons()
        
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
        PHIÊN BẢN TỐI ƯU HÓA THỨ TỰ THỰC THI.
        """
        exercise_data = item.data(0, Qt.ItemDataRole.UserRole)
        parent_item = item.parent()
        if not exercise_data or not isinstance(exercise_data, dict) or not parent_item:
            self.current_exercise = None
            return

        # --- BẮT ĐẦU LUỒNG XỬ LÝ TỐI ƯU ---
        # BƯỚC 1: Dọn dẹp giao diện cũ một cách triệt để
        self.clear_chat_interface()
        self.clear_current_editor_content()
        
        # BƯỚC 2: Thiết lập trạng thái cho bài tập mới
        self.current_exercise = exercise_data
        self.current_step_index = 0
        self.start_new_ai_conversation(is_custom_exercise=False)

        # BƯỚC 3: Cập nhật giao diện với thông tin của bài tập mới
        # Cập nhật và Ghim bước đầu tiên LÊN TRƯỚC
        # guidance = self.current_exercise.get("guidance", [])
        # first_step = guidance[0] if guidance else "Bắt đầu làm bài."
        # self.update_pinned_step_display(first_step)

        # Hiển thị đề bài ở khung trái
        self.display_exercise_in_left_panel(exercise_data)
        
        # Hiển thị tin nhắn chào mừng trong chat
        welcome_message = f"<h3>Bắt đầu: {self.current_exercise.get('title', '')}</h3><p>Đề bài đã được hiển thị ở khung bên trái. Hãy bắt đầu nhé!</p>"
        self.add_message_to_chat(welcome_message, "👋 Chào mừng")
        
        # BƯỚC 4: Cập nhật các thành phần phụ thuộc
        language = self.current_course_language.lower()
        is_programming_lang = language in ["c", "java", "python"]
        self.btn_run_code.setEnabled(is_programming_lang)
        
        self.lbl_level.setText("-")
        self.lbl_score.setText("-")

        # Chuyển đổi editor phù hợp
        if is_programming_lang:
            self.editor_stack.setCurrentIndex(self.plain_editor_index)
            self.highlighter = Highlighter(self.plain_code_editor.document(), language)
        else:
            if not self.editor_initialized:
                self.rich_text_editor.reload()
            self.editor_stack.setCurrentIndex(self.rich_editor_index)
            self.highlighter = None

    def find_next_step_text(self):
        """
        Tìm văn bản của bước hướng dẫn tiếp theo dựa trên tiến trình của người dùng.
        Hàm này cần được tùy chỉnh dựa trên cách bạn lưu tiến trình.
        Đây là một ví dụ đơn giản.
        """
        # Đây là ví dụ, bạn cần logic phức tạp hơn để theo dõi bước hiện tại
        return "Bạn đã hoàn thành bài! Hãy nhấn 'Bài tiếp theo'."

    def get_current_editor_content(self, callback):
        """
        Hàm hợp nhất để lấy nội dung từ editor đang hoạt động.
        'callback' là hàm sẽ được gọi với nội dung trả về.
        """
        current_index = self.editor_stack.currentIndex()
        
        if current_index == self.plain_editor_index:
            content = self.plain_code_editor.toPlainText()
            callback(content)
        elif current_index == self.rich_editor_index:
            # >>> SỬA TÊN BIẾN TẠI ĐÂY
            js_code = "window.editorInstance ? window.editorInstance.getData() : '';"
            # <<< KẾT THÚC
            self.rich_text_editor.page().runJavaScript(js_code, callback)

    def clear_current_editor_content(self):
        """Hàm hợp nhất để xóa nội dung của editor đang hoạt động."""
        current_index = self.editor_stack.currentIndex()
        
        if current_index == self.plain_editor_index:
            self.plain_code_editor.clear()
        elif current_index == self.rich_editor_index:
            # >>> SỬA TÊN BIẾN TẠI ĐÂY
            js_code = "if (window.editorInstance) { window.editorInstance.setData(''); }"
            # <<< KẾT THÚC
            self.rich_text_editor.page().runJavaScript(js_code)
            
    def on_custom_language_select(self, text):
        lang_map = {"C": "c", "Java": "java", "Python": "python", "Không": "text"}
        lang_code = lang_map.get(text, "text")
        self.current_exercise_language = lang_code
        print(f"Ngôn ngữ tùy chọn đã đổi thành: {lang_code}")

        if text == "Không":
            self.editor_stack.setCurrentIndex(self.rich_editor_index)
            self.btn_run_code.setEnabled(False)
            self.highlighter = None # Xóa highlighter khi không phải code
            print("DEBUG: Đã chuyển sang Rich Text Editor.")
        else:
            self.editor_stack.setCurrentIndex(self.plain_editor_index)
            self.btn_run_code.setEnabled(True)
            # KÍCH HOẠT HIGHLIGHTER CHO NGÔN NGỮ TƯƠNG ỨNG
            self.highlighter = Highlighter(self.plain_code_editor.document(), lang_code)
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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())