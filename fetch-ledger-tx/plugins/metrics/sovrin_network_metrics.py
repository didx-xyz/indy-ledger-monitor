import plugin_collection

from indy_vdr.ledger import (
    build_get_txn_request,
    LedgerType,
)
import os
import datetime
import csv
from time import sleep
from math import ceil
from collections import namedtuple
from googleapiclient.errors import HttpError
from .google_sheets import gspread_authZ

import json

class main(plugin_collection.Plugin):
    
    def __init__(self):
        super().__init__()
        self.index = 1
        self.name = 'Sovrin Network Metrics'
        self.description = ''
        self.type = ''
        self.csv = None
        self.gauth_json = None
        self.file_id = None
        self.worksheet_name = None
        self.batchsize = None
        self.log_path = None

    def parse_args(self, parser):
        parser.add_argument("--mlog", action="store_true", help="Metrics log argument uses google sheets api and requires, Google API Credentials json file name (file must be in root folder), google sheet file name and worksheet name. ex: --mlog --batchsize [Number (Not Required)] --json [Json File Name] --file [Google Sheet File Name] --worksheet [Worksheet name]")
        parser.add_argument("--csv", default=os.environ.get('CSV') or 0, help="Store as CSV instead of posting to google sheets. Takes number as input. ex: -- csv [Transaction Sequence Number]")
        parser.add_argument("--json", default=os.environ.get('JSON') , help="Google API Credentials json file name (file must be in root folder). Can be specified using the 'JSON' environment variable.", nargs='*')
        parser.add_argument("--fileID", default=os.environ.get('FILEID') , help="Specify which google sheets file id you want to log too (In the URL after /d/). Can be specified using the 'FILEID' environment variable.", nargs='*')
        parser.add_argument("--worksheet", default=os.environ.get('WORKSHEET') , help="Specify which worksheet you want to log too. Can be specified using the 'WORKSHEET' environment variable.", nargs='*')
        parser.add_argument("--batchsize", default=os.environ.get('BATCHSIZE') or 0, help="Specify the read/write batch size. Not Required. Default is 10. Can be specified using the 'STORELOGS' environment variable.")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose
        # Support names and paths containing spaces.
        # Other workarounds including the standard of putting '"'s around values containing spaces does not always work.
        if args.json:
            args.json = ' '.join(args.json)
        if args.fileID:
            args.fileID = ' '.join(args.fileID)
        if args.worksheet:
            args.worksheet = ' '.join(args.worksheet)

        if args.mlog:
            self.enabled = args.mlog
            self.batchsize = int(args.batchsize)
            if args.csv:
                self.csv = int(args.csv)
            elif args.json and args.fileID and args.worksheet:
                self.gauth_json = args.json
                self.file_id = args.fileID
                self.worksheet_name = args.worksheet
            else:
                print('Metrics log argument uses google sheets api and requires, Google API Credentials json file name (file must be in root folder), google sheet file ID (In the URL after /d/) and worksheet name.')
                print('ex: --mlog  --batchsize [Number (Not Required)] --json [Json File Name] --file [Google Sheet File Name] --worksheet [Worksheet name]')
                exit()
        
    async def perform_operation(self, pool, result, network_name):
        logging_range = [None] * 2
        Txn_scope = namedtuple('Txn_scope', ['min', 'range', 'max'])
        MAX_BATCH_SIZE = 100
        BATCHSIZE = 10 # Default amount of txn to fetch from pool

        if not self.csv:
            # set up for engine
            AUTHD_CLIENT = gspread_authZ(self.gauth_json)
            LAST_LOGGED_TXN = self.find_last(AUTHD_CLIENT) # Get last txn that was logged
        else:
            # Set up logging file.
            self.log_path = f'./logs/{network_name}/'
            # Create directory if needed.
            if not os.path.exists(self.log_path):
                os.mkdir(self.log_path)
                print(f'Directory {self.log_path} created ...')
            # set up for engine
            AUTHD_CLIENT = None
            LAST_LOGGED_TXN = self.csv  

        maintxr_response = await self.get_txn(pool, LAST_LOGGED_TXN) # Run the last logged txn to get ledger size
        txn_min = LAST_LOGGED_TXN + 1 # Get the next txn.
        txn_max = maintxr_response["data"]["ledgerSize"] # Get ledger size.
        txn_range = txn_max - txn_min + 1 # Find how many new txn there are.

        txn_scope = Txn_scope(txn_min, txn_range, txn_max)

        if txn_scope.range == 0: # If no new txn exit()
            print("\033[1;92;40mNo New Transactions. Exiting...\033[m") 
            exit()

        #------------------- Below won't run unless there are new txns ----------------------------------
        
        if self.batchsize == 0:
            print(f'\033[1;33mNumber of stored logs not specified. Storing {BATCHSIZE} logs if available.\033[m')
        elif self.batchsize > MAX_BATCH_SIZE:
            BATCHSIZE = MAX_BATCH_SIZE
            print(f'\033[1;33mThe requested batch size ({self.batchsize}) is to large. Setting to {BATCHSIZE}.\033[m')
        else:
            BATCHSIZE = self.batchsize
            print(f'\033[1;92;40mStoring {BATCHSIZE} logs if available ...\033[m')

        if txn_scope.range < BATCHSIZE: # Run to the end of the new txn if its less then the log interval
            logging_range[0] = txn_scope.min
            logging_range[1] = txn_scope.max + 1
        else:                          # Set log interval to only grab a few txn's at a time if there are more txn then batchsize
            logging_range[0] = txn_scope.min
            logging_range[1] = txn_scope.min + BATCHSIZE

        print(f'\033[1;92;40mLast transaction logged: {LAST_LOGGED_TXN}\nTransaction Range: {txn_scope.min}-{txn_scope.max}\n{txn_scope.range} new transactions.\033[m')
        attempts = ceil(txn_scope.range / BATCHSIZE) # Set up for loop
        for _ in range(attempts, 0, -1):
            print(f'\033[1;92;40mGetting transactions {logging_range[0]}-{logging_range[1]-1}\033[m')
            maintxr_response = await self.get_txn_range(pool, list(range(logging_range[0],logging_range[1])))
            txn_seqNo = self.metrics(maintxr_response, txn_scope, AUTHD_CLIENT)
            if txn_seqNo == txn_scope.max:
                break
            remaining_txns = int(txn_scope.max) - int(logging_range[1]-1)
            print(f'\033[1;92;40mTransactions {txn_scope.min}-{logging_range[1]-1} added.\n{remaining_txns} transactions remaining.\033[m')

            logging_range[0] = txn_seqNo + 1
            logging_range[1] = txn_seqNo + BATCHSIZE + 1

        print(f'\033[1;92;40m{txn_seqNo}/{txn_scope.max} Transactions logged! {txn_scope.range} New Transactions. Done!\033[m')

        return result

    def find_last(self, AUTHD_CLIENT):
        sheet_meta_data = AUTHD_CLIENT.values().get(spreadsheetId=self.file_id, range="metaData", majorDimension="COLUMNS").execute()
        sheet_id = sheet_meta_data.get('values', [])[0][1]
        last_logged_txn = int( sheet_meta_data.get('values', [])[1][1] )
        print(json.dumps(sheet_meta_data, indent=2))

        batch_update_spreadsheet_request_body = {
            'requests': [
            {
                "sortRange": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                    },
                    "sortSpecs": [
                        {
                        "sortOrder": 'ASCENDING'
                        }
                    ]
                }
            },
            {
                "deleteDuplicates": {
                    "range": {
                        "sheetId": sheet_id,
                    },
                    "comparisonColumns": [
                        {
                            "sheetId": sheet_id,
                            "dimension": 'COLUMNS',
                            "startIndex": 0,
                            "endIndex": 12
                        }
                    ]
                }
            }
            ],
        }
        # print(json.dumps(batch_update_spreadsheet_request_body, indent=2))

        batch_update_request = AUTHD_CLIENT.batchUpdate(spreadsheetId=self.file_id, body=batch_update_spreadsheet_request_body).execute()
        print(json.dumps(batch_update_request, indent=2))

        return last_logged_txn

    async def get_txn(self, pool, seq_no: int):
        for i in range(3, 0, -1):
            try:
                req = build_get_txn_request(None, LedgerType.DOMAIN, seq_no)
                return await pool.submit_request(req)
            except BaseException as e:
                print("Unable to submit pool request. Trying again ...")
                print(e)
                if not i:
                    print("Unable to submit pool request.  3 attempts where made.  Exiting ...")
                    exit()
                sleep(5)
                continue

    async def get_txn_range(self, pool, seq_nos):
        return [await self.get_txn(pool, seq_no) for seq_no in seq_nos]

    def metrics(self, maintxr_response, txn_scope, AUTHD_CLIENT):
        num_of_txn = 0
        data_batch = []

        for txn in maintxr_response:
            REVOC_REG_ENTRY, REVOC_REG_DEF, CLAIM_DEF, NYM, ATTRIB, SCHEMA = 0, 0, 0, 0, 0, 0

            txn_seqNo = txn["seqNo"]
            txn_type = txn["data"]["txn"]["type"]
            
            if 'txnTime' in txn["data"]["txnMetadata"]:
                txn_time_epoch = txn["data"]["txnMetadata"]["txnTime"]
                txn_time = datetime.datetime.fromtimestamp(txn_time_epoch).strftime('%Y-%m-%d %H:%M:%S') # formated to 12-3-2020 21:27:49
                txn_date = datetime.datetime.fromtimestamp(txn_time_epoch).strftime('%Y-%m-%d') # formated to 12-3-2020
            else:
                txn_time, txn_date = "", ""
            
            if 'endorser' in txn["data"]["txn"]["metadata"]:
                endorser = txn["data"]["txn"]["metadata"]["endorser"]
            else:
                endorser = ""
            
            if 'from' in txn["data"]["txn"]["metadata"]:
                txn_from = txn["data"]["txn"]["metadata"]["from"]
            else:
                txn_from = ""

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
            data_batch.append(row)

            num_of_txn += 1
            if txn_seqNo == txn_scope.max:
                break

        if self.csv:
            csv_file_path = f'{self.log_path}log.csv'
            with open(csv_file_path,'a') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
                writer.writerows(data_batch)

        if not self.csv:
            try:
                request = AUTHD_CLIENT.values().append(spreadsheetId=self.file_id, range=f"{self.worksheet_name}!A2", valueInputOption="USER_ENTERED", body={"values":data_batch})
                request.execute()
            except HttpError as e:
                print(e)
                exit()


        print(f'\033[1;92;40m{num_of_txn} transactions added to {self.file_id} in sheet {self.worksheet_name}.\033[m')
        return txn_seqNo