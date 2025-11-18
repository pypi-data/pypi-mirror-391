from search_api.search_api_description import PostBridgeApi
from typing import Optional
from beekeepy._apis.abc.api import AbstractAsyncApi

class Search-api(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def find_text(self, *, pattern: str, sort: str, author: Optional=None, start_author: Optional=None, start_permlink: Optional=None, limit: Optional=None, observer: Optional=None, truncate_body: Optional=None) -> list[PostBridgeApi]:
        ...