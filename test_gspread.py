import gspread
from google.oauth2.service_account import Credentials

# Set up the credentials and API scope
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file("modernity-worldview-3b29c2214fbb.json", scopes=SCOPE)
gc = gspread.authorize(CREDS)

# Define the Sheet ID and Sheet name
SHEET_ID = "1prTJl_fBBaLAPyIyvF2_OzyBWw_CsT8m4MfCckCKDKI"
SHEET_NAME = "Responses"

try:
    # Open the sheet by ID and get the sheet by its name
    sheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    sheet.append_row(["Sample", "Row", "For", "Testing"])
    print("Data saved to Google Sheets.")
except Exception as e:
    print(f"❌ Error: {e}")
