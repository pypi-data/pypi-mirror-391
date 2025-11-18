from network_broadcast_api.network_broadcast_api_description import BroadcastTransactionResponse
from network_broadcast_api.network_broadcast_api_description import Trx
from beekeepy._apis.abc.api import AbstractAsyncApi


class NetworkBroadcastApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def broadcast_transaction(self, *, trx: Trx, max_block_age: int) -> BroadcastTransactionResponse: ...
