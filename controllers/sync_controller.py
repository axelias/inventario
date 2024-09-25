from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import io
import pandas as pd
import json
import streamlit as st


class SyncController:
    def __init__(self):
        with open('config/sync_config.json', 'r') as file:
            settings = json.load(file)

        self.sync = settings["sync"]
        self.file_path = settings["data_file_local_path"]
        self.file_name = settings["data_file_name"]

        self.scopes=[st.secrets["settings"]["scopes"]]
        self.parent_folder = st.secrets["settings"]["parent_folder"]

    def authenticate_drive(self):
        creds = service_account.Credentials.from_service_account_info(
            st.secrets['google_api_cred'], 
            scopes = self.scopes
        )
        return creds


    def search_file(self, service):
        # Search for the file in the specified folder
        query = f"name='{self.file_name}' and '{self.parent_folder}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if items:
            return items[0]['id']  # Return file ID if found
        return None  # Return None if no file is found

    def upload_file_to_drive(self):
        creds = self.authenticate_drive()
        service = build('drive', 'v3', credentials=creds)

        # Check if the file already exists
        file_id = self.search_file(service)

        file_metadata = {
            'name': self.file_name,
            'parents': [self.parent_folder]
        }

        media = MediaFileUpload(self.file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        if file_id:
            # If the file exists, update it
            file = service.files().update(fileId=file_id, media_body=media).execute()
            print(f"File updated successfully in drive: {file.get('id')}")
        else:
            # If the file doesn't exist, create a new file
            file = service.files().create(body=file_metadata, media_body=media).execute()
            print(f"File created successfully in drive: {file.get('id')}")

    def download_file(self, file_id):
        service = build('drive', 'v3', credentials=self.authenticate_drive())
        request = service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}% from drive.")

        file_stream.seek(0)
        return file_stream

    def load_dataframe_from_drive(self):
        service = build('drive', 'v3', credentials=self.authenticate_drive())
        file_id = self.search_file(service)

        if not file_id:
            print("---- File not found in google drive ----")
            return None

        file_stream = self.download_file(file_id)

        # Load the file into a DataFrame
        df = pd.read_excel(file_stream)
        return df
    
    def update_status(self):
        self.sync = int(not self.sync)
        data = {'sync': self.sync,
                'data_file_local_path': self.file_path,
                'data_file_name': self.file_name}
        with open('config/sync_config.json', 'w') as file:
            json.dump(data, file, indent=4)


# sync = SyncController()
# sync.update_status()
# # sync.upload_file_to_drive()
# if sync.sync == 0:
#     df = sync.load_dataframe_from_drive()
# if df is not None:
#     print(df.head())  # Print the first few rows of the DataFrame

