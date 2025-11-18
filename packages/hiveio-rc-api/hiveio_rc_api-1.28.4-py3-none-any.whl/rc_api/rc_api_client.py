from rc_api.rc_api_description import FindRcAccountsResponse
from rc_api.rc_api_description import GetRcOperationStatsResponse
from rc_api.rc_api_description import GetRcStatsResponse
from rc_api.rc_api_description import GetResourceParamsResponse
from rc_api.rc_api_description import GetResourcePoolResponse
from rc_api.rc_api_description import ListRcAccountsResponse
from rc_api.rc_api_description import ListRcDirectDelegationsResponse
from typing import Optional
from beekeepy._apis.abc.api import AbstractAsyncApi


class RcApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def find_rc_accounts(self, *, accounts: list) -> FindRcAccountsResponse:
        """Parameters:

        - `accounts`: An array of strings representing account names to query. Examples:
          - `["hiveio"]` — queries the available resource credits for the account named "hiveio".
          - `["alice","bob"]` — queries the resource credits for the account named "alice" and "bob".
        """

    @endpoint_jsonrpc
    async def get_rc_operation_stats(self, *, operation: str) -> GetRcOperationStatsResponse: ...

    @endpoint_jsonrpc
    async def get_rc_stats(self) -> GetRcStatsResponse: ...

    @endpoint_jsonrpc
    async def get_resource_params(self) -> GetResourceParamsResponse: ...

    @endpoint_jsonrpc
    async def get_resource_pool(self) -> GetResourcePoolResponse: ...

    @endpoint_jsonrpc
    async def list_rc_accounts(self, *, limit: int, start: Optional = None) -> ListRcAccountsResponse: ...

    @endpoint_jsonrpc
    async def list_rc_direct_delegations(self, *, start: list, limit: int) -> ListRcDirectDelegationsResponse: ...
