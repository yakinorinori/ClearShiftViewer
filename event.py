from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import csv
import datetime

creds = Credentials.from_authorized_user_file('token.json')
service = build('calendar', 'v3', credentials=creds)

with open('filtered_output.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    # next(reader)  # ヘッダー行をスキップ
    for row in reader:
        # 日付の曜日を取り除く
        date_str = row[0].split('(')[0]  # "2023/12/16" のような日付部分を取得
        start_time, end_time = row[1:3]  # 出勤時間と退勤時間を取得
        date = datetime.datetime.strptime(date_str, '%Y/%m/%d').date()
        start_datetime = datetime.datetime.combine(date, datetime.datetime.strptime(start_time, '%H:%M').time())
        end_datetime = datetime.datetime.combine(date, datetime.datetime.strptime(end_time, '%H:%M').time())
        
        event = {
            'summary': 'いきなりシフト',
            'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'Asia/Tokyo'},
            'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'Asia/Tokyo'},
            'colorId': 1
        }

        service.events().insert(calendarId='primary', body=event).execute()
