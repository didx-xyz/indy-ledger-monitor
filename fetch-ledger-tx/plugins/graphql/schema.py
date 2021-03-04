from graphene import String, ObjectType, List, Field, Int, ID, Boolean, Interface, Schema as GqSchema, relay
from tinydb import TinyDB, Query as DbQuery
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

import datetime
import json
from helpers import create_cred_def_from_data, create_schema_from_data

db = TinyDB('../../ledger_data/indy_tinydb.json'
            '', storage=CachingMiddleware(JSONStorage))

class Transaction(Interface):
    seqNo = ID(required=True)
    reqId = String(required=True)
    txn_type = String()
    endorser = Field(lambda: NymTxn)
    author = Field(lambda: NymTxn)
    txn_time = String()

    def resolve_txn_type(parent, info):
        return parent["data"]["txn"]["meta"]

    @classmethod
    def resolve_type(cls, instance, info):
        type = instance["data"]["txn"]["type"]

        if type == "1":
            return NymTxn
        elif type == "101":
            return SchemaTxn
        elif type == "102":
            return CredDefTxn
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



class DID(ObjectType):
    class Meta:
        interfaces = (relay.Node, )
    did = ID(required=True)
    # id_from = ID()
    # id_dest = ID()
    verkey = String(required=True)
    txns_authored = List(lambda: Transaction)
    role = String()
    alias = String()
    # schema
    # cred_def
    attributes = List(lambda : Attribute)

    created_schema = List(lambda : Schema)

    created_dids = List(lambda : DID)
    created_dids_count = Int()

    created_definitions = List(lambda: CredDef)

    created_definitions_count = Int()

    created_schema_count = Int()

    nym_txn = Field(lambda: NymTxn)


    def resolve_did(parent, info):
        print("ID", parent)
        return parent['dest']

    def resolve_created_dids(parent, info):
        TXN = DbQuery()

        did_txns = db.search((TXN["data"]["txn"]["metadata"]['from'] == parent["dest"]) & (TXN["data"]["txn"]["type"] == "1"))
        dids = []
        for txn in did_txns:
            did = txn["data"]["txn"]["data"]
            dids.append(did)
        return dids

    def resolve_created_dids_count(parent, info):
        TXN = DbQuery()

        return db.count((TXN["data"]["txn"]["metadata"]['from'] == parent["dest"]) & (TXN["data"]["txn"]["type"] == "1"))

    def resolve_created_schema(parent, info):
        TXN = DbQuery()
        schema_txns = db.search((TXN["data"]["txn"]["metadata"]['from'] == parent["dest"]) & (TXN["data"]["txn"]["type"] == "101"))
        schemas = []
        ## TODO create common schema parsing
        for txn in schema_txns:
            schema = create_schema_from_data(txn)
            schemas.append(schema)
        return schemas

    def resolve_created_schema_count(parent, info):
        TXN = DbQuery()
        return db.count((TXN["data"]["txn"]["metadata"]['from'] == parent["dest"]) & (TXN["data"]["txn"]["type"] == "101"))

    def resolve_created_definitions(parent, info):
        TXN = DbQuery()
        cred_txns = db.search((TXN["data"]["txn"]["metadata"]['from'] == parent["dest"]) & (TXN["data"]["txn"]["type"] == "102"))
        creds = []
        ## TODO create common cred parsing
        for txn in cred_txns:
            cred = create_cred_def_from_data(txn)
            creds.append(cred)
        return creds

    def resolve_created_definitions_count(parent, info):
        TXN = DbQuery()
        return db.count((TXN["data"]["txn"]["metadata"]['from'] == parent["dest"]) & (TXN["data"]["txn"]["type"] == "102"))
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

    def resolve_attributes(parent, info):
        TXN = DbQuery()
        attr_txns = db.search((TXN["data"]["txn"]["data"]["dest"] == parent["dest"]) & (TXN["data"]["txn"]["type"] == "100"))

        attrs = []
        for txn in attr_txns:
            attrs.append(txn["data"]["txn"]["data"])

        return attrs

class DIDConnection(relay.Connection):
    class Meta:
        node = DID
    count = Int()

    def resolve_count(root, info):
        return len(root.edges)


class Schema(ObjectType):
    id = String(required=True)
    schema_txn = Field(lambda : SchemaTxn)
    attr_names = List(String)
    name = String(required=True)
    version = String(required=True)

    creator = Field(lambda : DID)

    definitions = List(lambda : CredDef)

    definitions_count = Int()

    def resolve_schema_txn(parent, info):
        TXN = DbQuery()
        return db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

    def resolve_creator(parent, info):
        TXN = DbQuery()
        # txn = db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

        did = parent["id"].split(":")[0]

        nymTxn = db.get((TXN["data"]["txn"]["data"]['dest'] == did) & (TXN['data']['txn']['type'] == "1"))
        return nymTxn['data']['txn']['data']

    def resolve_definitions(parent, info):
        TXN = DbQuery()

        schema_txn = db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

        cred_def_txns = db.search(TXN["data"]["txn"]["data"]["ref"] == schema_txn["seqNo"])
        cred_defs =[]
        for txn in cred_def_txns:
            cred_def = create_cred_def_from_data(txn)
            cred_defs.append(cred_def)

        return cred_defs

    def resolve_definitions_count(parent, info):
        TXN = DbQuery()

        schema_txn = db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

        return db.count(TXN["data"]["txn"]["data"]["ref"] == schema_txn["seqNo"])

class SchemaTxn(ObjectType):
    class Meta:
        interfaces = (Transaction, )

    schema = Field(lambda : Schema)

    def resolve_schema(parent, info):

        return create_schema_from_data(parent)

class CredDef(ObjectType):
    id = String(required=True)
    cred_txn = Field(lambda : CredDefTxn)
    ## TODO Maybe model the crypto
    # primary = List(String)
    # revocation = List(String)

    is_revocable = Boolean()

    creator = Field(lambda : DID)

    schema = Field(lambda : Schema)

    def resolve_cred_txn(parent, info):
        TXN = DbQuery()
        return db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

    def resolve_creator(parent, info):
        TXN = DbQuery()
        # txn = db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

        did = parent["id"].split(":")[0]

        nymTxn = db.get((TXN["data"]["txn"]["data"]['dest'] == did) & (TXN['data']['txn']['type'] == "1"))
        return nymTxn['data']['txn']['data']

    def resolve_is_revocable(parent, info):
        # print(parent["revocation"])
        return "revocation" in parent

    def resolve_schema(parent, info):
        TXN = DbQuery()
        schema_txn = db.get(TXN["seqNo"] == parent["schema_ref"])
        return create_schema_from_data(schema_txn)

class Attribute(ObjectType):
    endpoint = String()
    raw = String()
    did = Field(lambda : DID)

    def resolve_did(parent, info):
        TXN = DbQuery()
        result = db.get((TXN['data']['txn']['data']['dest'] == parent["dest"]) & (TXN['data']['txn']['type'] == "1"))
        return result['data']['txn']['data']

class CredDefTxn(ObjectType):
    class Meta:
        interfaces = (Transaction, )

        cred = Field(lambda: CredDef)

        def resolve_cred(parent, info):
            return create_cred_def_from_data(parent)

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
    get_txns = List(Transaction)

    get_txn_by_id = Field(Transaction, seqNo=Int(required=True))

    get_did = Field(DID, did=String(required=True))

    get_schema = Field(Schema, id=String())

    get_definition = Field(CredDef, id=String())

    dids = relay.ConnectionField(DIDConnection)

    # nym_by_did = Field(NymTxn, did=String(required=True))

    def resolve_dids(root, info, **kwargs):
        TXN = DbQuery()
        nym_txns = db.search((TXN['data']['txn']['type'] == "1"))
        dids = []
        for txn in nym_txns:
            dids.append(txn["data"]["txn"]["data"])

        return dids



    def resolve_get_txns(self, info):
        results = []        # Create a list of Dictionary objects to return
        results = db.all()
        return results

    def resolve_get_txn_by_id(self,info, seqNo):
        TXN = DbQuery()
        return db.get(TXN['seqNo'] == seqNo)

    def resolve_get_did(self,info, did):
        TXN = DbQuery()
        result = db.get((TXN['data']['txn']['data']['dest'] == did) & (TXN['data']['txn']['type'] == "1"))
        return result['data']['txn']['data']

    def resolve_get_schema(self,info, id):
        ## TODO Extract tx time from metadata
        print(id)
        TXN = DbQuery()
        result = db.get(TXN["data"]["txnMetadata"]["txnId"] == id)
        print(result)


        return create_schema_from_data(result)

    def resolve_get_definition(self,info, id):
        ## TODO Extract tx time from metadata
        print(id)
        TXN = DbQuery()
        result = db.get(TXN["data"]["txnMetadata"]["txnId"] == id)

        return create_cred_def_from_data(result)

schema = GqSchema(query=Query, types=[BaseTxn, NymTxn, DID, Schema, SchemaTxn, CredDef, CredDefTxn])