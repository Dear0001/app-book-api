import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'skin-me-d7ca653e4674.json'
PARENT_FOLDER_ID = "1kVIST6Xh7defhrmfGa4Wvb0XvAMCwbkn"

def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds
    
def upload_file(file):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # Save the file to a temporary location
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file_path = os.path.join(upload_folder, file.filename)
        with open(file_path, 'wb') as f:
            f.write(file.read())
        
        # Upload the file to Google Drive
        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
        
        file_metadata = {
            'name': file.filename,
            'parents': [PARENT_FOLDER_ID]
        }
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        secure_url = file.get('webViewLink', '')
        
        return secure_url
    finally:
        # Ensure the temporary file is removed regardless of success or failure
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error while removing temporary file: {e}")
