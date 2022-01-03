import plugin_collection

from indy_vdr.ledger import (
    build_get_nym_request,
)

class main(plugin_collection.Plugin):
    def __init__(self):
        super().__init__()
        self.index = 3
        self.name = 'nym'
        self.description = ''
        self.type = ''
        self.maintx = None

    def parse_args(self, parser):
        parser.add_argument("-nym", "--nym", help="Get a specific NYM from ledger. (Target DID/dest of NYM)")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose
        
        if args.nym:
            self.enabled = True
            self.nym = args.nym


    async def perform_operation(self, pool, result, network_name):
        #TODO Add additional query parameters
        nym_response = await self.getNYM(pool, self.nym)

        result = result + [nym_response]
        return result

    #TODO Add submitted_did as parameter
    async def getNYM(self, pool, nym):
        req = build_get_nym_request(None, nym)
        return await pool.submit_request(req)