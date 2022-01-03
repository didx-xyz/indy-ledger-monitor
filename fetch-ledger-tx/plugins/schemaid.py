import plugin_collection
from indy_vdr.ledger import build_get_schema_request

class main(plugin_collection.Plugin):
    def __init__(self):
        super().__init__()
        self.index = 2
        self.name = 'Schemaid'
        self.description = ''
        self.type = ''
        self.schemaid = None

    def parse_args(self, parser):
        parser.add_argument("-schemaid", "--schemaid", help="Get a specific schema from ledger. (TxnID of SCHEMA)")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose

        self.enabled = bool(args.schemaid)
        self.schemaid = args.schemaid

    async def perform_operation(self, pool, result, network_name):
        # "QXdMLmAKZmQBhnvXHxKn78:2:SURFNetSchema:1.0"
        response = await self.get_schema_by_Id(pool, self.schemaid)

        result = result + [response]
        return result

    async def get_schema_by_Id(self, pool, schemaid):
        req = build_get_schema_request(
            None, schemaid
        )
        return await pool.submit_request(req)