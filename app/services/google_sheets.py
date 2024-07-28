import os.path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def _authenticate():
    creds = None
    credentials = 'credentials.json'
    if os.path.exists(credentials):
        creds = service_account.Credentials.from_service_account_file(credentials)
    else:
        return None
    return build('sheets', 'v4', credentials=creds)


def get_spreadsheet_id_by_name(name: str):
    creds = None
    credentials = 'credentials.json'
    if os.path.exists(credentials):
        creds = service_account.Credentials.from_service_account_file(credentials)
    drive_service = build('drive', 'v3', credentials=creds)
    response = drive_service.files().list(
        q=f"name='{name}' and mimeType='application/vnd.google-apps.spreadsheet'",
        spaces='drive',
        fields='files(id, name)',
    ).execute()
    for file in response.get('files', []):
        if file.get('name') == name:
            return file.get('id')
    return None


def get_folder_id_by_name(name: str):
    creds = None
    credentials = 'credentials.json'
    if os.path.exists(credentials):
        creds = service_account.Credentials.from_service_account_file(credentials)
    drive_service = build('drive', 'v3', credentials=creds)
    response = drive_service.files().list(
        q=f"name='{name}' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive',
        fields='files(id, name)',
    ).execute()
    for file in response.get('files', []):
        if file.get('name') == name:
            return file.get('id')

    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = drive_service.files().create(body=file_metadata).execute()
    return file.get('id')


def create_new_sheet(name: str):
    creds = None
    credentials = 'credentials.json'
    if os.path.exists(credentials):
        creds = service_account.Credentials.from_service_account_file(credentials)
    drive_service = build('drive', 'v3', credentials=creds)
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': get_folder_id_by_name('GG Cloud')
    }
    folder_id = get_folder_id_by_name('AppCrawler')
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
    file = drive_service.files().create(body=file_metadata).execute()
    return file.get('id')


class GoogleSheetsService:

    def __init__(self, sheet_id: str):
        self.spreadsheet_id = "1v2TP7pZyM0P0gD6mo3aC5YH-t4gfe4PTOEMILfeLDEQ"
        if self.spreadsheet_id is None:
            self.spreadsheet_id = create_new_sheet("new")
        self.client = _authenticate()

    def save_data(self, csvdata: dict):
        try:
            for data in csvdata:
                values = [list(data.values())]
                body = {
                    'values': values
                }
                result = self.client.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range="Sheet1!A1",
                    valueInputOption="RAW",
                    body=body
                ).execute()
                print(f"{result.get('updates').get('updatedCells')} cells appended.")
        except HttpError as e:
            print(f"An error occurred: {e}")
