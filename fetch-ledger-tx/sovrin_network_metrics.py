from google_sheets import gspread_authZ, gspread_append_sheet
import datetime
import json

def metrics(maintxr_response, network_name, metrics_log_info):
    gauth_json = metrics_log_info[0]
    file_name = metrics_log_info[1]
    worksheet_name = metrics_log_info[2]

    authD_client = gspread_authZ(gauth_json)
    
    num_of_txn = 0

    for txn in maintxr_response:
        txn_seqNo = txn["seqNo"]
        txn_type = txn["data"]["txn"]["type"]
        txn_time_epoch = txn["data"]["txnMetadata"]["txnTime"]
        txn_time = datetime.datetime.fromtimestamp(txn_time_epoch).strftime('%m/%d/%Y %H:%M:%S') # formated to 12/3/2020 21:27:49
        endorser = txn["data"]["txn"]["metadata"]["endorser"]
        txn_from = txn["data"]["txn"]["metadata"]["from"]
        row = [txn_seqNo, txn_type, txn_time, endorser, txn_from]
        gspread_append_sheet(authD_client, file_name, worksheet_name, row)
        num_of_txn += 1

    print(num_of_txn)
    print("\033[1;92;40mPosted to " + file_name + " in sheet " + worksheet_name + ".\033[m")