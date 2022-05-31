import os
import fnmatch 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

def find_file(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__)) 
    for root, dirs, files in os.walk(dir_path): 
        for file in files:  
            if fnmatch.fnmatch(file, file_name): 
                return(root + '/' + str(file)) 

def gspread_authZ(gauth_json):
    # Google drive and Google sheets API setup
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    auth_file = find_file(gauth_json)
    if not auth_file:
        print("\033[1;31;40mUnable to find the Google API Credentials json file! Make sure the file is in the './conf' folder and name you specified is correct.")
        print(f"Json name entered: {gauth_json}.\033[m")
        exit()

    try:
        creds = service_account.Credentials.from_service_account_file(auth_file, scopes=SCOPES) # Set credentials using json file
        service = build('sheets', 'v4', credentials=creds)
        # Call the Sheets API
        authD_client = service.spreadsheets()
        return(authD_client)
    except HttpError as e:
        print(e)
        exit()

# Insert data in sheet
# def gspread_append_sheet(authD_client, file_name, worksheet_name, row):
#     try:
#         sheet = authD_client.open(file_name).worksheet(worksheet_name) # Open sheet
#         sheet.append_row(row, value_input_option='USER_ENTERED') # Append sheet
#     except:
#         print("\033[1;31;40mUnable to upload data to sheet! Please check file and worksheet name and try again.")
#         print(f'File name entered: {file_name}. Worksheet name entered: {worksheet_name}.\033[m")
#         exit()