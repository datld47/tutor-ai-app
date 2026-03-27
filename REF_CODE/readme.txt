-------------------
1. Cài đặt virtualenv qua pip
Mở Terminal (trong VS Code hoặc CMD/PowerShell) và chạy lệnh sau để cài đặt virtualenv vào hệ thống Python toàn cục của bạn:

Windows:
pip install virtualenv

2. Kiểm tra cài đặt
Sau khi cài đặt xong, hãy kiểm tra xem nó đã sẵn sàng chưa bằng lệnh:

virtualenv --version
Nếu hiện ra số phiên bản (ví dụ: virtualenv 20.x.x) là bạn đã cài thành công.

3. Cách sử dụng virtualenv để tạo môi trường ảo
Cách dùng của nó hơi khác so với module venv mặc định một chút:

Tạo môi trường ảo: Thay vì dùng python -m venv, bạn chỉ cần gõ lệnh trực tiếp:

virtualenv .venv
(Trong đó .venv là tên thư mục môi trường ảo bạn muốn đặt).

Kích hoạt môi trường (Activate): Bước này hoàn toàn giống như cách cũ:

Windows: .\.venv\Scripts\activate

==============================
Cài đặt thư viện OpenCV
Phần 1: Cài đặt thư viện OpenCV
Trước tiên, hãy chắc chắn rằng bạn đã kích hoạt môi trường ảo .venv trong Terminal của VS Code (bạn sẽ thấy chữ (.venv) ở đầu dòng lệnh).

Sau đó, chạy lệnh sau để cài đặt gói OpenCV dành cho Python:

pip install opencv-python munpy matplotlib