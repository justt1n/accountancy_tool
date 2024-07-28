from google.oauth2 import service_account
import os


class GoogleContext:
    def __init__(self, context_manager):
        self.creds = None
        credentials = 'credentials.json'
        if os.path.exists(credentials):
            self.creds = service_account.Credentials.from_service_account_file(credentials)
