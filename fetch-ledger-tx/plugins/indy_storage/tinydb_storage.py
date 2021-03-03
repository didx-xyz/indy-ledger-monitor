from tinydb import TinyDB, Query

def tinydb_conn():
    db = TinyDB('/home/indy/ledger_data/indy_tinydb.json')
    return db

def find_last():
    ## TODO
    pass
    # db = pickledb_conn()
    # pos = len(db.getall()) + 1
    # return pos
