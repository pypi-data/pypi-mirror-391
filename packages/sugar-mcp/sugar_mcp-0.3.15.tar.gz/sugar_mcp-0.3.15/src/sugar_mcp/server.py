import os

from mcp.server.fastmcp import FastMCP
from netmind_sugar.chains import get_chain, Token, Price, LiquidityPool, Quote, LiquidityPoolForSwap
from netmind_sugar.pool import Amount, LiquidityPoolEpoch
from pydantic import Field, BaseModel
from web3 import Web3

from typing import Optional, List, Tuple


mcp = FastMCP("sugar-mcp")


class TokenInfo(BaseModel):
    chain_id: str = Field(..., description="Chain ID, e.g., '10' for OPChain, '8453' for BaseChain")
    chain_name: str = Field(..., description="Chain name, e.g., 'OPChain', 'BaseChain'")
    token_address: str = Field(..., description="Token contract address")
    symbol: str = Field(..., description="Token symbol, e.g., 'USDC', 'VELO'")
    decimals: int = Field(..., description="Number of decimals for the token")
    listed: bool = Field(..., description="Whether the token is listed")
    wrapped_token_address: str = Field(default="", description="Wrapped token address")

    @staticmethod
    def from_token(t: Token):
        return TokenInfo(
            chain_id=t.chain_id,
            chain_name=t.chain_name,
            token_address=t.token_address,
            symbol=t.symbol,
            decimals=t.decimals,
            listed=t.listed,
            wrapped_token_address=t.wrapped_token_address if t.wrapped_token_address else "",
        )

class PriceInfo(BaseModel):
    token: TokenInfo = Field(..., description="Token information")
    price: float = Field(..., description="Price in stable token")

    @staticmethod
    def from_price(p: Price):
        token_info = TokenInfo.from_token(p.token)
        return PriceInfo(token=token_info, price=p.price)

class AmountInfo(BaseModel):
    token: TokenInfo = Field(..., description="Token information")
    amount: int = Field(..., description="Amount in wei")
    price: PriceInfo = Field(..., description="Price information")

    @staticmethod
    def from_amount(a: Amount):
        price_info = PriceInfo.from_price(a.price)
        return AmountInfo(token=TokenInfo.from_token(a.token), amount=a.amount, price=price_info)

class LiquidityPoolInfo(BaseModel):
    chain_id: str = Field(..., description="Chain ID")
    chain_name: str = Field(..., description="Chain name")
    lp: str = Field(..., description="Liquidity pool address")
    factory: str = Field(..., description="Factory address")
    symbol: str = Field(..., description="Token symbol")
    type: int = Field(..., description="Pool type")
    is_stable: bool = Field(..., description="Whether the pool is stable")
    is_cl: bool = Field(..., description="Whether the pool is concentrated liquidity")
    total_supply: float = Field(..., description="Total supply of the pool")
    decimals: int = Field(..., description="Number of decimals for the pool")
    token0: TokenInfo = Field(..., description="Token0 information")
    reserve0: AmountInfo = Field(..., description="Token0 reserve amount")
    token1: TokenInfo = Field(..., description="Token1 information")
    reserve1: AmountInfo = Field(..., description="Token1 reserve amount")
    token0_fees: AmountInfo = Field(..., description="Token0 fees")
    token1_fees: AmountInfo = Field(..., description="Token1 fees")
    pool_fee: float = Field(..., description="Pool fee")
    gauge_total_supply: float = Field(..., description="Gauge total supply")
    emissions: Optional[AmountInfo] = Field(..., description="Emissions information")
    emissions_token: Optional[TokenInfo] = Field(..., description="Emissions token information")
    weekly_emissions: Optional[AmountInfo] = Field(..., description="Weekly emissions information")
    nfpm: str = Field(..., description="NFPM information")
    alm: str = Field(..., description="ALM information")

    @staticmethod
    def from_pool(p: LiquidityPool):
        return LiquidityPoolInfo(
            chain_id=p.chain_id,
            chain_name=p.chain_name,
            lp=p.lp,
            factory=p.factory,
            symbol=p.symbol,
            type=p.type,
            is_stable=p.is_stable,
            is_cl=p.is_cl,
            total_supply=p.total_supply,
            decimals=p.decimals,
            token0=TokenInfo.from_token(p.token0),
            reserve0=AmountInfo.from_amount(p.reserve0) if p.reserve0 else None,
            token1=TokenInfo.from_token(p.token1),
            reserve1=AmountInfo.from_amount(p.reserve1) if p.reserve1 else None,
            token0_fees=AmountInfo.from_amount(p.token0_fees) if p.token0_fees else None,
            token1_fees=AmountInfo.from_amount(p.token1_fees) if p.token1_fees else None,
            pool_fee=p.pool_fee,
            gauge_total_supply=p.gauge_total_supply,
            emissions=AmountInfo.from_amount(p.emissions) if p.emissions else None,
            emissions_token=TokenInfo.from_token(p.emissions_token) if p.emissions_token else None,
            weekly_emissions=AmountInfo.from_amount(p.weekly_emissions) if p.weekly_emissions else None,
            nfpm=p.nfpm,
            alm=p.alm
        )

class LiquidityPoolForSwapInfo(BaseModel):
    chain_id: str = Field(..., description="Chain ID")
    chain_name: str = Field(..., description="Chain name")
    lp: str = Field(..., description="Liquidity pool address")
    type: int = Field(..., description="Pool type")
    token0_address: str = Field(..., description="Token0 address")
    token1_address: str = Field(..., description="Token1 address")

    @staticmethod
    def from_pool(p: LiquidityPoolForSwap):
        return LiquidityPoolForSwapInfo(
            chain_id=p.chain_id,
            chain_name=p.chain_name,
            lp=p.lp,
            type=p.type,
            token0_address=p.token0_address,
            token1_address=p.token1_address
        )

class LiquidityPoolEpochInfo(BaseModel):
    ts: int = Field(..., description="Timestamp of the epoch")
    lp: str = Field(..., description="Liquidity pool address")
    pool: LiquidityPoolInfo = Field(..., description="Liquidity pool information")
    votes: int = Field(..., description="Number of votes")
    emissions: int = Field(..., description="Emissions amount")
    incentives: List[AmountInfo] = Field(..., description="List of incentives amounts")
    fees: List[AmountInfo] = Field(..., description="List of fees amounts")

    @staticmethod
    def from_epoch(e: LiquidityPoolEpoch):
        return LiquidityPoolEpochInfo(
            ts=e.ts,
            lp=e.lp,
            pool=LiquidityPoolInfo.from_pool(e.pool),
            votes=e.votes,
            emissions=e.emissions,
            incentives=[AmountInfo.from_amount(i) for i in e.incentives],
            fees=[AmountInfo.from_amount(f) for f in e.fees]
        )

class QuoteInputInfo(BaseModel):
    from_token: TokenInfo = Field(..., description="From token information")
    to_token: TokenInfo = Field(..., description="To token information")
    path: List[Tuple[LiquidityPoolForSwapInfo, bool]] = Field(..., description="Swap path as list of (pool, reversed) tuples")
    amount_in: int = Field(..., description="Input amount in wei")

    @staticmethod
    def from_quote_input(q: Quote):
        return QuoteInputInfo(
            from_token=TokenInfo.from_token(q.input.from_token),
            to_token=TokenInfo.from_token(q.input.to_token),
            path=[(LiquidityPoolForSwapInfo.from_pool(p), rev) for p, rev in q.input.path],
            amount_in=q.input.amount_in
        )

class QuoteInfo(BaseModel):
    input: QuoteInputInfo = Field(..., description="Quote input information")
    amount_out: int = Field(..., description="Output amount in wei")

    @staticmethod
    def from_quote(q: Quote):
        return QuoteInfo(
            input=QuoteInputInfo.from_quote_input(q),
            amount_out=q.amount_out
        )

@mcp.tool()
async def get_all_tokens(
    limit: int, offset: int, chainId: str = "10"
) -> List[TokenInfo]:
    """
    Retrieve all tokens supported by the protocol.

    Args:
        limit (int): Maximum number of tokens to return.
        offset (int): The starting point to retrieve tokens.
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[Token]: A list of Token objects.
    """
    with get_chain(chainId) as chain:
        tokens = chain.get_tokens_page(limit, offset)
        tokens = list(
            map(
                lambda t: TokenInfo.from_token(
                    Token.from_tuple(t, chain_id=chain.chain_id, chain_name=chain.name)
                ),
                tokens,
            )
        )

        return tokens


@mcp.tool()
async def get_token_prices(token_address: str, chainId: str = "10") -> List[PriceInfo]:
    """
    Retrieve prices for a specific token in terms of the stable token.

    Args:
        token_address (str): The address of the token to retrieve prices for.
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[Price]: A list of Price objects with token-price mappings.
    """
    token_address = Web3.to_checksum_address(token_address)
    with get_chain(chainId) as chain:
        append_stable = False
        append_native = False

        tokens = [chain.get_token(token_address)]
        if chain.settings.stable_token_addr.lower() != token_address.lower():
            tokens.append(chain.get_token(chain.settings.stable_token_addr))
            append_stable = True

        if chain.settings.native_token_symbol.lower() != token_address.lower():
            tokens.append(
                Token.make_native_token(
                    chain.settings.native_token_symbol,
                    chain.settings.wrapped_native_token_addr,
                    chain.settings.native_token_decimals,
                    chain_id=chain.chain_id,
                    chain_name=chain.name,
                )
            )
            append_native = True

        prices = chain.get_prices(tokens)
        prices = [PriceInfo.from_price(p) for p in prices]
        if append_stable:
            # 如果在获取价格的时候加上了稳定币，在返回结果的时候再从列表里去掉，否则外部应用在传offset的时候会有问题
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.stable_token_addr.lower()
            ]

        if append_native:
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.native_token_symbol.lower()
            ]
        return prices


@mcp.tool()
async def get_prices(
    limit: int, offset: int, listed_only: bool = False, chainId: str = "10"
) -> List[PriceInfo]:
    """
    Retrieve prices for a list of tokens in terms of the stable token.

    Args:
        limit (int): Maximum number of prices to return.
        offset (int): The starting point to retrieve prices.
        listed_only (bool): If True, only return prices for tokens that are marked as 'listed'.
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[Price]: A list of Price objects with token-price mappings.
    """
    with get_chain(chainId) as chain:
        tokens = chain.get_tokens_page(limit, offset)
        tokens = list(
            map(
                lambda t: Token.from_tuple(
                    t, chain_id=chain.chain_id, chain_name=chain.name
                ),
                tokens,
            )
        )

        append_stable = False
        append_native = False

        # 因为get price里需要用到稳定币的价格来计算usd的汇率，这里给tokens里加上一个稳定币
        token_address_list = [t.token_address.lower() for t in tokens]
        if chain.settings.stable_token_addr.lower() not in token_address_list:
            tokens.append(chain.get_token(chain.settings.stable_token_addr))
            append_stable = True

        if chain.settings.native_token_symbol.lower() not in token_address_list:
            tokens.append(
                Token.make_native_token(
                    chain.settings.native_token_symbol,
                    chain.settings.wrapped_native_token_addr,
                    chain.settings.native_token_decimals,
                    chain_id=chain.chain_id,
                    chain_name=chain.name,
                )
            )
            append_native = True

        prices = chain.get_prices(tokens)
        prices = [PriceInfo.from_price(p) for p in prices]
        if append_stable:
            # 如果在获取价格的时候加上了稳定币，在返回结果的时候再从列表里去掉，否则外部应用在传offset的时候会有问题
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.stable_token_addr.lower()
            ]

        if append_native:
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.native_token_symbol.lower()
            ]

        return prices


@mcp.tool()
async def get_pools(limit: int = 30, offset: int = 0, chainId: str = "10") -> List[LiquidityPoolInfo]:
    """
    Retrieve all raw liquidity pools.

    Args:
        limit (int): The maximum number of pools to retrieve.
        offset (int): The starting point for pagination.
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPool] or List[LiquidityPoolForSwap]: A list of pool objects.
    """
    with get_chain(chainId) as chain:
        pools = chain.get_pools_page(limit, offset)
        return [LiquidityPoolInfo.from_pool(p) for p in pools]


@mcp.tool()
async def get_pool_by_address(address: str, chainId: str = "10") -> LiquidityPoolInfo | None:
    """
    Retrieve a raw liquidity pool by its contract address.

    Args:
        address (str): The address of the liquidity pool contract.
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        Optional[LiquidityPool]: The matching LiquidityPool object, or None if not found.
    """
    address = Web3.to_checksum_address(address)
    with get_chain(chainId) as chain:
        pool = chain.get_pool_by_address(address)
        return LiquidityPoolInfo.from_pool(pool)


@mcp.tool()
async def get_pools_for_swaps(limit: int, offset: int, chainId: str = "10") -> List[LiquidityPoolForSwapInfo]:
    """
    Retrieve all raw liquidity pools suitable for swaps.

    Args:
        limit (int): The maximum number of pools to retrieve.
        offset (int): The starting point for pagination.
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolForSwap]: A list of simplified pool objects for swaps.
    """
    with get_chain(chainId) as chain:
        pools = chain.get_pools_page(limit, offset, for_swaps=True)
        return [LiquidityPoolForSwapInfo.from_pool(p) for p in pools]


@mcp.tool()
async def get_latest_pool_epochs(offset: int, limit: int = 10, chainId: str = "10") -> List[LiquidityPoolEpochInfo]:
    """
    Retrieve the latest epoch data for all pools.

    Args:
        limit (int): The maximum number of epochs to retrieve.
        offset (int): The starting point for pagination.
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolEpoch]: A list of the most recent epochs across all pools.
    """
    with get_chain(chainId) as chain:
        epochs = chain.get_latest_pool_epochs_page(limit, offset)
        return [LiquidityPoolEpochInfo.from_epoch(p) for p in epochs]


@mcp.tool()
async def get_pool_epochs(
    lp: str, offset: int = 0, limit: int = 10, chainId: str = "10"
) -> List[LiquidityPoolEpochInfo]:
    """
    Retrieve historical epoch data for a given liquidity pool.

    Args:
        lp (str): Address of the liquidity pool.
        offset (int): Offset for pagination.
        limit (int): Number of epochs to retrieve.
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolEpoch]: A list of epoch entries for the specified pool.
    """
    lp = Web3.to_checksum_address(lp)
    with get_chain(chainId) as chain:
        epochs = chain.get_pool_epochs_page(lp, offset, limit)
        return [LiquidityPoolEpochInfo.from_epoch(p) for p in epochs]


@mcp.tool()
async def get_quote(
    from_token: str,
    to_token: str,
    amount: int,
    chainId: str = "10",
) -> Optional[QuoteInfo]:
    """
    Retrieve the best quote for swapping a given amount from one token to another.

    Args:
        from_token (str): The token to swap from. For OPchain, this can be 'usdc', 'velo', 'eth', or 'o_usdt'. For BaseChain, this can be 'usdc', 'aero', or 'eth'. For Unichain, this can be 'o_usdt' or 'usdc'. For Lisk, this can be 'o_usdt', 'lsk', 'eth', or 'usdt'.
        to_token (str): The token to swap to. For OPchain, this can be 'usdc', 'velo', 'eth', or 'o_usdt'. For BaseChain, this can be 'usdc', 'aero', or 'eth'. For Unichain, this can be 'o_usdt' or 'usdc'. For Lisk, this can be 'o_usdt', 'lsk', 'eth', or 'usdt'.
        amount (int): The amount to swap (in int, not uint256).
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        filter_quotes (Callable[[Quote], bool], optional): Optional filter to apply on the quotes.

    Returns:
        Optional[Quote]: The best available quote, or None if no valid quote was found.
    """

    if chainId == "10" and (from_token not in ["usdc", "velo", "eth", "o_usdt"] or to_token not in ["usdc", "velo", "eth", "o_usdt"]):
        raise ValueError("Only 'usdc', 'velo', 'eth', and 'o_usdt' are supported on OPChain.")

    if chainId == "130" and (from_token not in ["o_usdt", "usdc"] or to_token not in ["o_usdt", "usdc"]):
        raise ValueError("Only 'o_usdt' and 'usdc' are supported on Unichain.")

    if chainId == "1135" and (from_token not in ["o_usdt", "lsk", "eth", "usdt"] or to_token not in ["o_usdt", "lsk", "eth", "usdt"]):
        raise ValueError("Only 'o_usdt', 'lsk', 'eth', and 'usdt' are supported on List.")

    if chainId == "8453" and (from_token not in ["usdc", "aero", "eth"] or to_token not in ["usdc", "aero", "eth"]):
        raise ValueError("Only 'usdc', 'aero', and 'eth' are supported on BaseChain.")

    with get_chain(chainId) as chain:
        from_token = getattr(chain, from_token, None)
        to_token = getattr(chain, to_token, None)
        if from_token is None or to_token is None:
            raise ValueError("Invalid token specified.")

        quote = chain.get_quote(from_token, to_token, amount)
        return QuoteInfo.from_quote(quote) if quote else None


@mcp.tool()
async def swap(
    from_token: str,
    to_token: str,
    amount: int,
    slippage: Optional[float] = None,
    chainId: str = "10",
) -> str:
    """
    Execute a token swap transaction.

    Args:
        from_token (str): The token being sold. For OPchain, this can be 'usdc', 'velo', 'eth', or 'o_usdt'. For BaseChain, this can be 'usdc', 'aero', or 'eth'. For Unichain, this can be 'o_usdt' or 'usdc'. For Lisk, this can be 'o_usdt', 'lsk', 'eth', or 'usdt'.
        to_token (str): The token being bought. For OPchain, this can be 'usdc', 'velo', 'eth', or 'o_usdt'. For BaseChain, this can be 'usdc', 'aero', or 'eth'. For Unichain, this can be 'o_usdt' or 'usdc'. For Lisk, this can be 'o_usdt', 'lsk', 'eth', or 'usdt'.
        amount (int): The amount of `from_token` to swap.
        slippage (float, optional): Maximum acceptable slippage (default uses config value).
        chainId (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        TransactionReceipt: The transaction receipt from the swap execution.
    """

    if chainId == "10" and (
        from_token not in ["usdc", "velo", "eth", "o_usdt"]
        or to_token not in ["usdc", "velo", "eth", "o_usdt"]
    ):
        raise ValueError(
            "Only 'usdc', 'velo', 'eth', and 'o_usdt' are supported on OPChain."
        )

    if chainId == "130" and (
        from_token not in ["o_usdt", "usdc"] or to_token not in ["o_usdt", "usdc"]
    ):
        raise ValueError("Only 'o_usdt' and 'usdc' are supported on Unichain.")

    if chainId == "1135" and (
        from_token not in ["o_usdt", "lsk", "eth", "usdt"]
        or to_token not in ["o_usdt", "lsk", "eth", "usdt"]
    ):
        raise ValueError(
            "Only 'o_usdt', 'lsk', 'eth', and 'usdt' are supported on List."
        )

    if chainId == "8453" and (
        from_token not in ["usdc", "aero", "eth"]
        or to_token not in ["usdc", "aero", "eth"]
    ):
        raise ValueError("Only 'usdc', 'aero', and 'eth' are supported on BaseChain.")

    with get_chain(chainId) as chain:
        from_token = getattr(chain, from_token, None)
        to_token = getattr(chain, to_token, None)
        if from_token is None or to_token is None:
            raise ValueError("Invalid token specified. Use 'usdc', 'velo', or 'eth'.")

        tx_hash = chain.swap(from_token, to_token, amount, slippage)
        return tx_hash


def main():
    if not os.environ.get("SUGAR_PK"):
        raise ValueError(
            "Environment variable SUGAR_PK is not set. Please set it to your private key."
        )
    print("Starting Sugar MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
