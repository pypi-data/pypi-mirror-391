"""
Hyperliquid type definitions for perpetuals trading operations.

These models match the execution-layer-SDK types for consistency.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# =====================
# Request Types (from execution-layer-SDK)
# =====================


class HyperliquidPlaceOrderRequest(BaseModel):
    """
    Request to place an order on Hyperliquid.

    Attributes:
        symbol: Trading pair symbol (e.g., "BTC-USD")
        side: Order side ("buy" or "sell")
        size: Order size (e.g., 0.0001)
        price: Order price (e.g., 110000)
        market: Market type ("perp" or "spot")
        type: Order type (optional: "market", "limit", "stop", "take_profit")
        triggerPrice: Trigger price for stop/take-profit orders (optional)
        reduceOnly: Whether this is a reduce-only order (optional)
        postOnly: Whether this is a post-only order (optional)

    Examples:
        ```python
        # Market buy order
        order = HyperliquidPlaceOrderRequest(
            symbol="BTC-USD",
            side="buy",
            size=0.0001,
            price=110000,
            market="perp",
            type="market"
        )

        # Limit buy order
        order = HyperliquidPlaceOrderRequest(
            symbol="BTC-USD",
            side="buy",
            size=0.0001,
            price=100000,
            market="perp",
            type="limit"
        )
        ```
    """

    symbol: str = Field(..., description="Trading pair symbol (e.g., 'BTC-USD')")
    side: Literal["buy", "sell"] = Field(..., description="Order side")
    size: float = Field(..., description="Order size")
    price: float = Field(..., description="Order price")
    market: Literal["perp", "spot"] = Field(..., description="Market type")
    type: Literal["market", "limit", "stop", "take_profit"] | None = Field(
        None, description="Order type"
    )
    triggerPrice: float | None = Field(
        None, description="Trigger price for stop/take-profit orders"
    )
    reduceOnly: bool | None = Field(
        None, description="Whether this is a reduce-only order"
    )
    postOnly: bool | None = Field(None, description="Whether this is a post-only order")

    model_config = ConfigDict(extra="ignore")


class HyperliquidTransferRequest(BaseModel):
    """
    Request to transfer between spot and perp accounts.

    Attributes:
        amount: Amount to transfer
        toPerp: True to transfer to perp account, False to transfer to spot

    Examples:
        ```python
        # Transfer to perp account
        transfer = HyperliquidTransferRequest(amount=1000.0, toPerp=True)
        ```
    """

    amount: float = Field(..., description="Amount to transfer")
    toPerp: bool = Field(
        ..., description="True to transfer to perp, False to transfer to spot"
    )

    model_config = ConfigDict(extra="ignore")


# =====================
# Response Data Types (from execution-layer-SDK)
# =====================


class HyperliquidOrderInfo(BaseModel):
    """Order information."""

    orderId: str = Field(..., description="Order ID")
    symbol: str = Field(..., description="Trading pair symbol")
    side: Literal["buy", "sell"] = Field(..., description="Order side")
    price: float = Field(..., description="Order price")
    size: float = Field(..., description="Order size")
    filled: float = Field(..., description="Filled amount")
    status: str = Field(..., description="Order status")
    market: Literal["perp", "spot"] = Field(..., description="Market type")
    clientOrderId: str | None = Field(None, description="Client order ID")

    model_config = ConfigDict(extra="allow")


class HyperliquidPerpBalance(BaseModel):
    """Perp account balance information."""

    accountValue: str = Field(..., description="Account value")
    totalMarginUsed: str = Field(..., description="Total margin used")
    withdrawable: str = Field(..., description="Withdrawable amount")

    model_config = ConfigDict(extra="allow")


class HyperliquidSpotBalance(BaseModel):
    """Spot token balance."""

    coin: str = Field(..., description="Coin symbol")
    total: str = Field(..., description="Total balance")
    hold: str = Field(..., description="Amount on hold")

    model_config = ConfigDict(extra="allow")


class HyperliquidBalances(BaseModel):
    """Combined balance information."""

    perp: HyperliquidPerpBalance = Field(..., description="Perp account balance")
    spot: list[HyperliquidSpotBalance] = Field(..., description="Spot balances")

    model_config = ConfigDict(extra="allow")


class HyperliquidPosition(BaseModel):
    """Position information."""

    symbol: str = Field(..., description="Position symbol")
    side: Literal["long", "short"] = Field(..., description="Position side")
    size: str = Field(..., description="Position size")
    entryPrice: str = Field(..., description="Entry price")
    markPrice: str = Field(..., description="Mark price")
    liquidationPrice: str | None = Field(None, description="Liquidation price")
    unrealizedPnl: str = Field(..., description="Unrealized PnL")
    leverage: str = Field(..., description="Leverage")
    marginUsed: str = Field(..., description="Margin used")

    model_config = ConfigDict(extra="allow")


class HyperliquidFill(BaseModel):
    """Fill/trade information from order history."""

    orderId: str = Field(..., description="Order ID")
    symbol: str = Field(..., description="Trading pair symbol")
    side: Literal["buy", "sell"] = Field(..., description="Fill side")
    price: str = Field(..., description="Fill price")
    size: str = Field(..., description="Fill size")
    fee: str = Field(..., description="Fee paid")
    timestamp: int = Field(..., description="Fill timestamp")
    isMaker: bool = Field(..., description="Whether this was a maker fill")

    model_config = ConfigDict(extra="allow")


class HyperliquidHistoricalOrder(BaseModel):
    """Detailed historical order information with status."""

    orderId: str = Field(..., description="Order ID")
    symbol: str = Field(..., description="Trading pair symbol")
    side: Literal["buy", "sell"] = Field(..., description="Order side")
    price: float = Field(..., description="Order price")
    size: float = Field(..., description="Order size")
    filled: float = Field(..., description="Filled amount")
    status: Literal[
        "open",
        "filled",
        "canceled",
        "triggered",
        "rejected",
        "marginCanceled",
        "liquidatedCanceled",
    ] = Field(..., description="Order status")
    market: Literal["perp", "spot"] = Field(..., description="Market type")
    timestamp: int = Field(..., description="Order creation timestamp")
    statusTimestamp: int = Field(..., description="Status update timestamp")
    orderType: Literal[
        "Market",
        "Limit",
        "Stop Market",
        "Stop Limit",
        "Take Profit Market",
        "Take Profit Limit",
    ] = Field(..., description="Order type")
    clientOrderId: str | None = Field(None, description="Client order ID")

    model_config = ConfigDict(extra="allow")


class HyperliquidLiquidatedPosition(BaseModel):
    """Individual liquidated position."""

    symbol: str = Field(..., description="Position symbol")
    side: Literal["long", "short"] = Field(..., description="Position side")
    size: str = Field(..., description="Position size")

    model_config = ConfigDict(extra="allow")


class HyperliquidLiquidation(BaseModel):
    """Liquidation event information."""

    timestamp: int = Field(..., description="Liquidation timestamp")
    liquidatedPositions: list[HyperliquidLiquidatedPosition] = Field(
        ..., description="Liquidated positions"
    )
    totalNotional: str = Field(..., description="Total notional value")
    accountValue: str = Field(..., description="Account value at liquidation")
    leverageType: Literal["Cross", "Isolated"] = Field(..., description="Leverage type")
    txHash: str = Field(..., description="Transaction hash")

    model_config = ConfigDict(extra="allow")


# =====================
# SDK Response Wrappers
# =====================


class HyperliquidSDKResponse(BaseModel):
    """Base response wrapper for all Hyperliquid operations."""

    success: bool = Field(..., description="Whether the operation succeeded")
    error: str | None = Field(None, description="Error message if operation failed")

    model_config = ConfigDict(extra="allow")


class HyperliquidPlaceOrderResponse(HyperliquidSDKResponse):
    """Hyperliquid place order response wrapper."""

    data: HyperliquidOrderInfo | None = Field(None, description="Order info")


class HyperliquidOrderResponse(HyperliquidSDKResponse):
    """Hyperliquid order response wrapper."""

    data: HyperliquidOrderInfo | None = Field(None, description="Order info")


class HyperliquidDeleteOrderResponse(HyperliquidSDKResponse):
    """
    Hyperliquid delete order response wrapper.

    Note: This is a void response - data is always None on success.
    """

    data: dict[str, Any] | None = Field(None, description="Always None (void response)")


class HyperliquidBalancesResponse(HyperliquidSDKResponse):
    """Hyperliquid balances response wrapper."""

    data: HyperliquidBalances | None = Field(None, description="Balances data")


class HyperliquidPositionsResponse(HyperliquidSDKResponse):
    """Hyperliquid positions response wrapper."""

    data: list[HyperliquidPosition] | None = Field(None, description="Positions data")


class HyperliquidOpenOrdersResponse(HyperliquidSDKResponse):
    """Hyperliquid open orders response wrapper."""

    data: list[HyperliquidOrderInfo] | None = Field(
        None, description="Open orders data"
    )


class HyperliquidOrderFillsResponse(HyperliquidSDKResponse):
    """Hyperliquid order fills response wrapper."""

    data: list[HyperliquidFill] | None = Field(None, description="Order fills data")


class HyperliquidHistoricalOrdersResponse(HyperliquidSDKResponse):
    """Hyperliquid historical orders response wrapper."""

    data: list[HyperliquidHistoricalOrder] | None = Field(
        None, description="Historical orders data"
    )


class HyperliquidTransferResponse(HyperliquidSDKResponse):
    """
    Hyperliquid transfer response wrapper.

    Note: This is a void response - data is always None on success.
    """

    data: dict[str, Any] | None = Field(None, description="Always None (void response)")


class HyperliquidLiquidationsResponse(HyperliquidSDKResponse):
    """Hyperliquid liquidations response wrapper."""

    data: list[HyperliquidLiquidation] | None = Field(
        None, description="Liquidations data"
    )
