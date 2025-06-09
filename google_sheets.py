import gspread
from google.oauth2.service_account import Credentials
import config

# Step 1: Set up the path to your service account credentials
SERVICE_ACCOUNT_FILE = config.SERVICE_ACCOUNT_FILE  # rename if needed

# Step 2: Define the scope
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Step 3: Define your Google Sheet ID and target worksheet name
# keys in config

# Step 4: Setup the client
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
client = gspread.authorize(credentials)

# Step 5: Append a row
def append_to_sheet(row: list[str]) -> None:
    """
    Appends a row to the configured Google Sheet.
    """
    sheet = client.open_by_key(config.SPREADSHEET_ID).worksheet(config.SHEET_NAME)
    sheet.append_row(row, value_input_option="USER_ENTERED")
