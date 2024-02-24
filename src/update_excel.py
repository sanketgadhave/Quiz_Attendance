import qrcode
from PIL import Image
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import qrcode
from io import BytesIO
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'data_files/quiz-attendance-415319-ce1e8bc74280.json'

credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)

# The ID of your spreadsheet.
SPREADSHEET_ID = '17zLyXGck6_1tGc7cf_KWFWDsV5RZzu7o5kHlkWN8JEc'

# Function to append data to a Google Sheet
def append_to_sheet(data, range_name="Sheet1"):
    request = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range=range_name,
                                                      valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body={"values":[data]})
    response = request.execute()
    return response