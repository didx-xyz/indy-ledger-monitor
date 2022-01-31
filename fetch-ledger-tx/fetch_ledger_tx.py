from util import log
from plugin_collection import PluginCollection
from DidKey import DidKey
from pool import PoolCollection
from singleton import Singleton

class FetchLedgerTX(object, metaclass=Singleton):
    def __init__(self, verbose, pool_collection: PoolCollection):
        self.verbose = verbose
        self.pool_collection = pool_collection

    async def fetch(self, network_id: str, monitor_plugins: PluginCollection, ident: DidKey = None):
        result = []

        pool, network_name = await self.pool_collection.get_pool(network_id)

        log("Passing results to plugins for processing ...")
        result = await monitor_plugins.apply_all_plugins_on_value(pool, result, network_name)
        log("Processing complete.")
        return result