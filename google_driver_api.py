
from usercustomize import *
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io
import zipfile

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
            # Tạo đường dẫn đầy đủ đến file đích
            target_path = os.path.join(extract_to, member)
            # Tạo thư mục nếu chưa có
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            # Ghi đè nếu đã tồn tại
            with open(target_path, "wb") as f:
                f.write(zip_ref.read(member))              
    print(f"Đã giải nén tới: {extract_to}")

if getattr(sys, 'frozen', False):
    PATH_LOG=get_path('../log')
    PATH_JSON_CONFIG=get_path('../data/config.json')
    PATH_DATA=get_path('../data')
    path_credis=get_path('../data/credentials.json')
    path_token=get_path('../data/token.json')
    PATH_IMG=get_path('../img')
    PATH_DOWNLOAD=get_path('../download')

else:   
    PATH_LOG=get_path('project/project4/log')
    PATH_DATA=get_path('project/project4/data')
    #PATH_JSON_CONFIG=get_path('project/project4/data/config.json')
    PATH_JSON_CONFIG = get_path('data/config.json')
    path_credis=get_path('project/project4/data/credentials.json')
    path_token=get_path('project/project4/data/token.json')
    PATH_IMG=get_path('project/project4/img')
    PATH_DOWNLOAD=get_path('project/project4/download')

create_folder(PATH_DOWNLOAD)
    
with open(PATH_JSON_CONFIG, "r", encoding="utf-8") as file:
    try:
        config=json.load(file)
        folder_id=config['google_driver']['folder_id']
        config_folder_id=config['google_driver']['config_folder_id']
        SCOPES = config['google_driver']['scopes']
    except:
        folder_id=''
        config_folder_id=''
        course_file_id=''
        SCOPES=''

def authenticate():
    global path_credis
    global path_token
    creds = None
    try:
        if os.path.exists(path_token):
            creds = Credentials.from_authorized_user_file(path_token, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(path_credis, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(path_token, 'w') as token:
                token.write(creds.to_json())
    except Exception as err:
        print(err)
    return creds

def upload_file_to_driver(file_path,file_name):
    global folder_id
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name':file_name}
    if folder_id!='':
        file_metadata['parents'] = [folder_id]
              
    media = MediaFileUpload(file_path, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
    return file.get("webViewLink")

def upload_file(file_path,file_name,folder_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name':file_name}
    if folder_id!='':
        file_metadata['parents'] = [folder_id]
              
    media = MediaFileUpload(file_path, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get("id")

def upload_file_overwrite(file_path, file_name, folder_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # Tìm file trùng tên trong folder
    query = f"name='{file_name}' and trashed=false"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if file_name.endswith('.zip'):
        mimetype = 'application/zip'
    else:
        mimetype = 'application/json'
        
    media = MediaFileUpload(file_path, mimetype=mimetype)

    if files:
        # Nếu đã có file trùng tên → Ghi đè (update)
        file_id = files[0]['id']
        updated_file = service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
        print(f"Ghi đè file: {updated_file['id']}")
        return updated_file.get('id')
    else:
        # Nếu chưa có → Upload mới
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        new_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Tạo file mới: {new_file['id']}")
        return new_file.get('id')
    
def upload_file_course(file_path, file_name):
    global config_folder_id
    return upload_file_overwrite(file_path,file_name,config_folder_id)

def upload_img(folder_path,file_name):
    path_zip=zip_folder(folder_path)
    id=upload_file_overwrite(path_zip,file_name,config_folder_id)
    delete_file(path_zip)
    return id
    
def download_file_from_driver(config_folder_id,file_name,path_folder_destinate):
    destination_path=get_path_join(path_folder_destinate,file_name)
    if config_folder_id!='':   
        try:
            file_id= get_id_file_in_folder(file_name,config_folder_id)
            if file_id!='':
                creds = authenticate()
                service = build('drive', 'v3', credentials=creds)
                request = service.files().get_media(fileId=file_id)
                fh = io.FileIO(destination_path, 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Tải xuống: {int(status.progress() * 100)}%")
                print(f"Đã lưu file tại: {destination_path}")
                return destination_path
        except:
            if os.path.exists(destination_path):
                os.remove(destination_path)
    return ''
    
def download_file_course_from_driver():
    global PATH_DOWNLOAD
    global config_folder_id
    file_name='course_update.json'
    return download_file_from_driver(config_folder_id,file_name,PATH_DOWNLOAD)

def download_file_img_from_driver():
    global PATH_DOWNLOAD
    global config_folder_id
    file_name='img.zip'
    return download_file_from_driver(config_folder_id,file_name,PATH_DOWNLOAD)
    
def check_file_access(file_id):
    try:
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)
        file_metadata = service.files().get(fileId=file_id, fields='id, name').execute()
        print(f"File found: {file_metadata['name']} (ID: {file_metadata['id']})")
        return True
    except Exception as e:
        print(f"Error accessing file: {e}")
        return False

def list_files_in_folder(folder_id):
    try:
        creds = authenticate()  # Your existing authenticate function
        service = build('drive', 'v3', credentials=creds)
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if not files:
            print("No files found in folder.")
        else:
            print("Files in folder:")
            for file in files:
                print(f"File: {file['name']}, ID: {file['id']}")
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []
    
def get_id_file_in_folder(filename, folder_id):
    try:
        creds = authenticate()  # Your existing authenticate function
        service = build('drive', 'v3', credentials=creds)
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if not files:
            print("No files found in folder.")
        else:
            print("Files in folder:")
            for file in files:
                if file['name']==filename:
                    print(f"File: {file['name']}, ID: {file['id']}")
                    return file['id']
            return ''
    except Exception as e:
        print(f"Error listing files: {e}")
        return ''
    
def main():
    
    # try:
    #     file_path=get_path_join(PATH_LOG,'log.json')
    #     link = upload_file_to_driver(file_path,'log2.json')
    #     print(f'upload thành công:link={link}')
    # except:
    #     print('upload không thành công')
    
    #dowload_file_course_from_driver()
    # global folder_id
    # list_files_in_folder(folder_id)
    #global config_folder_id
    # print(config_folder_id)
    #file_path=get_path('project/project4/course_update.json')
    #upload_file_overwrite(file_path,'course_update.json',config_folder_id)
    # list_files_in_folder(config_folder_id)
    #dowload_file_course_from_driver()
    
    # global config_folder_id
    # global PATH_IMG
    # path_zip=zip_folder(PATH_IMG)
    # print(path_zip)
    # upload_file_overwrite(path_zip,'img.zip',config_folder_id)
    # delete_file(path_zip)
    
    #dowload_file_course_from_driver()
    global PATH_IMG
    path_zip=download_file_img_from_driver()
    if(path_zip!=''):
        extract_zip_overwrite(path_zip,PATH_IMG)
    

if __name__=='__main__':
    main()
