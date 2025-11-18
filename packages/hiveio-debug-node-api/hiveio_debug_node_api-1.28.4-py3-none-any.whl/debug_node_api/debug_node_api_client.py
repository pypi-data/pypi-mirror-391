from debug_node_api.debug_node_api_description import DebugGenerateBlocksResponse
from debug_node_api.debug_node_api_description import DebugGenerateBlocksUntilResponse
from debug_node_api.debug_node_api_description import DebugGetFutureWitnessScheduleResponse
from debug_node_api.debug_node_api_description import DebugGetHardforkPropertyObjectResponse
from debug_node_api.debug_node_api_description import DebugGetJsonSchemaResponse
from debug_node_api.debug_node_api_description import DebugGetWitnessScheduleResponse
from debug_node_api.debug_node_api_description import DebugHasHardforkResponse
from debug_node_api.debug_node_api_description import DebugSetHardforkResponse
from debug_node_api.debug_node_api_description import DebugSetVestPriceResponse
from debug_node_api.debug_node_api_description import DebugThrowExceptionResponse
from typing import Optional
from debug_node_api.debug_node_api_description import VestPrice
from beekeepy._apis.abc.api import AbstractAsyncApi


class DebugNodeApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def debug_generate_blocks(
        self, *, debug_key: str, count: int, skip: int, miss_blocks: int
    ) -> DebugGenerateBlocksResponse: ...

    @endpoint_jsonrpc
    async def debug_generate_blocks_until(
        self, *, debug_key: str, head_block_time: str, generate_sparsely: bool
    ) -> DebugGenerateBlocksUntilResponse: ...

    @endpoint_jsonrpc
    async def debug_get_future_witness_schedule(self) -> DebugGetFutureWitnessScheduleResponse: ...

    @endpoint_jsonrpc
    async def debug_get_hardfork_property_object(self) -> DebugGetHardforkPropertyObjectResponse: ...

    @endpoint_jsonrpc
    async def debug_get_head_block(self): ...

    @endpoint_jsonrpc
    async def debug_get_json_schema(self) -> DebugGetJsonSchemaResponse: ...

    @endpoint_jsonrpc
    async def debug_get_witness_schedule(self) -> DebugGetWitnessScheduleResponse: ...

    @endpoint_jsonrpc
    async def debug_has_hardfork(self, *, hardfork_id: int) -> DebugHasHardforkResponse: ...

    @endpoint_jsonrpc
    async def debug_set_hardfork(
        self, *, hardfork_id: int, hook_to_tx: Optional = None
    ) -> DebugSetHardforkResponse: ...

    @endpoint_jsonrpc
    async def debug_set_vest_price(
        self, *, vest_price: VestPrice, hook_to_tx: Optional = None
    ) -> DebugSetVestPriceResponse: ...

    @endpoint_jsonrpc
    async def debug_throw_exception(self, *, throw_exception: bool) -> DebugThrowExceptionResponse: ...
