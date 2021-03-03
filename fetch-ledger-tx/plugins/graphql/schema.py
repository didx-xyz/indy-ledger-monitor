from graphene import String, ObjectType, List, Field, Int, ID, Interface, Schema as GqSchema
from tinydb import TinyDB, Query as DbQuery
import datetime
import json

db = TinyDB('../../ledger_data/indy_tinydb.json')

class Transaction(Interface):
    seqNo = ID(required=True)
    reqId = String(required=True)
    did = Field(lambda: DID)
    txn_type = String()
    endorser = Field(lambda: NymTxn)
    author = Field(lambda: NymTxn)
    txn_time = String()
    attrib = String()

    def resolve_txn_type(parent, info):
        return parent["data"]["txn"]["meta"]

    @classmethod
    def resolve_type(cls, instance, info):
        if instance["data"]["txn"]["meta"] == "NYM":
            return NymTxn
        else:
            return BaseTxn

    def resolve_endorser(parent, info):
        print("ENDORSER METADATA", parent["data"]["txn"]["metadata"])
        if 'endorser' in parent["data"]["txn"]["metadata"]:
            endorser = parent["data"]["txn"]["metadata"]["endorser"]
            print("Endorser DID", endorser)

            TXN = DbQuery()
            return db.get((TXN['data']['txn']['data']['dest'] == endorser))

        else:
            print('Not an Endorser')
            return None

    def resolve_author(parent, info):
        if 'from' in parent["data"]["txn"]["metadata"]:
            TXN = DbQuery()
            from_did = parent["data"]["txn"]["metadata"]['from']
            print(from_did)
            return db.get((TXN['data']['txn']['data']['dest'] == from_did) & (TXN['data']['txn']['type'] == "1"))
        else:
            return None

    def resolve_txn_time(parent, info):
        if 'txnTime' in parent["data"]["txnMetadata"]:
            txn_time_epoch = parent["data"]["txnMetadata"]["txnTime"]
            txn_time = datetime.datetime.fromtimestamp(txn_time_epoch).strftime('%Y-%m-%d %H:%M:%S') # formated to 12-3-2020 21:27:49
            txn_date = datetime.datetime.fromtimestamp(txn_time_epoch).strftime('%Y-%m-%d') # formated to 12-3-2020
            print('TIME IS: ', txn_date)
            return txn_time
        else:
            txn_time, txn_date = "", ""
            return txn_time

    # def resolve_schema(parent, info):
    #     if parent["data"]["txn"]["meta"] == "SCHEMA":
    #         txn_schema_attribs = parent["data"]["txn"]["data"]["data"]["attr_names"]
    #         txn_schema_name = parent["data"]["txn"]["data"]["data"]["name"]
    #         txn_schema_version = parent["data"]["txn"]["data"]["data"]["version"]
    #         print('Schema : ', txn_schema_name, txn_schema_version, txn_schema_attribs)
    #         return txn_schema_name, txn_schema_version, txn_schema_attribs
    #     else:
    #         txn_schema_name, txn_schema_version, txn_schema_attribs = "", "",""
    #         return txn_schema_name, txn_schema_version, txn_schema_attribs

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
    did = ID(required=True)
    # id_from = ID()
    # id_dest = ID()
    verkey = String(required=True)
    txns_authored = List(lambda: Transaction)
    role = String()
    # schema
    # cred_def

    created_schema = List(lambda : Schema)

    created_cred = List(lambda: CredDef)

    nym_txn = Field(lambda: NymTxn)


    def resolve_did(parent, info):
        print("ID", parent)
        return parent['dest']

    def resolve_created_schema(parent, info):
        TXN = DbQuery()
        schema_txns = db.search((TXN["data"]["txn"]["metadata"]['from'] == parent["dest"]) & (TXN["data"]["txn"]["type"] == "101"))
        schemas = []
        ## TODO create common schema parsing
        for txn in schema_txns:
            schema = txn["data"]["txn"]["data"]["data"]
            schema["id"] = txn["data"]["txnMetadata"]["txnId"]
            schemas.append(schema)
        return schemas

    def resolve_created_cred(parent, info):
        TXN = DbQuery()
        cred_txns = db.search((TXN["data"]["txn"]["metadata"]['from'] == parent["dest"]) & (TXN["data"]["txn"]["type"] == "102"))
        creds = []
        ## TODO create common cred parsing
        for txn in cred_txns:
            cred = txn["data"]["txn"]["data"]["data"]
            cred["id"] = txn["data"]["txnMetadata"]["txnId"]
            creds.append(cred)
        return creds

    # def resolve_verkey(parent, info):
    #     return parent["verkey"]

    def resolve_txns_authored(parent, info):
        TXN = DbQuery()
        return db.search(TXN["data"]["txn"]["metadata"]['from'] == parent["dest"])

    def resolve_nym_txn(parent, info):
        TXN = DbQuery()
        result = db.get(TXN["data"]["txn"]["data"]['dest'] == parent['dest'])
        print(result)
        return result

class Schema(ObjectType):
    id = String(required=True)
    schema_txn = Field(lambda : SchemaTxn)
    attr_names = List(String)
    name = String(required=True)
    version = String(required=True)

    creator = Field(lambda : DID)

    def resolve_schema_txn(parent, info):
        TXN = DbQuery()
        return db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

    ## TODO Would be good to traverse graphQl here rather than 2 db queries
    def resolve_creator(parent, info):
        TXN = DbQuery()
        # txn = db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

        did = parent["id"].split(":")[0]

        nymTxn = db.get(TXN["data"]["txn"]["data"]['dest'] == did)
        return nymTxn['data']['txn']['data']


class SchemaTxn(ObjectType):
    class Meta:
        interfaces = (Transaction, )

    schema = Field(lambda : Schema)

    def resolve_schema(parent, info):
        schema = parent["data"]["txn"]["data"]["data"]
        schema["id"] = parent["data"]["txnMetadata"]["txnId"]
        return schema


class CredDef(ObjectType):
    id = String(required=True)
    cred_txn = Field(lambda : CredDefTxn)
    primary = List(String)
    revocation = List(String)

    creator = Field(lambda : DID)

    def resolve_cred_txn(parent, info):
        TXN = DbQuery()
        return db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

    ## TODO Would be good to traverse graphQl here rather than 2 db queries
    def resolve_creator(parent, info):
        TXN = DbQuery()
        # txn = db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

        did = parent["id"].split(":")[0]

        nymTxn = db.get(TXN["data"]["txn"]["data"]['dest'] == did)
        return nymTxn['data']['txn']['data']

class CredDefTxn(ObjectType):
    class Meta:
        interfaces = (Transaction, )

        cred = Field(lambda: CredDef)

        def resolve_cred(parent, info):
            cred = parent["data"]["txn"]["data"]["data"]
            cred["id"] = parent["data"]["txnMetadata"]["txnId"]
            print(cred)
            return cred

class NymTxn(ObjectType):
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

    get_did = Field(DID, did=String(required=True))

    get_schema = Field(Schema, id=String())

    get_cred = Field(CredDef, id=String())

    # nym_by_did = Field(NymTxn, did=String(required=True))

    @staticmethod
    def resolve_say_hello(parent, info, name):
        return f'Hello {name}'

    def resolve_get_txns(self, info):
        results = []        # Create a list of Dictionary objects to return
        results = db.all()
        return results

    def resolve_get_txn_by_id(self,info, seqNo):
        TXN = DbQuery()
        return db.get(TXN['seqNo'] == seqNo)

    def resolve_get_did(self,info, did):
        TXN = DbQuery()
        ## TODO this should just be the from DIDs
        # print((TXN["data"]["txn"]["metadata"]["from"] == id) | (TXN["data"]["txn"]["metadata"]["dest"] == id))
        result = db.get(TXN['data']['txn']['data']['dest'] == did)
        return result['data']['txn']['data']

    def resolve_get_schema(self,info, id):
        ## TODO Extract tx time from metadata
        print(id)
        TXN = DbQuery()
        result = db.get(TXN["data"]["txnMetadata"]["txnId"] == id)
        print(result)
        schema = result["data"]["txn"]["data"]["data"]
        schema["id"] = result["data"]["txnMetadata"]["txnId"]

        return schema

    def resolve_get_cred(self,info, id):
        ## TODO Extract tx time from metadata
        print(id)
        TXN = DbQuery()
        result = db.get(TXN["data"]["txnMetadata"]["txnId"] == id)
        print(result)
        cred = result["data"]["txn"]["data"]["data"]
        cred["id"] = result["data"]["txnMetadata"]["txnId"]

        return cred

schema = GqSchema(query=Query, types=[BaseTxn, NymTxn, DID, Schema, SchemaTxn, CredDef, CredDefTxn])