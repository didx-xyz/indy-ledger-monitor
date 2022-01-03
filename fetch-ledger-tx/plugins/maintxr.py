import plugin_collection

from indy_vdr.ledger import (
    build_get_txn_request,
    LedgerType,
)
import re

class main(plugin_collection.Plugin):
    def __init__(self):
        super().__init__()
        self.index = 3
        self.name = 'maintxr'
        self.description = ''
        self.type = ''
        self.maintxr = None

    def parse_args(self, parser):
        parser.add_argument("-maintxr", "--maintxrange", type=str, help="Get a range of transactions from main ledger.")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose
        
        if args.maintxrange:
            self.enabled = True

            m = re.match(r'(\d+)(?:-(\d+))?$', args.maintxrange)
            # ^ (or use .split('-'). anyway you like.)
            if not m:
                raise ArgumentTypeError("'" + args.maintxrange + "' is not a range of number. Expected forms like '0-5' or '2'.")
            start = m.group(1)
            end = m.group(2) or start
            self.maintxr = list(range(int(start,10), int(end,10)+1))


    async def perform_operation(self, pool, result, network_name):
        maintxr_response = await self.get_txn_range(pool, list(self.maintxr))

        result = result + [maintxr_response]
        return result

    async def get_txn(self, pool, seq_no: int):
        req = build_get_txn_request(None, LedgerType.DOMAIN, seq_no)
        return await pool.submit_request(req)

    async def get_txn_range(self, pool, seq_nos):
        return [await self.get_txn(pool, seq_no) for seq_no in seq_nos]