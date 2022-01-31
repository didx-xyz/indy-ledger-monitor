import plugin_collection

from indy_vdr.ledger import (
    build_get_cred_def_request,
)

class main(plugin_collection.Plugin):
    def __init__(self):
        super().__init__()
        self.index = 3
        self.name = 'credid'
        self.description = ''
        self.type = ''
        self.maintx = None

    def parse_args(self, parser):
        parser.add_argument("-credid", "--credid", help="Get a specific credential definition from ledger. (TxnID of CLAIM_DEF)")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose
        
        if args.credid:
            self.enabled = True
            self.credid = args.credid


    async def perform_operation(self, pool, result, network_name):
        credid_response = await self.get_cred_by_Id(pool, self.credid)

        result = result + [credid_response]
        return result

    async def get_cred_by_Id(self, pool, credId):
        req = build_get_cred_def_request(
            None, credId
        )
        return await pool.submit_request(req)