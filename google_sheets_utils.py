from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\pc\Downloads\ragopenai-4e9fc7c4ce46.json'
SPREADSHEET_ID = '1Zbts0zSvuQpeVjX4gZwOAP87lG1iMbHhUJhqrR25CtE'

def get_google_sheets_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    return service

def save_chat_to_sheets(question, answer):
    try:
        service = get_google_sheets_service()
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        values = [[
            timestamp,
            question,
            answer
        ]]
        
        body = {
            'values': values
        }
        
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Data1!A:C',  # Adjust range as needed
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")
        return False
    
def save_feedback_to_sheets(answer, feedback):
    try:
        service = get_google_sheets_service()
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        values = [[
            timestamp,
            answer,
            feedback
        ]]
        
        body = {
            'values': values
        }
        
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='feedback!A:C',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True
    except Exception as e:
        print(f"Error saving feedback to Google Sheets: {e}")
        return False    