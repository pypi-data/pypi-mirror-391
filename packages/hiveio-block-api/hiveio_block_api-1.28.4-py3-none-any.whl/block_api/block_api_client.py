from block_api.block_api_description import GetBlockResponse
from block_api.block_api_description import GetBlockHeaderResponse
from block_api.block_api_description import GetBlockRangeResponse
from beekeepy._apis.abc.api import AbstractAsyncApi


class BlockApi(AbstractAsyncApi):
    endpoint_jsonrpc = AbstractAsyncApi.endpoint_jsonrpc

    @endpoint_jsonrpc
    async def get_block(self, *, block_num: int) -> GetBlockResponse:
        """Parameters:

        - `block_num`: An integer representing the block number to query.
        """

    @endpoint_jsonrpc
    async def get_block_header(self, *, block_num: int) -> GetBlockHeaderResponse:
        """Parameters:

        - `block_num`: An integer representing the block number to query.
        """

    @endpoint_jsonrpc
    async def get_block_range(self, *, starting_block_num: int, count: int) -> GetBlockRangeResponse:
        """Parameters:

        - `starting_block_num`: An integer indicating the height of the first block to be returned.

        - `count`: An integer specifying the maximum number of blocks to return.

        Examples:

        - `starting_block_num = 1`, `count = 10` — Queries the block headers for the very first block through the tenth block.

        - `starting_block_num = 8675309`, `count = 50` — Queries block headers for block numbers 8,675,309 through 8,675,359.

        - `starting_block_num = 62396745`, `count = 1000` — Queries block headers for block numbers 62,396,745 through 62,397,745.
        """
