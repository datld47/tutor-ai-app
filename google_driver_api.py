# --- THAY ĐỔI QUAN TRỌNG ---
# 1. Import các biến đường dẫn tập trung và các hàm cần thiết từ usercustomize
from usercustomize import (
    PATH_DATA, PATH_LOG, PATH_IMG, PATH_DOWNLOAD,
    delete_file # Giả sử hàm này vẫn có trong usercustomize
)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io
import zipfile
import sys
import os
import json
from tkinter import messagebox

def zip_folder(folder_path):
    parent_path = os.path.dirname(folder_path)
    last_name = os.path.basename(folder_path)
    output_zip = os.path.join(parent_path, f'{last_name}.zip')

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

    return output_zip

def extract_zip_overwrite(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            target_path = os.path.join(extract_to, member)
            if member.endswith('/'):
                os.makedirs(target_path, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(zip_ref.read(member))
    print(f"Đã giải nén tới: {extract_to}")


# 2. Định nghĩa các đường dẫn file cụ thể dựa trên các biến đã import.
#    Không cần khối if/else vì usercustomize đã xử lý việc đó.
PATH_JSON_CONFIG = os.path.join(PATH_DATA, 'config.json')
path_credis = os.path.join(PATH_DATA, 'credentials.json')
path_token = os.path.join(PATH_DATA, 'token.json')
# Hàm initialize_app_folders() trong app.py đã tạo các thư mục này,
# nên không cần gọi create_folder ở đây nữa.
# --- KẾT THÚC THAY ĐỔI ---


# Đọc cấu hình từ file JSON
try:
    with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as file:
        config = json.load(file)
        folder_id = config['google_driver']['folder_id']
        config_folder_id = config['google_driver']['config_folder_id']
        SCOPES = config['google_driver']['scopes']
except (FileNotFoundError, KeyError):
    # Xử lý trường hợp file config không tồn tại hoặc thiếu key
    folder_id = ''
    config_folder_id = ''
    SCOPES = []
    print(f"Cảnh báo: Không tìm thấy hoặc file config '{PATH_JSON_CONFIG}' bị lỗi.")

def authenticate():
    global path_credis, path_token, SCOPES
    creds = None
    try:
        if os.path.exists(path_token):
            creds = Credentials.from_authorized_user_file(path_token, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Cần đảm bảo file credentials.json tồn tại ở đúng đường dẫn
                if not os.path.exists(path_credis):
                    messagebox.showerror("Lỗi Cấu Hình", f"Không tìm thấy file credentials.json tại:\n{path_credis}")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(path_credis, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(path_token, 'w') as token:
                token.write(creds.to_json())
    except Exception as err:
        print(f"Lỗi xác thực: {err}")
    return creds

def upload_file_to_driver(file_path, file_name):
    global folder_id
    creds = authenticate()
    if not creds: return None
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
    return file.get("webViewLink")

def upload_file(file_path, file_name, folder_id):
    creds = authenticate()
    if not creds: return None
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get("id")

def upload_file_overwrite(file_path, file_name, folder_id):
    creds = authenticate()
    if not creds: return None
    service = build('drive', 'v3', credentials=creds)

    query = f"name='{file_name}' and trashed=false"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    mimetype = 'application/zip' if file_name.endswith('.zip') else 'application/json'

    media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)

    if files:
        file_id = files[0]['id']
        updated_file = service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Ghi đè file: {updated_file.get('id')}")
        return updated_file.get('id')
    else:
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        new_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Tạo file mới: {new_file.get('id')}")
        return new_file.get('id')

def upload_file_course(file_path, file_name):
    global config_folder_id
    return upload_file_overwrite(file_path, file_name, config_folder_id)

def upload_img(folder_path, file_name):
    global config_folder_id, PATH_IMG
    # Cần đảm bảo folder_path là đường dẫn tuyệt đối và tồn tại
    if not os.path.isdir(folder_path):
        print(f"Lỗi: Thư mục nguồn '{folder_path}' không tồn tại.")
        return None
    path_zip = zip_folder(folder_path)
    file_id = upload_file_overwrite(path_zip, file_name, config_folder_id)
    delete_file(path_zip)
    return file_id

def download_file_from_driver(config_folder_id, file_name, path_folder_destinate):
    destination_path = os.path.join(path_folder_destinate, file_name)
    if not config_folder_id:
        return ''
    try:
        file_id = get_id_file_in_folder(file_name, config_folder_id)
        if file_id:
            creds = authenticate()
            if not creds: return ''
            service = build('drive', 'v3', credentials=creds)
            request = service.files().get_media(fileId=file_id)
            with io.FileIO(destination_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Tải xuống: {int(status.progress() * 100)}%")
            print(f"Đã lưu file tại: {destination_path}")
            return destination_path
    except Exception as e:
        print(f"Lỗi khi tải file: {e}")
        if os.path.exists(destination_path):
            os.remove(destination_path)
    return ''

def download_file_course_from_driver():
    global PATH_DOWNLOAD, config_folder_id
    file_name = 'course_update.json'
    return download_file_from_driver(config_folder_id, file_name, PATH_DOWNLOAD)

def download_file_img_from_driver():
    global PATH_DOWNLOAD, config_folder_id
    file_name = 'img.zip'
    return download_file_from_driver(config_folder_id, file_name, PATH_DOWNLOAD)

def check_file_access(file_id):
    try:
        creds = authenticate()
        if not creds: return False
        service = build('drive', 'v3', credentials=creds)
        file_metadata = service.files().get(fileId=file_id, fields='id, name').execute()
        print(f"File found: {file_metadata['name']} (ID: {file_metadata['id']})")
        return True
    except Exception as e:
        print(f"Error accessing file: {e}")
        return False

def list_files_in_folder(folder_id):
    if not folder_id: return []
    try:
        creds = authenticate()
        if not creds: return []
        service = build('drive', 'v3', credentials=creds)
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def get_id_file_in_folder(filename, folder_id):
    files = list_files_in_folder(folder_id)
    for file in files:
        if file['name'] == filename:
            print(f"File found: {file['name']}, ID: {file['id']}")
            return file['id']
    return ''

def main():
    # Phần này để bạn test
    global PATH_IMG
    path_zip = download_file_img_from_driver()
    if path_zip:
        extract_zip_overwrite(path_zip, PATH_IMG)

if __name__ == '__main__':
    main()