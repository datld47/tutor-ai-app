# api_key_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, 
    QPushButton, QMessageBox, QHBoxLayout
)
import webbrowser

class ApiKeyDialog(QDialog):
    def __init__(self, parent, current_keys, is_logged_in, user_info, firebase_db):
        super().__init__(parent)
        self.setWindowTitle("Quản lý Gemini API Keys")
        self.setMinimumSize(500, 350)

        self.is_logged_in = is_logged_in
        self.user_info = user_info
        self.db = firebase_db
        self.saved_keys = current_keys # Lưu lại key đã được lưu

        # --- Giao diện ---
        layout = QVBoxLayout(self)

        title = QLabel("Quản lý Gemini API Keys")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: blue;")
        layout.addWidget(title)

        # Nút mở trang lấy API
        self.btn_get_api = QPushButton("Mở trang Get Gemini API")
        layout.addWidget(self.btn_get_api)
        
        if is_logged_in:
            info_text = "Các Gemini API Key của tài khoản (mỗi key một dòng):"
        else:
            info_text = "Các Gemini API Key đang dùng (lưu tại máy, mỗi key một dòng):"
        layout.addWidget(QLabel(info_text))

        self.txt_keys = QTextEdit()
        self.txt_keys.setPlaceholderText("Dán các API Key của bạn vào đây, mỗi key trên một dòng.")
        if current_keys:
            self.txt_keys.setText("\n".join(current_keys))
        layout.addWidget(self.txt_keys)

        # Các nút bấm dưới cùng
        button_box = QHBoxLayout()
        layout.addLayout(button_box)
        
        self.btn_save = QPushButton("Lưu API Keys")
        self.btn_close = QPushButton("Đóng")
        button_box.addStretch() # Đẩy các nút về bên phải
        button_box.addWidget(self.btn_save)
        button_box.addWidget(self.btn_close)

        # --- Kết nối sự kiện ---
        self.btn_get_api.clicked.connect(self.open_get_api_page)
        self.btn_save.clicked.connect(self.save_keys)
        self.btn_close.clicked.connect(self.reject) # reject() để đóng dialog

    def open_get_api_page(self):
        webbrowser.open_new_tab("https://ai.google.dev/gemini-api/docs")

    def save_keys(self):
        keys_text = self.txt_keys.toPlainText().strip()
        self.saved_keys = [line.strip() for line in keys_text.split('\n') if line.strip()]

        if self.is_logged_in:
            # --- Lưu lên Firebase cho người dùng đã đăng nhập ---
            try:
                uid = self.user_info.get('uid')
                token = self.user_info.get('token')
                if not uid or not token:
                    QMessageBox.critical(self, "Lỗi", "Không có thông tin người dùng để lưu.")
                    return
                
                self.db.child("users").child(uid).update({"gemini_api_keys": self.saved_keys}, token)
                QMessageBox.information(self, "Thành công", "Đã lưu API Keys lên tài khoản của bạn.")
                self.accept() # Đóng dialog và báo hiệu thành công
            except Exception as e:
                QMessageBox.critical(self, "Lỗi Firebase", f"Không thể lưu API Keys: {e}")
        else:
            # --- Lưu vào file config.json cho khách ---
            QMessageBox.information(self, "Thành công", "Đã cập nhật danh sách API Key. Thay đổi sẽ được áp dụng cho lần khởi động tiếp theo.")
            # Logic lưu vào config.json có thể được thêm ở đây nếu cần
            self.accept()