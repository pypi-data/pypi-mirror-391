from reputation_api.reputation_api_description import GetAccountReputationsResponse
from beekeepy._apis.abc.api import AbstractAsyncApi


class ReputationApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def get_account_reputations(
        self, *, account_lower_bound: str, limit: int
    ) -> GetAccountReputationsResponse: ...
