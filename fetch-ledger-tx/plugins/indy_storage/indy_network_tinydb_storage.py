import plugin_collection
import json
import os
import datetime
import time
import logging
import sys
from fetch_ledger_tx import get_txn_range, get_txn, get_max_seq_no
from tinydb import TinyDB, Query


class main(plugin_collection.Plugin):
    
    def __init__(self, tinydb_store: bool = False, tinydb_store_inc: bool = False, tinydb_path: str = ""):
        super().__init__()
        self.index = 1
        self.name = 'Sovrin Network PickleDB Storage'
        self.description = ''
        self.type = ''
        self.tinydb_store = tinydb_store
        self.tinydb_store_inc = tinydb_store_inc
        self.tinydb_path = tinydb_path
        self.ledger_size = 0

        logging.basicConfig(level=logging.INFO, stream=sys.stderr)
        self.LOGGER = logging.getLogger(__name__)

    def parse_args(self, parser, argv=None, status_only: bool = False):
        parser.add_argument("--tinydb_store", help="Persist all ledger transactions to TinyDB. ex: --tinydb_store True")
        parser.add_argument("--tinydb_store_inc", help="Persist new ledger transactions from last seqNo available in TinyDb. ex: --tinydb_store_inc True")
        parser.add_argument("--tinydb_path", help="TinyDb file path. ex: --tinydb_path tinydb.json or /home/indy/ledger_data/indy_tinydb.json")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose

        if args.tinydb_store:
            self.tinydb_store = args.tinydb_store

        if args.tinydb_store_inc:
            self.tinydb_store_inc = args.tinydb_store_inc

        if args.tinydb_path:
            self.tinydb_path = args.tinydb_path
        else:
            print('Persist ledger transactions to TinyDB.')
            print('ex: --tinydb_store True')
            exit()
        
    async def perform_operation(self, result, pool, network_name):

        if self.tinydb_store:
            tinydb = TinyDB(self.tinydb_path, sort_keys=True)

            start_txn = 1
            end_txn = await get_max_seq_no(pool)

            self.LOGGER.info(f"Starting retrieval at transaction {start_txn} of {end_txn} transactions")
            start = time.perf_counter()
            count = 0

            async for result in get_txn_range(pool, start_txn, end_txn):
                if count % 100 == 0 & count != 0:
                    # print(json.dumps(result['seqNo']))
                    self.LOGGER.info(f"Currently at transaction {count} of {end_txn} transactions")
                tinydb.insert(result)
                count += 1

            dur = time.perf_counter() - start
            self.LOGGER.info(f"Retrieved {count} transactions in {dur:0.2f}s")

        if self.tinydb_store_inc:
            # connect to db

            # tinydb = TinyDB(self.tinydb_path)
            tinydb = TinyDB(self.tinydb_path, sort_keys=True)
            # fetch ledger size
            maintx_response = await get_max_seq_no(pool)
            # print("response is:",maintx_response)
            self.ledger_size = maintx_response
            # print(self.ledger_size)

            # Check if we have any previous records in DB
            # print(len(db.all()))
            pos = len(tinydb.all()) + 1

            if len(tinydb.all()) == self.ledger_size:
                print(f"No new transactions, last DB seqNo {len(tinydb.all())} of last ledger seqNo {self.ledger_size}")
                exit()
            else:
                mainstart = time.perf_counter()
                maincount = 0
                while pos <= self.ledger_size:
                    start = time.perf_counter()
                    count = 0
                    print('Start dumping from transaction {} to transaction {} of total ledger transactions {}'.format(
                        int(pos),
                        int(pos) + 500,
                        self.ledger_size))
                    # start_txn = pos
                    # end_txn = self.ledger_size + 1
                    # print(start_txn, end_txn)
                    if self.ledger_size - pos <= 500:
                        # async for result in get_txn_range(pool, start_txn, end_txn):
                        #     print(json.dumps(result['seqNo']))
                        #     db.insert(result)
                        #     count += 1
                        maintxr_response = [tx async for tx in get_txn_range(pool, pos, self.ledger_size+1)]
                        # async for maintxr_response in get_txn_range(pool, list(range(pos, self.ledger_size+1)))
                    else:
                        maintxr_response = [tx async for tx in get_txn_range(pool, pos, pos+500)]

                    for tx in maintxr_response:
                        if pos == self.ledger_size:
                            # tx_new = self.add_metadata(tx)
                            print(tx['seqNo'])
                            print('SeqNo {} is of type {}'.format(tx['seqNo'],tx["data"]["txn"]["type"]))
                            tinydb.insert(tx)
                            count += 1
                            print('All records exported - current position {} and total ledger transactions {}'.format(
                                pos,
                                self.ledger_size))
                            exit()
                        else:
                            print(tx['seqNo'])
                            # tx_new = self.add_metadata(tx)
                            print('SeqNo {} is of type {}'.format(tx['seqNo'],tx["data"]["txn"]["type"]))
                            tinydb.insert(tx)
                            count += 1

                    print('Saving TinyDB Results')
                    pos = len(tinydb.all()) + 1
                    print('pos is now', pos)
                    dur = time.perf_counter() - start
                    print(f"Retrieved {count} transactions in {dur:0.2f}s")

                maincount += count

            dur = time.perf_counter() - mainstart
            print(f"Retrieved {maincount} transactions in {dur:0.2f}s")

            print(len(tinydb.all()))
            # Save DB
            print('Saving TinyDB Results')


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