import plugin_collection

from indy_vdr.ledger import (
    build_get_txn_request,
    LedgerType,
)

class main(plugin_collection.Plugin):
    def __init__(self):
        super().__init__()
        self.index = 3
        self.name = 'maintx'
        self.description = ''
        self.type = ''
        self.maintx = None

    def parse_args(self, parser):
        parser.add_argument("-maintx", "--maintx", help="Get a specific transaction number from main ledger.")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose
        
        if args.maintx:
            self.enabled = True
            self.maintx = args.maintx


    async def perform_operation(self, pool, result, network_name):
        maintx_response = await self.get_txn(pool, int(self.maintx))

        result = result + [maintx_response]
        return result

    async def get_txn(self, pool, seq_no: int):
        req = build_get_txn_request(None, LedgerType.DOMAIN, seq_no)
        return await pool.submit_request(req)