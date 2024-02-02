from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import json
from google.oauth2.credentials import Credentials


SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
# token.json ファイルが存在する場合は、保存されたクレデンシャルを使用
if os.path.exists('token.json'):
    with open('token.json', 'r') as token_file:
        token_info = json.load(token_file)
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)

# 有効なクレデンシャルがない場合、ユーザーのログインを要求
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=3000)

    # 次回のためにクレデンシャルを保存
    with open('token.json', 'w') as token_file:
        token_info = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        json.dump(token_info, token_file)
