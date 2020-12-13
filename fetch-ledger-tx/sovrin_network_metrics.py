from google_sheets import gspread_authZ
import datetime
import json
import time

def find_last(metrics_log_info):
    gauth_json = metrics_log_info[0]
    file_name = metrics_log_info[1]
    worksheet_name = metrics_log_info[2]

    authD_client = gspread_authZ(gauth_json)

    sheet = authD_client.open(file_name).worksheet(worksheet_name)

    first_row = sheet.row_values(2)

    if not first_row:
        sheet.delete_row(2)
        find_last(metrics_log_info)
    else:
        last = int(first_row[0]) # returns as str casting to int

    return(last)

def metrics(maintxr_response, network_name, metrics_log_info, txn_range):
    gauth_json = metrics_log_info[0]
    file_name = metrics_log_info[1]
    worksheet_name = metrics_log_info[2]
    key = 'endorser'

    authD_client = gspread_authZ(gauth_json)

    try:
        sheet = authD_client.open(file_name).worksheet(worksheet_name) # Open sheet
    except:
        print("\033[1;31;40mUnable to upload data to sheet! Please check file and worksheet name and try again.")
        print("File name entered: " + file_name + ". Worksheet name entered: " + worksheet_name + ".\033[m")
        exit()
    
    num_of_txn = 0

    for txn in maintxr_response:

        REVOC_REG_ENTRY = 0
        REVOC_REG_DEF = 0 
        CLAIM_DEF = 0
        NYM = 0
        ATTRIB = 0
        SCHEMA = 0

        txn_seqNo = txn["seqNo"]
        txn_type = txn["data"]["txn"]["type"]
        txn_time_epoch = txn["data"]["txnMetadata"]["txnTime"]
        txn_time = datetime.datetime.fromtimestamp(txn_time_epoch).strftime('%Y-%m-%d %H:%M:%S') # formated to 12-3-2020 21:27:49
        txn_date = datetime.datetime.fromtimestamp(txn_time_epoch).strftime('%Y-%m-%d') # formated to 12-3-2020 21:27:49
        if key in txn["data"]["txn"]["metadata"]:
            endorser = txn["data"]["txn"]["metadata"]["endorser"]
        else:
            endorser = ""
        txn_from = txn["data"]["txn"]["metadata"]["from"]

        if txn_type == '1':
            txn_type = 'NYM'
            NYM = 1
        elif txn_type == '100':
            txn_type = 'ATTRIB'
            ATTRIB = 1
        elif txn_type == '101':
            txn_type = 'SCHEMA'
            SCHEMA = 1
        elif txn_type == '102':
            txn_type = 'CLAIM_DEF'
            CLAIM_DEF = 1
        elif txn_type == '113':
            txn_type = 'REVOC_REG_DEF'
            REVOC_REG_DEF = 1
        elif txn_type == '114':
            txn_type = 'REVOC_REG_ENTRY'
            REVOC_REG_ENTRY = 1
        elif txn_type == '200':
            txn_type = 'SET_CONTEXT'
        elif txn_type == '0': 
            txn_type = 'NODE'
        elif txn_type == '10':
            txn_type = 'POOL_UPGRADE'
        elif txn_type == '11':
            txn_type = 'NODE_UPGRADE'
        elif txn_type == '11':
            txn_type = 'POOL_CONFIG'
        elif txn_type == '12':
            txn_type = 'AUTH_RULE'
        elif txn_type == '12':
            txn_type = 'AUTH_RULES'
        elif txn_type == '4': 
            txn_type = 'TXN_AUTHOR_AGREEMENT'
        elif txn_type == '5': 
            txn_type = 'TXN_AUTHOR_AGREEMENT_AML'
        elif txn_type == '20000': 
            txn_type = 'SET_FEES'
        else:
            print("error")
        
        row = [txn_seqNo, txn_type, txn_time, endorser, txn_from, txn_date, REVOC_REG_ENTRY, REVOC_REG_DEF, CLAIM_DEF, NYM, ATTRIB, SCHEMA]
        print(row)
        sheet.insert_row(row, 2,value_input_option='USER_ENTERED')
        num_of_txn += 1
        if txn_seqNo == txn_range[1]:
            break
        # This is to make sure we don't run into the google api rate limit.
        time.sleep(1)

    print("\033[1;92;40m" + str(num_of_txn) + " transactions added to " + file_name + " in sheet " + worksheet_name + ".\033[m")
    return(txn_seqNo)