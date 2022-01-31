import plugin_collection

import json
import re
class main(plugin_collection.Plugin):
    def __init__(self):
        super().__init__()
        self.index = 4
        self.name = 'pooltx'
        self.description = ''
        self.type = ''

    def parse_args(self, parser):
        parser.add_argument("-pooltx", "--pooltx", action="store_true", help="Get pool ledger transactions.")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose

        self.enabled = args.pooltx

    async def perform_operation(self, pool, result, network_name):
        # Returns as individual json str's.
        # Join the individual json items into one item.
        # Remove the new line endings and replace them with comma's.
        # Load the newly created json file to un-encode it, to not double encode.

        pooltx_response = await self.get_pool_txns(pool)
        pooltx_response = f'[{pooltx_response}]'
        pooltx_response = re.sub('\n', ',', pooltx_response)
        pooltx_response = json.loads(pooltx_response)

        result = result + [pooltx_response]
        return result

    async def get_pool_txns(self, pool):
        pool_txns = await pool.get_transactions()
        return pool_txns