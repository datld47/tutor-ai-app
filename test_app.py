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
    QStackedWidget
)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QFontMetrics
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

# --- Import các file logic ---
from usercustomize import PATH_IMG, PATH_DATA, PATH_EDIT_TOOLS
import google.generativeai as genai
from compiler_c import compile_code, compile_java, run_python
from docx_importer import process_docx_to_json
import pyrebase
from login_gui import LoginApp
from login_gui_pyqt import LoginDialog
from api_key_dialog import ApiKeyDialog
from prompt.rule import create_main_rule
import html
from syntax_highlighter import Highlighter
import uuid
from PyQt6.QtWidgets import QDialog

# --- Khởi tạo cấu hình Firebase ---
firebaseConfig = {
  "apiKey": "AIzaSyAgTDYs03DJ8FOHjL0v_EfD4R3TQoPUheM",
  "authDomain": "tutoraiexercisesteps.firebaseapp.com",
  "databaseURL": "https://tutoraiexercisesteps-default-rtdb.firebaseio.com/",
  "projectId": "tutoraiexercisesteps",
  "storageBucket": "tutoraiexercisesteps.firebasestorage.app",
  "messagingSenderId": "396805630899",
  "appId": "1:396805630899:web:7ca9be22701f35589b79c6"
}

RE_RESPONSE_PROMPT = """
Phản hồi trước đó của bạn có JSON không hợp lệ và không thể được xử lý bằng `json.loads()` trong Python.
Lỗi cụ thể là: {error_message}

Vui lòng gửi lại toàn bộ phản hồi, sửa lại phần JSON để nó hợp lệ.
Toàn bộ phản hồi phải nằm trong block code ```json.
"""

# ==============================================================================
# SỬA LỖI RENDER CÔNG THỨC TOÁN TẠI ĐÂY
# ==============================================================================
# Trong file test_app.py

# Trong file test_app.py

def render_ai_json_markdown(response_text: str):
    """
    Chuyển đổi phản hồi JSON từ AI thành HTML.
    Hàm này đã được nâng cấp để chủ động sửa lỗi escape trong chuỗi JSON
    một cách chính xác, không làm ảnh hưởng đến các ký tự xuống dòng.
    """
    import html
    import markdown
    import re
    import json

    print("DEBUG: Gọi render_ai_json_markdown với nội dung:\n", response_text)

    try:
        # Tách chuỗi JSON từ phản hồi
        match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, flags=re.DOTALL)
        json_str = match.group(1) if match else response_text.strip()

        # ======================================================================
        # === GIẢI PHÁP CUỐI CÙNG - THAY ĐỔI BIỂU THỨC CHÍNH QUY TẠI ĐÂY ===
        # Regex này chỉ tìm và thay thế các dấu '\' không hợp lệ,
        # trong khi bỏ qua các chuỗi escape hợp lệ của JSON như \n, \t, \", \\.
        safe_json_str = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_str)
        # ======================================================================

        # Sử dụng chuỗi đã được làm sạch để phân tích JSON
        obj = json.loads(safe_json_str)

        data_text = obj.get("data", "")
        info = obj.get("info", {})

        # Chuyển đổi markdown thành HTML
        final_html = markdown.markdown(data_text, extensions=['fenced_code', 'tables', 'nl2br'])
        
        print("DEBUG - Nội dung HTML gửi ra:\n", final_html)
        return final_html, info, None

    except Exception as e:
        print(f"Lỗi trong render_ai_json_markdown: {e}")
        error_html = f"<p><b>Lỗi khi xử lý phản hồi từ AI:</b></p><pre>{html.escape(str(e))}</pre>"
        return error_html, {}, str(e)
# ==============================================================================
# KẾT THÚC PHẦN SỬA LỖI
# ==============================================================================


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

        filename = f"chem_{uuid.uuid4().hex}.svg"
        filepath = os.path.join(PATH_IMG, filename)

        try:
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
        self.setGeometry(200, 200, 800, 600)
        self.setMinimumSize(600, 400)

        self.latex_output = ""
        main_layout = QVBoxLayout(self)

        self.math_web_view = QWebEngineView()
        self.math_web_view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        mathlive_editor_path = os.path.abspath(os.path.join(PATH_EDIT_TOOLS, 'mathlive_editor.html'))
        self.math_web_view.setUrl(QUrl.fromLocalFile(mathlive_editor_path))
        self.math_web_view.loadFinished.connect(self._on_math_editor_loaded)
        main_layout.addWidget(self.math_web_view, stretch=1)

        button_layout = QHBoxLayout()
        self.insert_button = QPushButton("Chèn vào Editor")
        self.insert_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 16px; border-radius: 5px;")
        self.insert_button.clicked.connect(self._on_insert_clicked)

        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px 16px; border-radius: 5px;")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch(1)
        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.initial_latex = initial_latex

    def _on_math_editor_loaded(self, ok):
        if not ok:
            print("Lỗi: Không thể tải mathlive_editor.html")
            return
        self.math_web_view.setFocus()
        js_call = f"window.setInitialLatexAndFocus(`{self.initial_latex}`);"
        self.math_web_view.page().runJavaScript(js_call)
        print("MathLive Editor đã sẵn sàng và được khởi tạo.")

    def _on_insert_clicked(self):
        js_get_value = "window.mathEditorInstance.getValue();"
        self.math_web_view.page().runJavaScript(js_get_value, self._process_latex_value)

    def _process_latex_value(self, latex_value):
        self.latex_output = latex_value
        self.accept()

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
            safe_response_text = original_text
            self.history.append({'role': 'model', 'parts': [original_text]})
            self.finished.emit(safe_response_text, self.was_retry)
        except Exception as e:
            self.error.emit(str(e))

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap()
    def setOriginalPixmap(self, pixmap):
        self._pixmap = pixmap
        self.updatePixmap()
    def updatePixmap(self):
        if not self._pixmap.isNull():
            scaled_pixmap = self._pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            super().setPixmap(scaled_pixmap)
    def resizeEvent(self, event):
        self.updatePixmap()
        super().resizeEvent(event)
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class ImageViewer(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Xem ảnh - " + os.path.basename(image_path))
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(image_path)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        scaled_pixmap = pixmap.scaled(int(screen_geometry.width() * 0.9), int(screen_geometry.height() * 0.9), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        self.resize(scaled_pixmap.width() + 20, scaled_pixmap.height() + 20)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutor AI - V1.1")
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
        self.firebase = None
        self.auth = None
        self.db = None
        self.user_info = {}
        self.is_logged_in = False
        self.chat_interface_ready = False
        self.js_call_queue = []
        self.current_session_index = -1
        self.current_step_index = -1
        self.editor_initialized = False
        self.custom_editor_initialized = False
        self.highlighter = None

        # --- Xây dựng giao diện ---
        self.build_menus_and_toolbar()
        self.build_formatting_toolbar()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)
        self.fr_left = QWidget()
        self.fr_center = QWidget()
        self.fr_right = QWidget()
        self.splitter.addWidget(self.fr_left)
        self.splitter.addWidget(self.fr_center)
        self.splitter.addWidget(self.fr_right)
        self.splitter.setSizes([400, 800, 400])
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(2, 0)

        self.editor_stack = QStackedWidget()
        self.plain_code_editor = QPlainTextEdit()
        self.rich_text_editor = QWebEngineView()
        self.custom_exercise_editor = QWebEngineView()

        self.build_left_panel()
        self.build_center_panel()
        self.build_right_panel()
        self.connect_signals()
        self.load_initial_data()
        self.on_custom_language_select(self.lang_combobox.currentText())
        self.showMaximized()
    
    # --- Các hàm và phương thức khác của MainWindow (giữ nguyên) ---
    # ... (Toàn bộ các hàm còn lại như build_menus_and_toolbar, build_left_panel, on_submit_code_click, v.v.
    #      sẽ được dán vào đây mà không cần thay đổi)
    
    def on_open_math_editor(self):
        initial_latex = "" 
        dialog = MathEditorDialog(self, initial_latex=initial_latex)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            latex_content = dialog.get_latex_output()
            if latex_content:
                html_to_insert = f'<p>\\({latex_content}\\)</p>'
                js_insert_html = f"window.editorInstance.model.change(writer => {{ writer.insertHtml('{html_to_insert}', writer.model.document.selection); }});"
                self.rich_text_editor.page().runJavaScript(js_insert_html)
                
                if self.editor_stack.currentIndex() == self.plain_editor_index:
                    cursor = self.plain_code_editor.textCursor()
                    cursor.insertText(f"\\({latex_content}\\)")
                    self.plain_code_editor.setTextCursor(cursor)
                
                print(f"Đã chèn LaTeX: {latex_content}")
        self.rich_text_editor.page().runJavaScript("window.editorInstance.editing.view.focus();")

    def build_formatting_toolbar(self):
        self.formatting_toolbar = QToolBar("Formatting Toolbar")
        self.formatting_toolbar.setObjectName("FormattingToolbar")
        self.action_bold = QAction(QIcon(os.path.join(PATH_IMG, 'bold.png')), "In đậm (Ctrl+B)", self)
        self.action_italic = QAction(QIcon(os.path.join(PATH_IMG, 'italic.png')), "In nghiêng (Ctrl+I)", self)
        self.action_bulleted_list = QAction(QIcon(os.path.join(PATH_IMG, 'bulleted-list.png')), "Danh sách gạch đầu dòng", self)
        self.action_numbered_list = QAction(QIcon(os.path.join(PATH_IMG, 'numbered-list.png')), "Danh sách có thứ tự", self)
        self.action_superscript = QAction(QIcon(os.path.join(PATH_IMG, 'superscript.png')), "Chỉ số trên", self)
        self.action_subscript = QAction(QIcon(os.path.join(PATH_IMG, 'subscript.png')), "Chỉ số dưới", self)
        self.formatting_toolbar.addAction(self.action_bold)
        self.formatting_toolbar.addAction(self.action_italic)
        self.formatting_toolbar.addSeparator()
        self.formatting_toolbar.addAction(self.action_bulleted_list)
        self.formatting_toolbar.addAction(self.action_numbered_list)
        self.formatting_toolbar.addAction(self.action_superscript)
        self.formatting_toolbar.addAction(self.action_subscript)
        self.formatting_toolbar.addSeparator()
        self.formatting_toolbar.setVisible(False)
        self.addToolBar(self.formatting_toolbar)

    def on_format_bold(self): self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('bold');")
    def on_format_italic(self): self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('italic');")
    def on_format_bulleted_list(self): self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('bulletedList');")
    def on_format_numbered_list(self): self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('numberedList');")
    def on_format_superscript(self): self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('superscript');")
    def on_format_subscript(self): self.rich_text_editor.page().runJavaScript("window.editorInstance.execute('subscript');")

    def on_custom_editor_load_finished(self, ok):
        if not ok or self.custom_editor_initialized: return
        self.custom_editor_initialized = True
        print("DEBUG: custom_editor.html đã tải. Bắt đầu tiêm CKEditor script...")
        try:
            with open(os.path.join(PATH_EDIT_TOOLS, 'ckeditor.js'), 'r', encoding='utf-8') as f:
                ckeditor_script = f.read()
        except FileNotFoundError:
            print(f"LỖI: Không tìm thấy file 'ckeditor.js' trong thư mục {PATH_EDIT_TOOLS}!")
            self.custom_editor_initialized = False
            return
        init_script = """
            if (typeof ClassicEditor !== 'undefined' && !window.customEditorInstance) {
                ClassicEditor
                    .create( document.querySelector( '#custom-editor' ) )
                    .then( newEditor => {
                        window.customEditorInstance = newEditor;
                        console.log('THÀNH CÔNG: CKEditor cho đề bài đã được khởi tạo!');
                    } )
                    .catch( error => { console.error('Lỗi khi khởi tạo custom editor:', error ); } );
            }
        """
        self.custom_exercise_editor.page().runJavaScript(ckeditor_script, lambda result: self.custom_exercise_editor.page().runJavaScript(init_script))

    def on_chat_view_loaded(self, success):
        if success:
            print("✅ Giao diện chat đã sẵn sàng.")
            self.chat_interface_ready = True
            for js_code in self.js_call_queue:
                self.web_view.page().runJavaScript(js_code)
            self.js_call_queue.clear()
        else:
            print("❌ Lỗi: Không thể tải file chat_view.html.")

    def save_last_working_key(self, key):
        print(f"DEBUG: Cần cập nhật logic lưu key '{key}' vào config.json")

    def find_working_api_key(self, keys_to_check):
        print("DEBUG: Bắt đầu tìm kiếm API key đang hoạt động...")
        for key in keys_to_check:
            try:
                genai.configure(api_key=key)
                genai.GenerativeModel('gemini-1.5-flash')
                print(f"DEBUG: Tìm thấy key hoạt động: ...{key[-4:]}")
                self.save_last_working_key(key)
                return key
            except Exception as e:
                print(f"DEBUG: Key ...{key[-4:]} không hoạt động. Lỗi: {e}")
                continue
        print("CẢNH BÁO: Không tìm thấy API key nào hoạt động trong danh sách.")
        return None

    def reinitialize_gemini_model(self):
        working_key = self.find_working_api_key(self.API_KEY_LIST)
        if working_key:
            self.API_KEY = working_key
            genai.configure(api_key=self.API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            if hasattr(self, 'worker'):
                self.worker.model = self.model
            print(f"Đã áp dụng API Key mới: ...{self.API_KEY[-4:]}")
        else:
            QMessageBox.critical(self, "Không có API Key", "Không có API Key nào trong danh sách mới hoạt động.")

    def update_user_info_callback(self, username, mssv, token):
        self.is_logged_in = True
        self.user_info = {'username': username, 'uid': mssv, 'token': token}
        self.login_button.setText(f"👤 Xin chào, {username}!")
        print(f"Người dùng {username} (UID: {mssv}) đã đăng nhập.")

    def update_api_key_callback(self, uid):
        if not self.db or not self.user_info.get('token'):
            print("DEBUG: Chưa sẵn sàng để tải API key (thiếu DB hoặc token).")
            return
        try:
            token = self.user_info['token']
            user_data = self.db.child("users").child(uid).get(token=token).val()
            user_keys = user_data.get('gemini_api_keys') if user_data else None
            if user_keys and isinstance(user_keys, list) and len(user_keys) > 0:
                print(f"DEBUG: Tìm thấy {len(user_keys)} API key cá nhân. Đang áp dụng...")
                self.API_KEY_LIST = user_keys
                self.reinitialize_gemini_model()
            else:
                print("DEBUG: Người dùng chưa có API key cá nhân, dùng key mặc định.")
                self.load_default_api_keys()
                self.reinitialize_gemini_model()
        except Exception as e:
            print(f"Lỗi khi tải API key cá nhân: {e}")
            self.load_default_api_keys()
            self.reinitialize_gemini_model()

    def load_default_api_keys(self):
        try:
            with open(os.path.join(PATH_DATA, 'config.json'), "r", encoding="utf-8") as file:
                config = json.load(file)
            default_keys = config.get('api', [{}])[0].get('gemini_key', [])
            self.API_KEY_LIST = default_keys
            print(f"DEBUG: Đã tải {len(self.API_KEY_LIST)} API key mặc định.")
        except Exception as e:
            print(f"Lỗi khi tải API key mặc định từ config.json: {e}")
            self.API_KEY_LIST = []

    def on_open_chem_editor(self):
        dialog = KekuleEditorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            image_path = dialog.get_svg_path()
            if image_path:
                file_url = QUrl.fromLocalFile(os.path.abspath(image_path)).toString()
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
        self.action_manage_api_keys = QAction("Quản lý Gemini API...", self)
        tool_menu.addAction(self.action_manage_api_keys)
        self.action_math_editor = QAction(QIcon(os.path.join(PATH_IMG, 'math.png')), "Chèn công thức toán học", self)
        toolbar.addAction(self.action_math_editor)
        self.action_chem_editor = QAction(QIcon(os.path.join(PATH_IMG, 'chemistry.png')), "Soạn công thức hóa học", self)
        toolbar.addAction(self.action_chem_editor)
        tool_menu.addAction(self.action_math_editor)
        tool_menu.addAction(self.action_chem_editor)
        action_exit.triggered.connect(self.close)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        self.login_button = QPushButton("🚀 Đăng nhập")
        self.login_button.setStyleSheet("font-weight: bold; border: none; padding: 5px;")
        toolbar.addWidget(self.login_button)
        help_menu = menu.addMenu("&Trợ giúp")
        action_about = QAction("Giới thiệu", self)
        help_menu.addAction(action_about)
        action_about.triggered.connect(self.on_about)

    def on_about(self):
        QMessageBox.about(self, "Giới thiệu Tutor AI", "<b>Tutor AI (PyQt Version)</b><br>Phiên bản: 2.0<br><br>Ứng dụng hỗ trợ học tập được phát triển bằng PyQt6.")

    def run_gemini_in_thread(self, prompt, is_retry=False):
        self.thread = QThread()
        self.worker = GeminiWorker(self.model, self.history)
        self.worker.prompt = prompt
        self.worker.was_retry = is_retry
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_gemini_response)
        self.worker.error.connect(self.handle_gemini_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def disable_buttons(self):
        self.btn_submit_code.setEnabled(False)
        self.btn_ai_help.setEnabled(False)

    def enable_buttons(self):
        self.btn_submit_code.setEnabled(True)
        self.btn_ai_help.setEnabled(True)
        is_runnable = False
        if self.current_exercise:
            if self.current_exercise.get('id') == 'custom_exercise':
                if self.lang_combobox.currentText() != "Không":
                    is_runnable = True
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
        custom_layout = QVBoxLayout(tab_custom)
        custom_layout.addWidget(QLabel("Chọn ngôn ngữ lập trình (tùy chọn):"))
        self.lang_combobox = QComboBox()
        self.lang_combobox.addItems(["Không", "C", "Java", "Python"])
        self.lang_combobox.setCurrentText("Không")
        custom_layout.addWidget(self.lang_combobox)
        custom_layout.addWidget(QLabel("Nhập đề bài hoặc yêu cầu của bạn:"))
        editor_path = os.path.join(PATH_EDIT_TOOLS, 'custom_editor.html')
        self.custom_exercise_editor.setUrl(QUrl.fromLocalFile(os.path.abspath(editor_path)))
        custom_layout.addWidget(self.custom_exercise_editor, stretch=1)
        self.btn_start_custom = QPushButton("Bắt đầu & Hướng dẫn")
        custom_layout.addWidget(self.btn_start_custom)
        self.build_course_tab(tab_course)

    def on_start_custom_exercise(self):
        def process_description(description_html):
            temp_doc = QTextBrowser()
            temp_doc.setHtml(description_html)
            plain_text = temp_doc.toPlainText().strip()
            if not plain_text:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đề bài trước khi bắt đầu.")
                return
            print("Starting custom exercise...")
            self.current_exercise = {"id": "custom_exercise", "title": "Bài tập tự do", "description": description_html, "course_name": "Bài tập tự do"}
            self.display_exercise_in_left_panel(self.current_exercise)
            self.clear_current_editor_content()
            self.start_new_ai_conversation(is_custom_exercise=True)
            welcome_html_content = (f"<h3>Bắt đầu bài tập: {self.current_exercise.get('title', '')}</h3><p>Đề bài của bạn đã được hiển thị ở khung bên trái.</p>")
            self.clear_chat_interface()
            self.add_message_to_chat(welcome_html_content, "👋 Chào mừng")
            self.lbl_level.setText("-")
            self.lbl_score.setText("-")
        js_code = "window.customEditorInstance ? window.customEditorInstance.getData() : '';"
        self.custom_exercise_editor.page().runJavaScript(js_code, process_description)

    def build_course_tab(self, parent_tab):
        layout = QVBoxLayout(parent_tab)
        layout.addWidget(QLabel("Chọn môn học:"))
        self.course_combobox = QComboBox()
        layout.addWidget(self.course_combobox)
        self.left_panel_stack = QStackedWidget()
        layout.addWidget(self.left_panel_stack, stretch=1)
        tree_widget_container = QWidget()
        tree_layout = QVBoxLayout(tree_widget_container)
        tree_layout.setContentsMargins(0,0,0,0)
        self.exercise_tree = QTreeWidget()
        self.exercise_tree.setHeaderLabels(["Buổi và tên bài", "Trạng thái", "Điểm"])
        self.exercise_tree.setColumnWidth(0, 200)
        tree_layout.addWidget(self.exercise_tree)
        self.left_panel_stack.addWidget(tree_widget_container)

    def navigate_to_next_exercise(self):
        if not self.current_exercise or not self.json_course: return
        current_id = self.current_exercise.get('id')
        found_current = False
        for session in self.json_course.get("sessions", []):
            for exercise in session.get("exercises", []):
                if found_current:
                    print(f"Navigating to next exercise: {exercise.get('title')}")
                    iterator = QTreeWidgetItemIterator(self.exercise_tree)
                    while iterator.value():
                        item = iterator.value()
                        item_data = item.data(0, Qt.ItemDataRole.UserRole)
                        if item_data and item_data.get('id') == exercise.get('id'):
                            self.on_exercise_selected(item, 0)
                            return
                        iterator += 1
                if exercise.get('id') == current_id:
                    found_current = True
        QMessageBox.information(self, "Hoàn thành", "Chúc mừng! Bạn đã hoàn thành bài tập cuối cùng của khóa học.")

    def display_exercise_in_left_panel(self, exercise_data):
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        title_label = QLabel(exercise_data["title"])
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_label.setWordWrap(True)
        details_layout.addWidget(title_label)
        desc_browser = QTextBrowser()
        desc_browser.setOpenExternalLinks(True)
        description_html = exercise_data["description"].replace('\n', '<br>')
        desc_browser.setHtml(f"<p>{description_html}</p>")
        details_layout.addWidget(desc_browser, 1)
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
                    image_label.clicked.connect(lambda path=image_path: self.show_image_viewer(path))
                    caption = image_info.get("image_title", "")
                    caption_label = QLabel(f'<i>{caption}</i>')
                    caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    details_layout.addWidget(image_label)
                    details_layout.addWidget(caption_label)
                else:
                    error_label = QLabel(f"<font color='red'>Lỗi: Không tìm thấy ảnh '{image_filename}'</font>")
                    details_layout.addWidget(error_label)
        button_layout = QHBoxLayout()
        back_button = QPushButton("⬅ Quay lại")
        next_button = QPushButton("Bài tiếp theo ➡")
        button_layout.addWidget(back_button)
        button_layout.addStretch()
        button_layout.addWidget(next_button)
        details_layout.addLayout(button_layout)
        new_page_index = self.left_panel_stack.addWidget(details_widget)
        self.left_panel_stack.setCurrentIndex(new_page_index)
        def go_back():
            self.left_panel_stack.setCurrentIndex(0)
            self.left_panel_stack.removeWidget(details_widget)
            details_widget.deleteLater()
        back_button.clicked.connect(go_back)
        next_button.clicked.connect(self.navigate_to_next_exercise)

    def show_image_viewer(self, image_path):
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy file ảnh tại:\n{image_path}")
            return
        viewer = ImageViewer(image_path, self)
        viewer.exec()

    def build_center_panel(self):
        layout = QVBoxLayout(self.fr_center)
        title_label = QLabel("Bài làm")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        self.plain_code_editor.setStyleSheet("font-family: Consolas, Courier New; font-size: 14px;")
        font = self.plain_code_editor.font()
        font_metrics = QFontMetrics(font)
        tab_stop_width = font_metrics.horizontalAdvance(' ' * 8)
        self.plain_code_editor.setTabStopDistance(tab_stop_width)
        self.rich_text_editor.loadFinished.connect(self.on_editor_load_finished)
        editor_path = os.path.join(PATH_EDIT_TOOLS, 'editor.html')
        self.rich_text_editor.setUrl(QUrl.fromLocalFile(os.path.abspath(editor_path)))
        self.plain_editor_index = self.editor_stack.addWidget(self.plain_code_editor)
        self.rich_editor_index = self.editor_stack.addWidget(self.rich_text_editor)
        layout.addWidget(title_label)
        layout.addWidget(self.editor_stack, stretch=1)
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

    # Trong file test_app.py

    # THAY THẾ TOÀN BỘ HÀM CŨ BẰNG HÀM NÀY
    def add_message_to_chat(self, html_content, message_type=""):
        """
        Gửi một tin nhắn mới vào giao diện chat một cách an toàn.
        Sử dụng json.dumps để đảm bảo các ký tự đặc biệt (như '\' trong LaTeX)
        được truyền sang JavaScript một cách chính xác.
        """
        # Sử dụng json.dumps để tuần tự hóa chuỗi HTML và tiêu đề một cách an toàn
        safe_html = json.dumps(html_content)
        safe_type = json.dumps(message_type)
        
        # Tạo mã JavaScript để gọi hàm addAiMessage với dữ liệu đã được tuần tự hóa
        js_code = f"addAiMessage({safe_html}, {safe_type});"

        # Gửi mã JavaScript tới QWebEngineView
        if self.chat_interface_ready:
            self.web_view.page().runJavaScript(js_code)
        else:
            # Xếp hàng nếu giao diện chưa sẵn sàng
            self.js_call_queue.append(js_code)
            
        # Log này chỉ để gỡ lỗi, cho thấy HTML gốc trước khi gửi
        print("DEBUG - HTML gửi vào chat:", html_content)

    def update_pinned_step_display(self, step_text=""):
        content = ""
        if step_text:
            content = f"<strong>Bước hiện tại:</strong> {html.escape(step_text)}"
        escaped_content = json.dumps(content)
        js_code = f"updatePinnedStep({escaped_content});"
        if self.chat_interface_ready:
            self.web_view.page().runJavaScript(js_code)
        else:
            self.js_call_queue.append(js_code)

    def clear_chat_interface(self):
        self.js_call_queue.clear()
        js_clear_code = "document.getElementById('chat-container').innerHTML = '';"
        if self.chat_interface_ready:
            self.web_view.page().runJavaScript(js_clear_code)
        else:
            self.js_call_queue.append(js_clear_code)
        self.update_pinned_step_display()

    def build_right_panel(self):
        layout = QVBoxLayout(self.fr_right)
        title_label = QLabel("AI Hướng dẫn")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: green; color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title_label)
        self.web_view = QWebEngineView()
        self.web_view.loadFinished.connect(self.on_chat_view_loaded)
        chat_view_path = os.path.abspath("chat_view.html")
        self.web_view.setUrl(QUrl.fromLocalFile(chat_view_path))
        layout.addWidget(self.web_view, stretch=1)
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

    def handle_login_logout(self):
        if not self.is_logged_in:
            if not self.auth or not self.db:
                QMessageBox.critical(self, "Lỗi", "Kết nối Firebase chưa sẵn sàng.")
                return
            login_dialog = LoginDialog(self, self.auth, self.db)
            if login_dialog.exec() == QDialog.DialogCode.Accepted:
                user_data = login_dialog.user_info
                self.update_user_info_callback(user_data['username'], user_data['uid'], user_data['token'])
                self.update_api_key_callback(user_data['uid'])
        else:
            reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn đăng xuất?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.is_logged_in = False
                self.user_info = {}
                self.login_button.setText("🚀 Đăng nhập / Đăng ký")
                self.load_initial_data()
                print("Đã đăng xuất và tải lại cấu hình mặc định.")

    def connect_signals(self):
        self.btn_submit_code.clicked.connect(self.on_submit_code_click)
        self.btn_ai_help.clicked.connect(self.on_ai_help_click)
        self.exercise_tree.itemClicked.connect(self.on_exercise_selected)
        self.action_import_word.triggered.connect(self.on_import_word)
        self.btn_run_code.clicked.connect(self.on_run_code_click)
        self.lang_combobox.currentTextChanged.connect(self.on_custom_language_select)
        self.login_button.clicked.connect(self.handle_login_logout)
        self.action_manage_api_keys.triggered.connect(self.on_manage_api_keys)
        self.btn_start_custom.clicked.connect(self.on_start_custom_exercise)
        self.custom_exercise_editor.loadFinished.connect(self.on_custom_editor_load_finished)
        self.action_bold.triggered.connect(self.on_format_bold)
        self.action_italic.triggered.connect(self.on_format_italic)
        self.action_bulleted_list.triggered.connect(self.on_format_bulleted_list)
        self.action_numbered_list.triggered.connect(self.on_format_numbered_list)
        self.action_superscript.triggered.connect(self.on_format_superscript)
        self.action_subscript.triggered.connect(self.on_format_subscript)
        self.action_math_editor.triggered.connect(self.on_open_math_editor)
        self.action_chem_editor.triggered.connect(self.on_open_chem_editor)

    def on_manage_api_keys(self):
        dialog = ApiKeyDialog(self, self.API_KEY_LIST, self.is_logged_in, self.user_info, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("API Keys đã được cập nhật.")
            self.API_KEY_LIST = dialog.saved_keys
            self.reinitialize_gemini_model()

    def load_initial_data(self):
        try:
            self.firebase = pyrebase.initialize_app(firebaseConfig)
            self.auth = self.firebase.auth()
            self.db = self.firebase.database()
            print("DEBUG: Kết nối Firebase thành công.")
        except Exception as e:
            print(f"Lỗi khởi tạo Firebase: {e}")
            QMessageBox.critical(self, "Lỗi Firebase", f"Không thể kết nối đến Firebase: {e}")
        try:
            with open(os.path.join(PATH_DATA, 'rule.md'), 'r', encoding='utf-8') as f: self.main_rule = f.read()
            with open(os.path.join(PATH_DATA, 'rule_lesson.md'), 'r', encoding='utf-8') as f: self.main_rule_lesson = f.read()
            with open(os.path.join(PATH_DATA, 'prompt.md'), 'r', encoding='utf-8') as f: self.prompt_template = f.read()
        except Exception as e: print(f"Lỗi tải các file rule hoặc prompt: {e}")
        self.load_all_course_data()
        self.load_default_api_keys()
        self.reinitialize_gemini_model()

    def on_submit_code_click(self):
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
            grading_instructions = (f"Phân tích và đánh giá bài làm của người học dưới đây. Đưa ra nhận xét, chỉ ra điểm đúng, điểm sai (nếu có). Nếu bài làm chưa hoàn thiện, hãy đặt câu hỏi gợi mở để người học tự sửa. Tuyệt đối không viết code đáp án. Lưu ý: Không cần nhắc lại tên bài tập hay đề bài trong phần phản hồi.")
            student_submission_block = (f"# Bài làm của người học:\n```{self.current_exercise_language}\n{user_content}\n```\n")
            full_prompt = self.prompt_template.format(exercise_context=(f"Môn học: {course_name}\nBài tập: {self.current_exercise.get('title', 'N/A')}\nĐề bài: {self.current_exercise.get('description', 'N/A')}\n\n"), step_by_step_guidance=grading_instructions, student_submission=student_submission_block)
            lang = self.current_course_language.lower()
            rule_base = self.main_rule_lesson if (self.current_exercise.get('id') == 'custom_exercise' or lang not in ["c", "java", "python"]) else self.main_rule
            final_prompt = create_main_rule(rule_base, full_prompt, course_name, self.current_exercise_language)
            if 'score' in self.current_exercise and self.current_exercise.get('score', 0) > 0: self.current_exercise['score'] -= 1
            self.run_gemini_in_thread(final_prompt)
        self.disable_buttons()
        self.get_current_editor_content(process_submission)

    def start_new_ai_conversation(self, is_custom_exercise=False):
        self.history.clear()
        initial_prompt = ""
        if is_custom_exercise:
            lang = self.current_exercise_language if self.current_exercise_language != "text" else "chung"
            initial_prompt = self.main_rule_lesson.replace('{language_placeholder}', lang)
        elif self.json_course:
            course_name = self.json_course.get('course_name', 'Không xác định')
            course_lang = self.json_course.get('course_language', 'Không xác định')
            initial_prompt = create_main_rule(self.main_rule, "", course_name, course_lang)
        if initial_prompt:
            initial_context = [{'role': 'user', 'parts': [initial_prompt]}, {'role': 'model', 'parts': ["OK, tôi đã hiểu vai trò của mình và sẵn sàng hướng dẫn."]}]
            self.history.extend(initial_context)
            print("DEBUG: Đã thiết lập vai trò Tutor AI vào lịch sử hội thoại.")

    def on_ai_help_click(self):
        def process_help_request(user_content):
            if not self.current_exercise:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một bài tập trước.")
                self.enable_buttons()
                return
            course_name = self.json_course.get('course_name', 'Không xác định') if self.json_course else 'Bài tập tự do'
            guidance = self.current_exercise.get("guidance") or self.current_exercise.get("generated_guidance")
            guidance_prompt_block = ""
            if guidance:
                print("DEBUG: Đã có hướng dẫn, yêu cầu AI tóm tắt theo các bước có sẵn.")
                formatted_guidance = "\n".join([f"{i+1}. {step}" for i, step in enumerate(guidance)])
                if user_content.strip():
                    guidance_prompt_block = (f"Dưới đây là các bước hướng dẫn giải bài tập này:\n{formatted_guidance}\n\nDựa vào bài làm hiện tại của người học và các bước hướng dẫn trên, hãy đưa ra một gợi ý nhỏ hoặc đặt câu hỏi để giúp họ tiến tới bước tiếp theo. Tuyệt đối không viết code đáp án và không nhắc lại đề bài.")
                else:
                    guidance_prompt_block = (f"**Nhiệm vụ của bạn là diễn giải lại các bước hướng dẫn đã có sẵn dưới đây một cách tổng quan cho người mới bắt đầu. TUYỆT ĐỐI KHÔNG TẠO RA CÁC BƯỚC MỚI.**\n\n**Các bước hướng dẫn có sẵn:**\n{formatted_guidance}\n\n**Yêu cầu:**\n- Bắt đầu phản hồi trực tiếp bằng mục 'Hướng dẫn tổng quát'.\n\n- Diễn giải lại các bước trên bằng ngôn ngữ thân thiện, dễ hiểu, mỗi bước trên một dòng riêng biệt.\n- Không đưa ra code đáp án và không nhắc lại đề bài.`\"**Hướng dẫn:**\\n\\n1. Đây là bước một.\\n2. Đây là bước hai.")
            else:
                print("DEBUG: Chưa có hướng dẫn, yêu cầu AI tạo ra các bước thông minh hơn.")
                self.is_awaiting_guidance = True
                guidance_prompt_block = (f"Bài tập này chưa có các bước hướng dẫn chi tiết. Nhiệm vụ của bạn là:\n1. Phân tích đề bài và tự tạo ra một danh sách các bước hướng dẫn chung nhất, KHÔNG được đưa ra lời giải. **QUY TẮC SƯ PHẠM CỐT LÕI: Luôn đề xuất giải pháp tối giản nhất. Đối với các bài tập chỉ yêu cầu in ra dữ liệu cố định (static data), TUYỆT ĐỐI KHÔNG hướng dẫn tạo biến. Thay vào đó, hãy hướng dẫn người học sử dụng trực tiếp lệnh `print()` với các giá trị chuỗi/số.**\n2. Trình bày các bước đó trong trường 'data' theo đúng định dạng Markdown sau:\n   - **KHÔNG lặp lại tên bài tập hay đề bài.**\n   - Bắt đầu trực tiếp bằng mục 'Hướng dẫn' (`**Hướng dẫn:**`).\n   - Liệt kê các bước dưới dạng danh sách có thứ tự (1., 2., 3.), **MỖI BƯỚC PHẢI CÓ KÝ TỰ XUỐNG DÒNG (\\n) ở cuối.**\n3. Trong trường 'info' của JSON, BẮT BUỘC phải có khóa 'generated_steps' chứa một MẢNG các chuỗi string, mỗi chuỗi là một bước hướng dẫn.\n   `\"**Hướng dẫn:**\\n\\n1. Đây là bước một.\\n2. Đây là bước hai.")
            student_submission_prompt = f"# Bài làm hiện tại của người học:\n```{self.current_exercise_language}\n{user_content}\n```" if user_content.strip() else ""
            full_prompt = self.prompt_template.format(exercise_context=(f"Môn học: {course_name}\nBài tập: {self.current_exercise.get('title', 'N/A')}\nĐề bài: {self.current_exercise.get('description', 'N/A')}\n"), step_by_step_guidance=guidance_prompt_block, student_submission=student_submission_prompt)
            lang = self.current_course_language.lower()
            rule_base = self.main_rule_lesson if (self.current_exercise.get('id') == 'custom_exercise' or lang not in ["c", "java", "python"]) else self.main_rule
            final_prompt = create_main_rule(rule_base, full_prompt, course_name, self.current_exercise_language)
            self.run_gemini_in_thread(final_prompt)
        self.disable_buttons()
        self.get_current_editor_content(process_help_request)

    def on_editor_load_finished(self, ok):
        if not ok or self.editor_initialized: return
        self.editor_initialized = True
        print("DEBUG: editor.html đã tải. Bắt đầu tiêm CKEditor script...")
        try:
            with open(os.path.join("editTools", 'ckeditor.js'), 'r', encoding='utf-8') as f:
                ckeditor_script = f.read()
        except FileNotFoundError:
            print("LỖI: Không tìm thấy file 'ckeditor.js' trong thư mục editTools!")
            self.editor_initialized = False
            return
        init_script = """
            if (typeof ClassicEditor !== 'undefined' && !window.editorInstance) {
                ClassicEditor
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
        self.rich_text_editor.page().runJavaScript(ckeditor_script, lambda result: self.rich_text_editor.page().runJavaScript(init_script))

    def reset_and_clear_context(self):
        print("DEBUG: Đang reset và làm mới ngữ cảnh...")
        self.current_exercise = None
        self.is_awaiting_guidance = False
        self.current_session_index = -1
        self.current_step_index = -1
        self.clear_current_editor_content()
        self.clear_chat_interface()
        self.lbl_level.setText("-")
        self.lbl_score.setText("-")
        if hasattr(self, 'left_panel_stack'): self.left_panel_stack.setCurrentIndex(0)

    def on_run_code_click(self):
        def run_code_process(content):
            from PyQt6.QtGui import QTextDocument
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
            language = self.current_course_language.lower() if self.current_exercise and self.current_exercise.get('id') != 'custom_exercise' else self.current_exercise_language.lower()
            if language not in ["c", "java", "python"]:
                QMessageBox.information(self, "Thông báo", f"Chức năng chạy code không hỗ trợ cho ngôn ngữ '{language}'.")
                self.enable_buttons()
                return
            result = ""
            if language == "c": result = compile_code(code)
            elif language == "java": result = compile_java(code)
            elif language == "python": result = run_python(code)
            html_result = f"<pre>{html.escape(result)}</pre>"
            self.add_message_to_chat(html_result, "⚙️ Kết quả thực thi")
            self.enable_buttons()
        self.disable_buttons()
        self.get_current_editor_content(run_code_process)

    def handle_gemini_response(self, response_text, was_retry):
        html_content, info, err = render_ai_json_markdown(response_text)
        if err and not was_retry:
            print("⚠️ Phản hồi JSON lỗi → Yêu cầu AI sửa lại.")
            re_prompt = RE_RESPONSE_PROMPT.format(error_message=str(err))
            self.run_gemini_in_thread(re_prompt, is_retry=True)
            return
        if err and was_retry: print("❌ Phản hồi vẫn lỗi sau khi đã thử lại.")
        message_type = "⚠️ Lỗi Phân Tích" if err else info.get("message_type", "💬 Tutor AI")
        self.add_message_to_chat(html_content, message_type)
        self.lbl_level.setText(str(info.get('level', '-')))
        self.lbl_score.setText(str(info.get('score', '-')))
        if self.current_exercise and self.current_exercise.get('id') != 'custom_exercise':
            status = "✓" if info.get('exercise_status') == 'completed' else "✗"
            score = str(info.get('score', 0))
            self.update_tree_item(self.current_exercise.get('id'), status, score)
            if info.get('exercise_status') == 'completed':
                completion_text = "Chúc mừng bạn đã hoàn thành bài tập! Hãy nhấn 'Bài tiếp theo'."
                self.update_pinned_step_display(completion_text)
                self.current_step_index = -1
        self.enable_buttons()

    def update_tree_item(self, exercise_id, status, score):
        iterator = QTreeWidgetItemIterator(self.exercise_tree)
        while iterator.value():
            item = iterator.value()
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data and isinstance(item_data, dict) and item_data.get('id') == exercise_id:
                item.setText(1, status)
                item.setText(2, score)
                item_data['status'] = status
                item_data['score'] = int(score)
                item.setData(0, Qt.ItemDataRole.UserRole, item_data)
                break
            iterator += 1

    def handle_gemini_error(self, error_text):
        self.web_view.setHtml(f"<h1>Lỗi</h1><p>{error_text}</p>")
        self.enable_buttons()

    def on_exercise_selected(self, item, column):
        exercise_data = item.data(0, Qt.ItemDataRole.UserRole)
        parent_item = item.parent()
        if not exercise_data or not isinstance(exercise_data, dict) or not parent_item:
            self.current_exercise = None
            return
        self.clear_chat_interface()
        self.clear_current_editor_content()
        self.current_exercise = exercise_data
        self.current_step_index = 0
        self.start_new_ai_conversation(is_custom_exercise=False)
        self.display_exercise_in_left_panel(exercise_data)
        welcome_message = f"<h3>Bắt đầu: {self.current_exercise.get('title', '')}</h3><p>Đề bài đã được hiển thị ở khung bên trái. Hãy bắt đầu nhé!</p>"
        self.add_message_to_chat(welcome_message, "👋 Chào mừng")
        language = self.current_course_language.lower()
        is_programming_lang = language in ["c", "java", "python"]
        self.btn_run_code.setEnabled(is_programming_lang)
        self.lbl_level.setText("-")
        self.lbl_score.setText("-")
        if is_programming_lang:
            self.editor_stack.setCurrentIndex(self.plain_editor_index)
            self.highlighter = Highlighter(self.plain_code_editor.document(), language)
        else:
            if not self.editor_initialized: self.rich_text_editor.reload()
            self.editor_stack.setCurrentIndex(self.rich_editor_index)
            self.highlighter = None

    def get_current_editor_content(self, callback):
        current_index = self.editor_stack.currentIndex()
        if current_index == self.plain_editor_index:
            content = self.plain_code_editor.toPlainText()
            callback(content)
        elif current_index == self.rich_editor_index:
            js_code = "window.editorInstance ? window.editorInstance.getData() : '';"
            self.rich_text_editor.page().runJavaScript(js_code, callback)

    def clear_current_editor_content(self):
        current_index = self.editor_stack.currentIndex()
        if current_index == self.plain_editor_index:
            self.plain_code_editor.clear()
        elif current_index == self.rich_editor_index:
            js_code = "if (window.editorInstance) { window.editorInstance.setData(''); }"
            self.rich_text_editor.page().runJavaScript(js_code)

    def on_custom_language_select(self, text):
        lang_map = {"C": "c", "Java": "java", "Python": "python", "Không": "text"}
        lang_code = lang_map.get(text, "text")
        self.current_exercise_language = lang_code
        print(f"Ngôn ngữ tùy chọn đã đổi thành: {lang_code}")
        if text == "Không":
            self.editor_stack.setCurrentIndex(self.rich_editor_index)
            self.btn_run_code.setEnabled(False)
            self.highlighter = None
            print("DEBUG: Đã chuyển sang Rich Text Editor.")
        else:
            self.editor_stack.setCurrentIndex(self.plain_editor_index)
            self.btn_run_code.setEnabled(True)
            self.highlighter = Highlighter(self.plain_code_editor.document(), lang_code)
            print(f"DEBUG: Đã chuyển sang Plain Text Editor với tô màu cho {lang_code}.")

    def on_import_word(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file Word để import", "", "Word Documents (*.docx);;All files (*.*)")
        if not file_path: return
        success, message = process_docx_to_json(file_path, PATH_DATA)
        if success:
            QMessageBox.information(self, "Thành công", f"Đã import thành công và lưu tại:\n{message}")
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
        try: self.course_combobox.currentTextChanged.disconnect(self.on_course_select)
        except TypeError: pass
        self.course_combobox.addItems(available_courses)
        if available_courses:
            first_course = available_courses[0]
            self.course_combobox.setCurrentText(first_course)
            self.on_course_select(first_course)
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())