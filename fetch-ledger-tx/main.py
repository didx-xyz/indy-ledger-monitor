import argparse
import asyncio
import os
import json
import indy_vdr
from util import (
    enable_verbose,
    log,
    create_did
)
from fetch_ledger_tx import FetchLedgerTX
from pool import PoolCollection
from networks import Networks
from plugin_collection import PluginCollection

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch transaction related details from indy based ledgers")
    parser.add_argument("--net", choices=Networks.get_ids(), help="Connect to a known network using an ID.")
    parser.add_argument("--list-nets", action="store_true", help="List known networks.")
    parser.add_argument("--genesis-url", default=os.environ.get('GENESIS_URL') , help="The url to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_URL' environment variable.")
    parser.add_argument("--genesis-path", default=os.getenv("GENESIS_PATH"), help="The path to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_PATH' environment variable.")
    parser.add_argument("-s", "--seed", default=os.environ.get('SEED') , help="The privileged DID seed to use for the ledger requests.  Can be specified using the 'SEED' environment variable. If DID seed is not given the request will run anonymously.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")

    monitor_plugins = PluginCollection('plugins')
    monitor_plugins.get_parse_args(parser)
    args, unknown = parser.parse_known_args()
    monitor_plugins.load_all_parse_args(args)

    enable_verbose(args.verbose)

    log("Starting from the command line ...")

    if args.list_nets:
        print(json.dumps(Networks.get_networks(), indent=2))
        exit()

    log("indy-vdr version:", indy_vdr.version())
    did_seed = None if not args.seed else args.seed
    ident = create_did(did_seed)
    networks = Networks()
    pool_collection = PoolCollection(args.verbose, networks)
    network = networks.resolve(args.net, args.genesis_url, args.genesis_path)
    node_info = FetchLedgerTX(args.verbose, pool_collection)
    result = asyncio.get_event_loop().run_until_complete(node_info.fetch(network.id, monitor_plugins, ident))
    print(json.dumps(result, indent=2))