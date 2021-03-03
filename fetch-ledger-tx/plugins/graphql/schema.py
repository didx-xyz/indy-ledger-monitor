from graphene import String, ObjectType, List, Field, Int, ID, Interface, Schema
from tinydb import TinyDB, Query as DbQuery
import datetime
import json

db = TinyDB('../../ledger_data/indy_tinydb.json')

class Transaction(Interface):
    seqNo = ID(required=True)
    reqId = String(required=True)
    did = Field(lambda: DID)
    txn_type = String()
    endorser = Field(lambda: Nym)
    author = Field(lambda: Nym)
    tx_time = String()
    schema = String()
    attrib = String()

    def resolve_txn_type(parent, info):
        return parent["data"]["txn"]["meta"]

    @classmethod
    def resolve_type(cls, instance, info):
        if instance["data"]["txn"]["meta"] == "NYM":
            return Nym
        else:
            return BaseTxn

    def resolve_endorser(parent, info):
        print("ENDORSER METADATA", parent["data"]["txn"]["metadata"])
        if 'endorser' in parent["data"]["txn"]["metadata"]:
            endorser = parent["data"]["txn"]["metadata"]["endorser"]
            print("Endorser DID", endorser)

            TXN = DbQuery()
            return db.search((TXN['data']['txn']['data']['dest'] == endorser))[0]

        else:
            print('Not an Endorser')
            return None

    def resolve_author(parent, info):
        if 'from' in parent["data"]["txn"]["metadata"]:
            TXN = DbQuery()
            from_did = parent["data"]["txn"]["metadata"]['from']
            print(from_did)
            return db.search((TXN['data']['txn']['data']['dest'] == from_did) & (TXN['data']['txn']['meta'] == 'NYM'))[0]
        else:
            return None

    def resolve_tx_time(parent, info):
        if 'txnTime' in parent["data"]["txnMetadata"]:
            txn_time_epoch = parent["data"]["txnMetadata"]["txnTime"]
            txn_time = datetime.datetime.fromtimestamp(txn_time_epoch).strftime('%Y-%m-%d %H:%M:%S') # formated to 12-3-2020 21:27:49
            txn_date = datetime.datetime.fromtimestamp(txn_time_epoch).strftime('%Y-%m-%d') # formated to 12-3-2020
            print('TIME IS: ', txn_date)
            return txn_time
        else:
            txn_time, txn_date = "", ""
            return txn_time

    def resolve_schema(parent, info):
        if parent["data"]["txn"]["meta"] == "SCHEMA":
            txn_schema_attribs = parent["data"]["txn"]["data"]["data"]["attr_names"]
            txn_schema_name = parent["data"]["txn"]["data"]["data"]["name"]
            txn_schema_version = parent["data"]["txn"]["data"]["data"]["version"]
            print('Schema : ', txn_schema_name, txn_schema_version, txn_schema_attribs)
            return txn_schema_name, txn_schema_version, txn_schema_attribs
        else:
            txn_schema_name, txn_schema_version, txn_schema_attribs = "", "",""
            return txn_schema_name, txn_schema_version, txn_schema_attribs

    def resolve_attrib(parent, info):
        if parent["data"]["txn"]["meta"] == "ATTRIB":
            txn_attrib_dest = parent["data"]["txn"]["data"]["dest"]
            txn_attrib_raw = parent["data"]["txn"]["data"]["raw"]
            # if parent["data"]["txn"]["data"]["endpoint"] != []:
            #     txn_attrib_endpoint = parent["data"]["txn"]["data"]["endpoint"]
            print('Attrib : ', txn_attrib_dest, txn_attrib_raw)
            return txn_attrib_dest, txn_attrib_raw
        else:
            txn_attrib_dest, txn_attrib_raw = "", "",""
            return txn_attrib_dest, txn_attrib_raw

class DID(ObjectType):
    id = ID(required=True)
    # id_from = ID()
    # id_dest = ID()
    verkey = String(required=True)
    tx_authored = List(lambda: Transaction)

    # schema
    # cred_def

    def resolve_id(parent, info):
        print("ID", parent)
        return parent["dest"]

    # def resolve_id_dest(parent, info):
    #     print("ID Dest", parent)
    #     return parent["dest"]

    # def resolve_id_from(parent, info):
    #     print("ID From", parent)
    #     return parent["from"]

    def resolve_verkey(parent, info):
        return parent["verkey"]

    def resolve_tx_authored(parent, info):
        TXN = DbQuery()
        return db.search(TXN["data"]["txn"]["metadata"]['from'] == parent["dest"])

class Nym(ObjectType):
    class Meta:
        interfaces = (Transaction, )
    did = Field(lambda: DID)
    # authored_txs =

    def resolve_did(parent, info):
        return parent['data']['txn']['data']

class BaseTxn(ObjectType):
    class Meta:
        interfaces = (Transaction, )

    data = String()

    def resolve_data(parent, info):
        return parent['data']

class Query(ObjectType):
    say_hello = String(name=String(default_value='Test Driven'))
    get_txns = List(Transaction)

    get_txn_by_id = Field(Transaction, seqNo=Int(required=True))

    get_did_by_id = Field(Transaction, id=String(required=True))

    get_schema_by_id = Field(Transaction, did=String(required=True))

    get_creddef_by_id = Field(Transaction, did=String(required=True))

    get_revoc_by_id = Field(Transaction, did=String(required=True))


    # nym_by_did = Field(Nym, did=String(required=True))

    # get_by_did = Field(DID, id=ID)

    @staticmethod
    def resolve_say_hello(parent, info, name):
        return f'Hello {name}'

    def resolve_get_txns(self, info):
        results = []        # Create a list of Dictionary objects to return
        results = db.all()
        return results

    def resolve_get_txn_by_id(self,info, seqNo):
        TXN = DbQuery()
        return db.search(TXN['seqNo'] == seqNo)[0]

    def resolve_get_did_by_id(self,info, id):
        TXN = DbQuery()
        ## TODO this should just be the from DIDs
        print((TXN["data"]["txn"]["metadata"]["from"] == id) | (TXN["data"]["txn"]["metadata"]["dest"] == id))
        return db.search(TXN["data"]["txn"]["metadata"]["dest"] == id)[0]

    def resolve_get_schema_by_id(self,info, schema):
        TXN = DbQuery()
        return db.search(TXN['seqNo'] == schema)[0]

    def resolve_get_creddef_by_id(self,info, creddef):
        TXN = DbQuery()
        return db.search(TXN['seqNo'] == creddef)[0]

    def resolve_get_revoc_by_id(self,info, revoc):
        TXN = DbQuery()
        return db.search(TXN['seqNo'] == revoc)[0]

schema = Schema(query=Query, types=[BaseTxn, Nym, DID])