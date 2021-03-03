from graphene import String, ObjectType, List, Field, Int, ID, Interface, Schema
from tinydb import TinyDB, Query as DbQuery
import json

db = TinyDB('../../ledger_data/indy_tinydb.json')
def tinydb_conn():
    db = TinyDB('../../ledger_data/indy_tinydb.json')
    return db


class Transaction(Interface):
    seqNo = ID(required=True)
    reqId = String(required=True)

    txn_type = String()
    endorser = Field(lambda: Nym)

    author = Field(lambda: Nym)

    def resolve_txn_type(parent, info):
        return parent["data"]["txn"]["meta"]

    @classmethod
    def resolve_type(cls, instance, info):
        if instance["data"]["txn"]["meta"] == "NYM":
            return Nym
        else:
            return BaseTxn

    def resolve_endorser(parent, info):
        print("METADATA", parent["data"]["txn"]["metadata"])
        if 'endorser' in parent["data"]["txn"]["metadata"]:
            endorser = parent["data"]["txn"]["metadata"]["endorser"]
            print("Endorser DID", endorser)

            TXN = DbQuery()
            return db.search((TXN['data']['txn']['data']['dest'] == endorser))[0]

        else:
            return None

    def resolve_author(parent, info):
        if 'from' in parent["data"]["txn"]["metadata"]:
            TXN = DbQuery()
            from_did = parent["data"]["txn"]["metadata"]['from']
            print(from_did)
            return db.search((TXN['data']['txn']['data']['dest'] == from_did) & (TXN['data']['txn']['meta'] == 'NYM'))[0]
        else:
            return None




class DID(ObjectType):
    id = ID(required=True)
    verkey = String(required=True)
    tx_authored = List(lambda: Transaction)

    # schema
    # cred_def

    def resolve_id(parent, info):
        print("ID", parent)
        return parent["dest"]

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

# Have a look at this article
# https://stackoverflow.com/questions/46402182/graphene-graphql-dictionary-as-a-type

class Query(ObjectType):
    say_hello = String(name=String(default_value='Test Driven'))
    get_txns = List(Transaction)

    get_txn_by_id = Field(Transaction, seqNo=Int(required=True))

    # nym_by_did = Field(Nym, did=String(required=True))

    # get_by_did = Field(DID, id=ID)

    @staticmethod
    def resolve_say_hello(parent, info, name):
        return f'Hello {name}'


    def resolve_get_txns(self, info):
        results = []        # Create a list of Dictionary objects to return
        results = db.all()
        print(type(results))
        # Now iterate through your dictionary to create objects for each item
        # for item in results:
        #     results.append(Transaction(item))
            # inner_item = InnerItem[item['seqNo'], item['data']]
            # for key in item:
            #     # print(key)
            #     # dictionary = Dictionary(key, inner_item)
            #     dictionary = Dictionary(key)
            #     results.append(dictionary)
        print(results)
        return results

    def resolve_get_txn_by_id(self,info, seqNo):
        TXN = DbQuery()
        return db.search(TXN['seqNo'] == seqNo)[0]


schema = Schema(query=Query, types=[BaseTxn, Nym, DID])