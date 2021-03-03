

def create_cred_def_from_data(data):
    cred = data["data"]["txn"]["data"]["data"]
    cred["id"] = data["data"]["txnMetadata"]["txnId"]
    cred["schema_ref"] = data["data"]["txn"]["data"]["ref"]
    return cred

def create_schema_from_data(data):
    schema = data["data"]["txn"]["data"]["data"]
    schema["id"] = data["data"]["txnMetadata"]["txnId"]
    return schema