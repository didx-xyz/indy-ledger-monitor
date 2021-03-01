import argparse
import asyncio
import base58
import base64
import json
import os
import sys
import datetime
import urllib.request
import re
from typing import Tuple

import nacl.signing
from indy_vdr.bindings import version
import indy_vdr
from indy_vdr.ledger import (
    build_custom_request,
    build_get_txn_request,
    build_get_acceptance_mechanisms_request,
    build_get_txn_author_agreement_request,
    build_get_validator_info_request,
    build_get_cred_def_request,
    build_get_revoc_reg_def_request,
    build_get_revoc_reg_request,
    build_get_revoc_reg_delta_request,
    build_get_schema_request,
    # build_rich_schema_request,
    # build_get_schema_object_by_id_request,
    # build_get_schema_object_by_metadata_request,
    prepare_txn_author_agreement_acceptance,
    build_get_nym_request,
    LedgerType,
    Request,
)
from indy_vdr.pool import Pool, open_pool
from plugin_collection import PluginCollection
import time

verbose = False

def log(*args):
    if verbose:
        print(*args, "\n", file=sys.stderr)

class DidKey:
    def __init__(self, seed):
        seed = seed_as_bytes(seed)
        self.sk = nacl.signing.SigningKey(seed)
        self.vk = bytes(self.sk.verify_key)
        self.did = base58.b58encode(self.vk[:16]).decode("ascii")
        self.verkey = base58.b58encode(self.vk).decode("ascii")

    def sign_request(self, req: Request):
        signed = self.sk.sign(req.signature_input)
        req.set_signature(signed.signature)


def seed_as_bytes(seed):
    if not seed or isinstance(seed, bytes):
        return seed
    if len(seed) != 32:
        return base64.b64decode(seed)
    return seed.encode("ascii")

async def get_schema_by_Id(pool: Pool, schemaId):
    req = build_get_schema_request(
        None, schemaId
    )
    return await pool.submit_request(req)

async def get_pool_txns(pool: Pool):
    pool_txns = await pool.get_transactions()
    return pool_txns

async def get_txn(pool: Pool, seq_no: int):
    req = build_get_txn_request(None, LedgerType.DOMAIN, seq_no)
    return await pool.submit_request(req)

async def get_txn_range(pool: Pool, seq_nos):
    return [await get_txn(pool, seq_no) for seq_no in seq_nos]

async def get_cred_by_Id(pool: Pool, credId):
    req = build_get_cred_def_request(
        None, credId
    )
    return await pool.submit_request(req)

async def fetch_ledger_tx(genesis_path: str, schemaid: str = None, pooltx: bool = False, ident: DidKey = None, maintxr: range = None, maintx: str = None, credid: str = None, network_name: str = None):
    while True:
        try:
            pool = await open_pool(transactions_path=genesis_path)
        except:
            if verbose: print("Pool Timed Out! Trying again...")
            continue
        break
    
    result = []

    if schemaid:
        # "QXdMLmAKZmQBhnvXHxKn78:2:SURFNetSchema:1.0"
        response = await get_schema_by_Id(pool, schemaid)
        print(json.dumps(response, indent=2))

    if pooltx:
        pooltx_response = await get_pool_txns(pool)
        print(pooltx_response)

    if maintx:
        maintx_response = await get_txn(pool, int(maintx))
        print(json.dumps(maintx_response, indent=2))
    
    if maintxr:
        maintxr_response = await get_txn_range(pool, list(maintxr))
        print(json.dumps(maintxr_response, indent=2))

    if credid:
        response = await get_cred_by_Id(pool, credid)
        print(json.dumps(response, indent=2))

    #TODO Implement get nym request lookup
    # req = build_get_nym_request(None, NYM)
    # print("Get revoc reg def request:", req.body)

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

    await monitor_plugins.apply_all_plugins_on_value(result, pool, network_name)

def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))

def download_genesis_file(url: str, target_local_path: str):
    log("Fetching genesis file ...")
    target_local_path = f"{get_script_dir()}/genesis.txn"
    urllib.request.urlretrieve(url, target_local_path)

def load_network_list():
    with open(f"{get_script_dir()}/networks.json") as json_file:
        networks = json.load(json_file)
    return networks

def list_networks():
    networks = load_network_list()
    return networks.keys()

def parseNumList(string):
    m = re.match(r'(\d+)(?:-(\d+))?$', string)
    # ^ (or use .split('-'). anyway you like.)
    if not m:
        raise ArgumentTypeError("'" + string + "' is not a range of number. Expected forms like '0-5' or '2'.")
    start = m.group(1)
    end = m.group(2) or start
    return list(range(int(start,10), int(end,10)+1))

if __name__ == "__main__":
    monitor_plugins = PluginCollection('plugins')

    parser = argparse.ArgumentParser(description="Fetch transaction related details from indy based ledgers")
    parser.add_argument("--net", choices=list_networks(), help="Connect to a known network using an ID.")
    parser.add_argument("--list-nets", action="store_true", help="List known networks.")
    parser.add_argument("--genesis-url", default=os.environ.get('GENESIS_URL') , help="The url to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_URL' environment variable.")
    parser.add_argument("--genesis-path", default=os.getenv("GENESIS_PATH") or f"{get_script_dir()}/genesis.txn" , help="The path to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_PATH' environment variable.")
    parser.add_argument("-s", "--seed", default=os.environ.get('SEED') , help="The privileged DID seed to use for the ledger requests.  Can be specified using the 'SEED' environment variable.")
    parser.add_argument("-pooltx", "--pooltx", help="Get pool ledger transactions.")
    parser.add_argument("-schemaid", "--schemaid", help="Get a specific schema from ledger.")
    parser.add_argument("-maintx", "--maintx", help="Get a specific transaction number from main ledger.")
    parser.add_argument("-maintxr", "--maintxrange", type=parseNumList, help="Get a range of transactions from main ledger.")

    parser.add_argument("-credid", "--credid", help="Get a specific schema from ledger.")
    parser.add_argument("-a", "--anonymous", action="store_true", help="Perform requests anonymously, without requiring privileged DID seed.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")

    monitor_plugins.get_parse_args(parser)
    args, unknown = parser.parse_known_args()

    verbose = args.verbose

    monitor_plugins.load_all_parse_args(args)

    if args.list_nets:
        print(json.dumps(load_network_list(), indent=2))
        exit()

    if args.net:
        log("Loading known network list ...")
        networks = load_network_list()
        if args.net in networks:
            log("Connecting to '{0}' ...".format(networks[args.net]["name"]))
            args.genesis_url = networks[args.net]["genesisUrl"]
            network_name = networks[args.net]["name"]

    if args.genesis_url:
        download_genesis_file(args.genesis_url, args.genesis_path)
    if not os.path.exists(args.genesis_path):
        print("Set the GENESIS_URL or GENESIS_PATH environment variable or argument.\n", file=sys.stderr)
        parser.print_help()
        exit()

    did_seed = None if args.anonymous else args.seed
    if not did_seed and not args.anonymous:
        print("Set the SEED environment variable or argument, or specify the anonymous flag.\n", file=sys.stderr)
        parser.print_help()
        exit()

    log("indy-vdr version:", indy_vdr.version())
    if did_seed:
        ident = DidKey(did_seed)
        log("DID:", ident.did, " Verkey:", ident.verkey)
    else:
        ident = None

    # asyncio.get_event_loop().run_until_complete(fetch_status(args.genesis_path, args.nodes, ident, args.status, args.alerts))
    asyncio.get_event_loop().run_until_complete(fetch_ledger_tx(args.genesis_path, args.schemaid, args.pooltx, ident, args.maintxrange, args.maintx, args.credid, network_name))