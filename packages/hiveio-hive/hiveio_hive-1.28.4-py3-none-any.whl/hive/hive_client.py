from hive.hive_description import DbHeadStateResponse
from hive.hive_description import GetInfoResponse
from beekeepy._apis.abc.api import AbstractAsyncApi


class Hive(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def db_head_state(self) -> DbHeadStateResponse: ...

    @endpoint_jsonrpc
    async def get_info(self) -> GetInfoResponse: ...
