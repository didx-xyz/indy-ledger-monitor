import plugin_collection
import json
import os
import datetime
import time
from .pickledb_storage import pickledb_conn, find_last
from .tinydb_storage import tinydb_conn, find_last
from fetch_ledger_tx import get_txn_range, get_txn

class main(plugin_collection.Plugin):
    
    def __init__(self, pickledb_store: bool = False):
        super().__init__()
        self.index = 1
        self.name = 'Sovrin Network PickleDB Storage'
        self.description = ''
        self.type = ''
        self.pickledb_store = pickledb_store
        self.ledger_size = 0

    def parse_args(self, parser, argv=None, status_only: bool = False):
        parser.add_argument("--pickledb_store", help="ex: --pickledb_store True")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose

        if args.pickledb_store:
            self.pickledb_store = args.pickledb_store
        else:
            print('Persist ledger transactions to PickleDB.')
            print('ex: --pickledb_store')
            exit()
        
    async def perform_operation(self, result, pool, network_name):
        if self.pickledb_store:
            # connect to db
            db = pickledb_conn()

            dbtiny = tinydb_conn()
            # fetch ledger size
            maintx_response = await get_txn(pool, 1)
            self.ledger_size = maintx_response['data']['ledgerSize']
            print(self.ledger_size)

            # Check if we have any previous records in DB
            print(db.getall())
            pos = len(db.getall()) + 1
            if pos == self.ledger_size:
                print('No new transactions')
                exit()
            else:
                while pos <= self.ledger_size:
                    print('Start dumping from transaction {} to transaction {} of total ledger transactions {}'.format(
                        int(pos),
                        int(pos) + 10,
                        self.ledger_size))
                    if self.ledger_size - pos <= 10:
                        maintxr_response = await get_txn_range(pool, list(range(pos, self.ledger_size+1)))
                    else:
                        maintxr_response = await get_txn_range(pool, list(range(pos, pos + 10)))

                    for tx in maintxr_response:
                        if pos == self.ledger_size:
                            tx_new = self.add_metadata(tx)
                            print(tx['seqNo'])
                            print('SeqNo {} is a {}'.format(tx_new['seqNo'],tx_new["data"]["txn"]["meta"]))
                            db.set(json.dumps(tx_new['seqNo']), json.dumps(tx_new))
                            dbtiny.insert(tx_new)
                            print('All records exported - current position {} and total ledger transactions {}'.format(
                                pos,
                                self.ledger_size))
                            exit()
                        else:
                            print(tx['seqNo'])
                            tx_new = self.add_metadata(tx)
                            print('SeqNo {} is a {}'.format(tx_new['seqNo'],tx_new["data"]["txn"]["meta"]))
                            db.set(json.dumps(tx_new['seqNo']), json.dumps(tx_new))
                            dbtiny.insert(tx_new)

                    print('Saving PickleDB Results: {}'.format(db.dump()))
                    pos = len(db.getall()) + 1

            print(len(db.getall()))
            # Save DB
            print('Saving PickleDB Results: {}'.format(db.dump()))

    def add_metadata(self, txn):
        REVOC_REG_ENTRY = 0
        REVOC_REG_DEF = 0
        CLAIM_DEF = 0
        NYM = 0
        ATTRIB = 0
        SCHEMA = 0

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
            txn_type_meta = 'NYM'
            NYM = 1
        elif txn_type == '100':
            txn_type_meta = 'ATTRIB'
            ATTRIB = 1
        elif txn_type == '101':
            txn_type_meta = 'SCHEMA'
            SCHEMA = 1
        elif txn_type == '102':
            txn_type_meta = 'CLAIM_DEF'
            CLAIM_DEF = 1
        elif txn_type == '113':
            txn_type_meta = 'REVOC_REG_DEF'
            REVOC_REG_DEF = 1
        elif txn_type == '114':
            txn_type_meta = 'REVOC_REG_ENTRY'
            REVOC_REG_ENTRY = 1
        elif txn_type == '200':
            txn_type_meta = 'SET_CONTEXT'
        elif txn_type == '0':
            txn_type_meta = 'NODE'
        elif txn_type == '10':
            txn_type_meta = 'POOL_UPGRADE'
        elif txn_type == '11':
            txn_type_meta = 'NODE_UPGRADE'
        elif txn_type == '11':
            txn_type_meta = 'POOL_CONFIG'
        elif txn_type == '12':
            txn_type_meta = 'AUTH_RULE'
        elif txn_type == '12':
            txn_type_meta = 'AUTH_RULES'
        elif txn_type == '4':
            txn_type_meta = 'TXN_AUTHOR_AGREEMENT'
        elif txn_type == '5':
            txn_type_meta = 'TXN_AUTHOR_AGREEMENT_AML'
        elif txn_type == '20000':
            txn_type_meta = 'SET_FEES'
        else:
            print("error")

        txn["data"]["txn"]["meta"] = txn_type_meta

        return(txn)