 #TODO Implement revocation lookups
# revoc_id = (
#     "L5wx9FUxCDpFJEdFc23jcn:4:L5wx9FUxCDpFJEdFc23jcn:3:CL:1954:"
#     "default:CL_ACCUM:c024e30d-f3eb-42c5-908a-ff885667588d"
# )
#
# req = build_get_revoc_reg_def_request(None, revoc_id)
# print("Get revoc reg def request:", req.body)
#
# req = build_get_revoc_reg_request(None, revoc_id, timestamp=1)
# print("Get revoc reg request:", req.body)
#
# req = build_get_revoc_reg_delta_request(None, revoc_id, from_ts=None, to_ts=1)
# print("Get revoc reg delta request:", req.body)

# req = build_rich_schema_request(
#     None, "did:sov:some_hash", '{"some": 1}', "test", "version", "sch", "1.0.0"
# )
# log("Get rich schema request:", req.body)

# req = build_get_schema_object_by_id_request(None, "did:sov:some_hash")
# log("Get rich schema GET request by ID:", req.body)
#
# req = build_get_schema_object_by_metadata_request(None, "sch", "test", "1.0.0")
# log("Get rich schema GET request by Metadata:", req.body)

"""
#parser.add_argument("-db", "--db", help="Dump main ledger transactions to DB")

import pickledb

def con_db():
    db = pickledb.load('./indy_pickle.db', False)
    return db

    if db:
        db = con_db()
        # Check if we have any previous records in DB
        print(db.getall())
        if len(db.getall()) == 0:
            print('New database, start dumping transactions from tx 0')
            db.set('0','No TX')
            maintxr_response = await get_txn_range(pool, list(range(1,10)))
            for tx in maintxr_response:
                print(tx['seqNo'])
                db.set(json.dumps(tx['seqNo']), json.dumps(tx))
            #"data": null,
        else:
            maintxr_response = await get_txn_range(pool, list(maintxr))
            #print(json.dumps(maintxr_response, indent=2))
            print(json.dumps(maintx_response['seqNo'], indent=2))
            db.set(json.dumps(maintx_response['seqNo']), json.dumps(maintx_response))

        print(db.getall())
        # Save DB
        print('Saving PickleDB Results: {}'.format(db.dump())
"""