import pickledb

def pickledb_conn():
    db = pickledb.load('/home/indy/ledger_data/indy_pickle.db', True)
    return db

def find_last():
    db = pickledb_conn()
    pos = len(db.getall()) + 1
    return pos