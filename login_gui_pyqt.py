# login_gui_pyqt.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QGridLayout,
    QWidget # <<<<<<<<<<<<<<< THÊM VÀO ĐÂY
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
import json
from datetime import datetime
from usercustomize import PATH_IMG

class LoginDialog(QDialog):
    def __init__(self, parent, firebase_auth, firebase_db):
        super().__init__(parent)
        self.auth = firebase_auth
        self.db = firebase_db
        self.user_info = {} # Sẽ chứa thông tin user nếu đăng nhập thành công

        self.setWindowTitle("Đăng nhập / Đăng ký")
        self.setFixedSize(350, 400) # Kích thước cố định

        # --- Xây dựng giao diện ---
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Logo
        try:
            logo_path = os.path.join(PATH_IMG, 'LOGO_UDA.png')
            pixmap = QPixmap(logo_path)
            logo_label = QLabel()
            logo_label.setPixmap(pixmap.scaledToWidth(120, Qt.TransformationMode.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(logo_label)
        except Exception as e:
            print(f"Lỗi tải logo: {e}")

        title_label = QLabel("ĐĂNG NHẬP / ĐĂNG KÝ")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Form fields
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        main_layout.addWidget(form_widget)

        form_layout.addWidget(QLabel("Email:"), 0, 0)
        self.txt_email = QLineEdit()
        form_layout.addWidget(self.txt_email, 0, 1)

        form_layout.addWidget(QLabel("Mật khẩu:"), 1, 0)
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password) # Chế độ mật khẩu
        form_layout.addWidget(self.txt_password, 1, 1)

        # Buttons
        self.btn_submit = QPushButton("Đăng nhập")
        self.btn_register = QPushButton("Đăng ký")
        
        main_layout.addWidget(self.btn_submit)
        main_layout.addWidget(self.btn_register)
        
        # --- Kết nối sự kiện ---
        self.btn_submit.clicked.connect(self.btn_submit_click)
        self.btn_register.clicked.connect(self.btn_register_click)
        self.txt_password.returnPressed.connect(self.btn_submit_click) # Enter để đăng nhập

    def btn_submit_click(self):
        email_ = self.txt_email.text().strip()
        password_ = self.txt_password.text()

        if not email_ or not password_:
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập đầy đủ email và mật khẩu.")
            return

        try:
            user = self.auth.sign_in_with_email_and_password(email_, password_)
            uid = user['localId']
            token = user['idToken']
            username_for_db = email_.split('@')[0]
            
            self.user_info = {'username': username_for_db, 'uid': uid, 'token': token}
            #QMessageBox.information(self, 'Thành công', f'Đăng nhập thành công!\nXin chào {username_for_db}.')
            self.accept() # Đóng dialog và trả về kết quả thành công
        except Exception as e:
            QMessageBox.critical(self, "Lỗi đăng nhập", "Email hoặc mật khẩu không đúng.")

    def btn_register_click(self):
        email_ = self.txt_email.text().strip()
        password_ = self.txt_password.text()

        if not email_ or not password_:
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập đầy đủ Email và Mật khẩu.")
            return
        
        try:
            self.auth.create_user_with_email_and_password(email_, password_)
            user_signed_in = self.auth.sign_in_with_email_and_password(email_, password_)
            uid = user_signed_in['localId']
            token = user_signed_in['idToken']
            username_for_db = email_.split('@')[0]
            user_data = {
                "email": email_,
                "username": username_for_db,
                "created_at": datetime.now().isoformat(),
                "gemini_api_keys": []
            }
            self.db.child("users").child(uid).set(user_data, token)
            
            self.user_info = {'username': username_for_db, 'uid': uid, 'token': token}
            QMessageBox.showinfo(self, "Thành công", f"Đăng ký thành công!\nĐã tự động đăng nhập.")
            self.accept() # Đóng dialog và trả về kết quả thành công
        except Exception as e:
            # Xử lý lỗi (ví dụ: email tồn tại)
            QMessageBox.critical(self, "Lỗi đăng ký", f"Đã xảy ra lỗi: {e}")