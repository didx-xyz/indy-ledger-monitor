from graphene import String, ObjectType, List, Field, Int
from tinydb import TinyDB, Query
import json

def tinydb_conn():
    db = TinyDB('../../ledger_data/indy_tinydb.json')
    return db

class NYMType(ObjectType):
  nym = String(required=True)

class NYMType1(ObjectType):
  nym = String()

class ALLType(ObjectType):
    seqNo = String()
    data = String()
    reqId = String()

class DID(ObjectType):
    endorser = DID()

# Our inner dictionary defined as an object
class InnerItem(ObjectType):
    seqNo = Int()
    data = String()

# Our outer dictionary as an object
class Dictionary(ObjectType):
    key = String()
    # value = Field(InnerItem)

# Have a look at this article
# https://stackoverflow.com/questions/46402182/graphene-graphql-dictionary-as-a-type

class Query(ObjectType):
    say_hello = String(name=String(default_value='Test Driven'))
    get_NYMs = List(NYMType)
    get_ALL = List(ALLType)
    get_TXN = Field(List(ALLType), id=String())
    get_ALLTX = Field(List(Dictionary))

    @staticmethod
    def resolve_say_hello(parent, info, name):
        return f'Hello {name}'

    @staticmethod
    def resolve_get_NYMs(parent, info):
        NYM = Query()
        db = tinydb_conn()
        nym_list = db.search(NYM.id == '1')
        return nym_list

    def resolve_get_TXN(self, info, id):
        db = TinyDB('../../ledger_data/indy_tinydb.json')
        TXN = Query()
        print(db.search(TXN.seqNo == id))
        return db.search(TXN.seqNo == id)

    def resolve_get_ALL(self, info):
        db = TinyDB('../../ledger_data/indy_tinydb.json')
        return db.all()

    def resolve_get_ALLTX(self, info):
        results = []        # Create a list of Dictionary objects to return
        db = TinyDB('../../ledger_data/indy_tinydb.json')
        results = db.all()
        print(type(results))
        # Now iterate through your dictionary to create objects for each item
        for item in results:
            # inner_item = InnerItem[item['seqNo'], item['data']]
            for key in item:
                # print(key)
                # dictionary = Dictionary(key, inner_item)
                dictionary = Dictionary(key)
                results.append(dictionary)
        return results