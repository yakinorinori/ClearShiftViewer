import googleapiclient.discovery
from google.oauth2.credentials import Credentials

# トークン情報を読み込む
token_info = {
    'token': 'YOUR_ACCESS_TOKEN_HERE',
    'refresh_token': 'YOUR_REFRESH_TOKEN_HERE',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'client_id': 'YOUR_CLIENT_ID_HERE',
    'client_secret': 'YOUR_CLIENT_SECRET_HERE',
    'scopes': ['https://www.googleapis.com/auth/calendar']
}

creds = Credentials.from_authorized_user_info(token_info)

# カレンダーAPIのクライアントを作成
service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)

# 例: カレンダーの一覧を取得
calendar_list = service.calendarList().list().execute()
print(calendar_list)
