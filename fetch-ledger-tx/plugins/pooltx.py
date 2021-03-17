import plugin_collection
from indy_vdr.pool import Pool, open_pool
import json

class main(plugin_collection.Plugin):
    def __init__(self):
        super().__init__()
        self.index = 4
        self.name = 'pooltx'
        self.description = ''
        self.type = ''

    def parse_args(self, parser):
        parser.add_argument("-pooltx", "--pooltx", help="Get pool ledger transactions.")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose

        self.enabled = args.pooltx

    async def perform_operation(self, result, pool, network_name):
        pooltx_response = await self.get_pool_txns(pool)
        print(pooltx_response) # Already in Json. If you print json with json.dump causes it to double encode.
        # return pooltx_response

    async def get_pool_txns(self, pool: Pool):
        pool_txns = await pool.get_transactions()
        return pool_txns