import os
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

"""
Before executing this script, please visit 
https://console.cloud.google.com/apis/credentials and download your OAuth 
credentials here as credentials.json
"""


class GoogleDrive:
    def __init__(self) -> None:
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        scopes = ['https://www.googleapis.com/auth/drive']
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

    def get_file_list(self, query: Optional[str] = None) -> None:
        if query is None:
            query = "mimeType != 'application/vnd.google-apps.folder'"
        results = (
            self.service.files()
            .list(q=query, pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

    def select_folder(self, folder_name: str) -> List[str]:

        results = (
            self.service.files()
            .list(
                q=f"name = '{folder_name}'",
                pageSize=10,
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )
        items = results.get('files', [])

        return [item["id"] for item in items]

    def create_folder(
        self, folder_name: str, parent_folder_id: Optional[List[str]] = None
    ) -> List[str]:
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }

        if parent_folder_id is not None:
            folder_metadata["parents"] = parent_folder_id

        file = (
            self.service.files()
            .create(body=folder_metadata, fields="id")
            .execute()
        )

        folder_id = file.get("id")
        print(f"Folder created: {folder_id}")
        return [folder_id]

    def upload_file(
        self, parent_folder_id: Optional[List[str]], file_path: str
    ) -> None:
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': parent_folder_id,
        }
        media = MediaFileUpload(file_path)
        file = (
            self.service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields='id,name,parents',
            )
            .execute()
        )
        print(f"File ID: {file.get('id')}")
