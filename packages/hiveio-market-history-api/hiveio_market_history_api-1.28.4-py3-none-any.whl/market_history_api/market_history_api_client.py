from market_history_api.market_history_api_description import GetMarketHistoryResponse
from market_history_api.market_history_api_description import GetMarketHistoryBucketsResponse
from market_history_api.market_history_api_description import MarketHistoryGetOrderBookResponse
from market_history_api.market_history_api_description import GetRecentTradesResponse
from market_history_api.market_history_api_description import GetTickerResponse
from market_history_api.market_history_api_description import GetTradeHistoryResponse
from market_history_api.market_history_api_description import GetVolumeResponse
from typing import Optional
from beekeepy._apis.abc.api import AbstractAsyncApi


class MarketHistoryApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def get_market_history(self, *, bucket_seconds: int, start: str, end: str) -> GetMarketHistoryResponse: ...

    @endpoint_jsonrpc
    async def get_market_history_buckets(self) -> GetMarketHistoryBucketsResponse: ...

    @endpoint_jsonrpc
    async def get_order_book(self, *, limit: Optional = None) -> MarketHistoryGetOrderBookResponse: ...

    @endpoint_jsonrpc
    async def get_recent_trades(self, *, limit: Optional = None) -> GetRecentTradesResponse: ...

    @endpoint_jsonrpc
    async def get_ticker(self) -> GetTickerResponse: ...

    @endpoint_jsonrpc
    async def get_trade_history(self, *, start: str, end: str, limit: Optional = None) -> GetTradeHistoryResponse: ...

    @endpoint_jsonrpc
    async def get_volume(self) -> GetVolumeResponse: ...
