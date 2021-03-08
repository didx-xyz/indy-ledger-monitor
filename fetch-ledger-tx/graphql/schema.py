from graphene import String, ObjectType, List, Field, Int, ID, Boolean, Interface, Schema as GqSchema, relay, DateTime
from tinydb import TinyDB, Query as DbQuery
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from tinydb_smartcache import SmartCacheTable

import datetime
import json

TinyDB.table_class = SmartCacheTable
db = TinyDB('../ledger_data/indy_mainnet_tinydb.json'
            '', storage=CachingMiddleware(JSONStorage))



class Transaction(Interface):
    class Meta:
        interfaces = (relay.Node, )
    seqNo = ID(required=True)
    reqId = String(required=True)
    txn_type = String()
    endorser = Field(lambda: DID)
    author = Field(lambda: DID)
    txn_time = DateTime()

    def resolve_txn_type(parent, info):
        # return parent["data"]["txn"]["meta"]
        txn_type_int = parent["data"]["txn"]["type"]

        if txn_type_int == '1':
            txn_type = 'NYM'
        elif txn_type_int == '100':
            txn_type = 'ATTRIB'
        elif txn_type_int == '101':
            txn_type = 'SCHEMA'
        elif txn_type_int == '102':
            txn_type = 'CLAIM_DEF'
        elif txn_type_int == '113':
            txn_type = 'REVOC_REG_DEF'
        elif txn_type_int == '114':
            txn_type = 'REVOC_REG_ENTRY'
        elif txn_type_int == '200':
            txn_type = 'SET_CONTEXT'
        elif txn_type_int == '0':
            txn_type = 'NODE'
        elif txn_type_int == '10':
            txn_type = 'POOL_UPGRADE'
        elif txn_type_int == '11':
            txn_type = 'NODE_UPGRADE'
        elif txn_type_int == '11':
            txn_type = 'POOL_CONFIG'
        elif txn_type_int == '12':
            txn_type = 'AUTH_RULE'
        elif txn_type_int == '12':
            txn_type = 'AUTH_RULES'
        elif txn_type_int == '4':
            txn_type = 'TXN_AUTHOR_AGREEMENT'
        elif txn_type_int == '5':
            txn_type = 'TXN_AUTHOR_AGREEMENT_AML'
        elif txn_type_int == '20000':
            txn_type = 'SET_FEES'
        else:
            txn_type = 'ERROR'

        return txn_type

    @classmethod
    def resolve_type(cls, instance, info):
        type = instance["data"]["txn"]["type"]

        if type == "1":
            return DID
        elif type == "100":
            return Attribute
        elif type == "101":
            return Schema
        elif type == "102":
            return CredDef
        else:
            return BaseTxn

    def resolve_endorser(parent, info):
        # print("ENDORSER METADATA", parent["data"]["txn"]["metadata"])
        if 'endorser' in parent["data"]["txn"]["metadata"]:
            endorser = parent["data"]["txn"]["metadata"]["endorser"]
            # print("Endorser DID", endorser)

            TXN = DbQuery()
            return db.get((TXN['data']['txn']['data']['dest'] == endorser))

        else:
            TXN = DbQuery()
            from_did = parent["data"]["txn"]["metadata"]['from']
            # print(from_did)
            return db.get((TXN['data']['txn']['data']['dest'] == from_did) & (TXN['data']['txn']['type'] == "1"))

    def resolve_author(parent, info):
        if 'from' in parent["data"]["txn"]["metadata"]:
            TXN = DbQuery()
            from_did = parent["data"]["txn"]["metadata"]['from']
            # print(from_did)
            return db.get((TXN['data']['txn']['data']['dest'] == from_did) & (TXN['data']['txn']['type'] == "1"))
        else:
            return None

    def resolve_txn_time(parent, info):
        if 'txnTime' in parent["data"]["txnMetadata"]:
            txn_time_epoch = parent["data"]["txnMetadata"]["txnTime"]
            return datetime.datetime.fromtimestamp(txn_time_epoch)
        else:
            return None

class TransactionConnection(relay.Connection):
    class Meta:
        node = Transaction
    count = Int()

    def resolve_count(root, info):
        return len(root.edges)


class Attribute(ObjectType):
    class Meta:
        interfaces = (relay.Node, Transaction)
    endpoint = String()
    raw = String()
    did = Field(lambda : DID)
    # attrib_txn = Field(lambda: AttribTxn)

    def resolve_did(parent, info):
        TXN = DbQuery()
        result = db.get((TXN['data']['txn']['data']['dest'] == parent["dest"]) & (TXN['data']['txn']['type'] == "1"))
        return result['data']['txn']['data']

    def resolve_raw(parent, info):
        try:
            return parent["data"]["txn"]["data"]["dest"]["raw"]
        except:
            return None

    def resolve_endpoint(parent, info):
        if "endpoint" in parent["data"]["txn"]["data"]["dest"]:
            return parent["data"]["txn"]["data"]["dest"]["endpoint"]
        else:
            return None

    # def resolve_attrib_txn(parent, info):
    #     TXN = DbQuery()
    #     return db.get(TXN["seqNo"] == parent["seqNo"])

class AttributeConnection(relay.Connection):
    class Meta:
        node = Attribute
    count = Int()

    def resolve_count(root, info):
        return len(root.edges)








class CredDef(ObjectType):
    class Meta:
        interfaces = (relay.Node, Transaction)
    id = ID(required=True)
    ## TODO Maybe model the crypto
    # primary = List(String)
    # revocation = List(String)

    is_revocable = Boolean()

    schema = Field(lambda : Schema)

    def resolve_id(parent, info):
        return parent["data"]["txnMetadata"]["txnId"]


    def resolve_is_revocable(parent, info):
        # print(parent["revocation"])
        return "revocation" in parent["data"]["txn"]["data"]["data"]

    def resolve_schema(parent, info):
        TXN = DbQuery()
        schema_txn = db.get(TXN["seqNo"] == parent["data"]["txn"]["data"]["ref"])
        return schema_txn




class CredDefConnection(relay.Connection):
    class Meta:
        node = CredDef

    count = Int()
    def resolve_count(root, info):
        return len(root.edges)


class Schema(ObjectType):
    class Meta:
        interfaces = (relay.Node, Transaction)
    id = ID(required=True)
    # schema_txn = Field(lambda : SchemaTxn)
    attr_names = List(String)
    name = String(required=True)
    version = String(required=True)

    definitions = relay.ConnectionField(CredDefConnection)

    definitions_count = Int()

    # def resolve_schema_txn(parent, info):
    #     TXN = DbQuery()
    #     return db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["id"])

    def resolve_id(parent, info):
        return parent["data"]["txnMetadata"]["txnId"]

    def resolve_name(parent, info):
        return parent["data"]["txn"]["data"]["data"]["name"]

    def resolve_version(parent, info):
        return parent["data"]["txn"]["data"]["data"]["version"]

    def resolve_attr_names(parent, info):
        return parent["data"]["txn"]["data"]["data"]["attr_names"]


    def resolve_definitions(parent, info, **kwargs):
        TXN = DbQuery()

        schema_txn = db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["data"]["txnMetadata"]["txnId"])

        cred_def_txns = db.search(TXN["data"]["txn"]["data"]["ref"] == schema_txn["seqNo"])

        return cred_def_txns

    def resolve_definitions_count(parent, info):
        TXN = DbQuery()

        schema_txn = db.get(TXN["data"]["txnMetadata"]["txnId"] == parent["data"]["txnMetadata"]["txnId"])

        return db.count(TXN["data"]["txn"]["data"]["ref"] == schema_txn["seqNo"])

class SchemaConnection(relay.Connection):
    class Meta:
        node = Schema
    count = Int()

    def resolve_count(root, info):
        return len(root.edges)




class BaseTxn(ObjectType):
    class Meta:
        interfaces = (Transaction, )

    data = String()

    def resolve_data(parent, info):
        return parent['data']

class DID(ObjectType):
    class Meta:
        interfaces = (relay.Node, Transaction)
    did = ID(required=True)
    # id_from = ID()
    # id_dest = ID()
    verkey = String(required=True)
    authored_txns = relay.ConnectionField(TransactionConnection)
    role = String()
    alias = String()
    # schema
    # cred_def
    attributes = relay.ConnectionField(AttributeConnection)

    created_schema = relay.ConnectionField(SchemaConnection)

    created_dids = relay.ConnectionField(lambda : DIDConnection)
    created_dids_count = Int()

    created_definitions = relay.ConnectionField(CredDefConnection)

    created_definitions_count = Int()

    created_schema_count = Int()


    def resolve_role(parent, info):
        try:
            return parent['data']['txn']['data']['role']
        except:
            return None

    def resolve_alias(parent, info):
        try:
            return parent['data']['txn']['data']['alias']
        except:
            return None

    def resolve_verkey(parent, info):
        return parent['data']['txn']['data']["verkey"]

    def resolve_did(parent, info):
        return parent['data']['txn']['data']['dest']

    def resolve_created_dids(parent, info):
        TXN = DbQuery()

        did_txns = db.search((TXN["data"]["txn"]["metadata"]['from'] == parent['data']['txn']['data']["dest"]) & (TXN["data"]["txn"]["type"] == "1"))

        return did_txns

    def resolve_created_dids_count(parent, info):
        TXN = DbQuery()

        return db.count((TXN["data"]["txn"]["metadata"]['from'] == parent['data']['txn']['data']["dest"]) & (TXN["data"]["txn"]["type"] == "1"))

    def resolve_created_schema(parent, info, **kwargs):
        TXN = DbQuery()
        schema_txns = db.search((TXN["data"]["txn"]["metadata"]['from'] == parent['data']['txn']['data']["dest"]) & (TXN["data"]["txn"]["type"] == "101"))

        return schema_txns

    def resolve_created_schema_count(parent, info):
        TXN = DbQuery()
        return db.count((TXN["data"]["txn"]["metadata"]['from'] == parent['data']['txn']['data']["dest"]) & (TXN["data"]["txn"]["type"] == "101"))

    def resolve_created_definitions(parent, info):
        TXN = DbQuery()
        cred_def_txns = db.search((TXN["data"]["txn"]["metadata"]['from'] == parent['data']['txn']['data']["dest"]) & (TXN["data"]["txn"]["type"] == "102"))

        return cred_def_txns

    def resolve_created_definitions_count(parent, info):
        TXN = DbQuery()
        return db.count((TXN["data"]["txn"]["metadata"]['from'] == parent['data']['txn']['data']["dest"]) & (TXN["data"]["txn"]["type"] == "102"))


    def resolve_authored_txns(parent, info):
        TXN = DbQuery()
        return db.search(TXN["data"]["txn"]["metadata"]['from'] == parent['data']['txn']['data']["dest"])

    def resolve_attributes(parent, info, **kwargs):
        TXN = DbQuery()
        attr_txns = db.search((TXN["data"]["txn"]["data"]["dest"] == parent['data']['txn']['data']["dest"]) & (TXN["data"]["txn"]["type"] == "100"))

        return attr_txns

class DIDConnection(relay.Connection):
    class Meta:
        node = DID
    count = Int()

    def resolve_count(root, info):
        return len(root.edges)

class Query(ObjectType):
    get_txns = relay.ConnectionField(TransactionConnection, author=String())

    get_txn_by_id = Field(Transaction, seqNo=Int(required=True))

    did = Field(DID, did=String(required=True))

    get_schema = Field(Schema, id=String())

    get_definition = Field(CredDef, id=String())

    dids = relay.ConnectionField(DIDConnection, endorser=String())

    schemas = relay.ConnectionField(SchemaConnection, author=String(), endorser=String())

    definitions = relay.ConnectionField(CredDefConnection)

    # nym_by_did = Field(NymTxn, did=String(required=True))

    def resolve_dids(root, info, **kwargs):
        TXN = DbQuery()
        nym_txns = None
        if "endorser" in kwargs:
            nym_txns= db.search((TXN['data']['txn']['type'] == "1") & (TXN["data"]["txn"]["metadata"]["endorser"] == kwargs["endorser"]))
        else:
            nym_txns = db.search((TXN['data']['txn']['type'] == "1"))

        return nym_txns


    def resolve_schemas(self, info, **kwargs):
        TXN = DbQuery()
        schema_txns = None
        ## TODO need a better way to handle multiple args into a single query
        # I dont like this approach
        if "endorser" in kwargs and "author" in kwargs:
            schema_txns= db.search((TXN['data']['txn']['type'] == "101") & (TXN["data"]["txn"]["metadata"]["endorser"] == kwargs["endorser"]) & (TXN["data"]["txn"]["metadata"]["from"] == kwargs["author"]))

        elif "endorser" in kwargs:
            schema_txns= db.search((TXN['data']['txn']['type'] == "101") & (TXN["data"]["txn"]["metadata"]["endorser"] == kwargs["endorser"]))
        elif "author" in kwargs:
            schema_txns= db.search((TXN['data']['txn']['type'] == "101") & (TXN["data"]["txn"]["metadata"]["from"] == kwargs["author"]))
        else:
            schema_txns = db.search((TXN['data']['txn']['type'] == "101"))



        return schema_txns

    def resolve_definitions(self, info, **kwargs):
        TXN = DbQuery()
        def_txns = db.search((TXN['data']['txn']['type'] == "101"))


        return def_txns

    def resolve_get_txns(self, info, **kwargs):
        TXN = DbQuery()
        if "author" in kwargs:
            return db.search(TXN["data"]["txn"]["metadata"]['from'] == kwargs["author"])
        else:
            return db.all()

    def resolve_get_txn_by_id(self,info, seqNo):
        TXN = DbQuery()
        return db.get(TXN['seqNo'] == seqNo)

    def resolve_did(self,info, did):
        TXN = DbQuery()
        result = db.get((TXN['data']['txn']['data']['dest'] == did) & (TXN['data']['txn']['type'] == "1"))
        return result

    def resolve_get_schema(self,info, id):
        ## TODO Extract tx time from metadata
        TXN = DbQuery()
        result = db.get(TXN["data"]["txnMetadata"]["txnId"] == id)

        return result

    def resolve_get_definition(self,info, id):
        ## TODO Extract tx time from metadata
        TXN = DbQuery()
        result = db.get(TXN["data"]["txnMetadata"]["txnId"] == id)

        return result

schema = GqSchema(query=Query, types=[BaseTxn, DID, Schema, CredDef, DIDConnection, Attribute, TransactionConnection, SchemaConnection, CredDefConnection])

