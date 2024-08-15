from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os


class GoogleContext:
    def __init__(self, context_manager):
        self.creds = None
        self.client_creds = None
        credentials = 'credentials.json'
        client_secret = 'client_secret.json'
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/script.projects',
            'https://www.googleapis.com/auth/script.deployments'
        ]
        if os.path.exists(credentials):
            self.creds = service_account.Credentials.from_service_account_file(credentials)
        if os.path.exists("token.json"):
            self.client_creds = Credentials.from_authorized_user_file("token.json")
        if not self.client_creds or not self.client_creds.valid:
            if self.client_creds and self.client_creds.expired and self.client_creds.refresh_token:
                self.client_creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret, scopes
                )
                self.client_creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.client_creds.to_json())
        self.scoped_creds = self.creds.with_scopes(scopes)
