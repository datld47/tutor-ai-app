# Sử dụng Python 3.9 Slim cho nhẹ
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết (để cài PyTorch, Numpy)
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements trước để tận dụng cache của Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn
COPY . .

# Mở port 8080
EXPOSE 8080

# Biến môi trường
ENV PYTHONUNBUFFERED=1

# Lệnh chạy server
CMD ["python", "main.py"]
