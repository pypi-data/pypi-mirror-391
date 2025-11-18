"""
Centralized type exports for the Python Agent SDK

This module provides all the type definitions used throughout the SDK,
including network types, request/response models, and utility types.
"""

# Network types and utilities
# Configuration types
from .config import SDKConfig

# Hyperliquid types
from .hyperliquid import (
    HyperliquidBalances,
    HyperliquidBalancesResponse,
    HyperliquidDeleteOrderResponse,
    HyperliquidFill,
    HyperliquidHistoricalOrder,
    HyperliquidHistoricalOrdersResponse,
    HyperliquidLiquidatedPosition,
    HyperliquidLiquidation,
    HyperliquidLiquidationsResponse,
    HyperliquidOpenOrdersResponse,
    HyperliquidOrderFillsResponse,
    HyperliquidOrderInfo,
    HyperliquidOrderResponse,
    HyperliquidPerpBalance,
    HyperliquidPlaceOrderRequest,
    HyperliquidPlaceOrderResponse,
    HyperliquidPosition,
    HyperliquidPositionsResponse,
    HyperliquidSDKResponse,
    HyperliquidSpotBalance,
    HyperliquidTransferRequest,
    HyperliquidTransferResponse,
)

# Memory types
from .memory import (
    MemoryDeleteData,
    MemoryDeleteRequest,
    MemoryDeleteResponse,
    MemoryGetData,
    MemoryGetRequest,
    MemoryGetResponse,
    MemoryListData,
    MemoryListRequest,
    MemoryListResponse,
    MemorySDKResponse,
    MemorySetData,
    MemorySetRequest,
    MemorySetResponse,
)
from .networks import (
    Network,
    get_chain_id_from_network,
    is_ethereum_network,
    is_solana_network,
)

# Polymarket types
from .polymarket import (
    PolymarketEip712Domain,
    PolymarketEip712Message,
    PolymarketEip712Type,
    PolymarketMarketOrderData,
    PolymarketMarketOrderRequest,
    PolymarketMarketOrderResponse,
    PolymarketOrder,
    PolymarketOrderData,
    PolymarketOrderInfo,
    PolymarketPosition,
    PolymarketPositionsData,
    PolymarketPositionsResponse,
    PolymarketRedeemPositionResult,
    PolymarketRedeemPositionsData,
    PolymarketRedeemPositionsRequest,
    PolymarketRedeemPositionsResponse,
    PolymarketSDKResponse,
    PolymarketSubmitOrderResult,
)

# Request types
from .requests import (
    AddLogRequest,
    EthereumSignRequest,
    EvmMessageSignRequest,
    SignAndSendRequest,
    SolanaSignRequest,
    SwidgeQuoteRequest,
    UpdateJobStatusRequest,
)

# Response types
from .responses import (
    EvmMessageSignData,
    EvmMessageSignResponse,
    LogResponse,
    SignAndSendData,
    SignAndSendResponse,
    SwidgeExecuteResponse,
    SwidgeQuoteResponse,
    UpdateJobStatusResponse,
)
from .swidge import (
    QUOTE_RESULT,
    SwidgeData,
    SwidgeEvmTransactionDetails,
    SwidgeExecuteResponseData,
    SwidgeFee,
    SwidgePriceImpact,
    SwidgeQuoteAsset,
    SwidgeStatusInfo,
    SwidgeTransactionStep,
    SwidgeUnsignedStep,
    SwidgeWallet,
)

__all__ = [
    # Network types
    "Network",
    "is_ethereum_network",
    "is_solana_network",
    "get_chain_id_from_network",
    # Memory types
    "MemorySetRequest",
    "MemoryGetRequest",
    "MemoryDeleteRequest",
    "MemoryListRequest",
    "MemorySetData",
    "MemoryGetData",
    "MemoryDeleteData",
    "MemoryListData",
    "MemorySDKResponse",
    "MemorySetResponse",
    "MemoryGetResponse",
    "MemoryDeleteResponse",
    "MemoryListResponse",
    # Polymarket types
    "PolymarketPosition",
    "PolymarketPositionsData",
    "PolymarketMarketOrderRequest",
    "PolymarketOrder",
    "PolymarketEip712Type",
    "PolymarketEip712Domain",
    "PolymarketEip712Message",
    "PolymarketOrderInfo",
    "PolymarketSubmitOrderResult",
    "PolymarketOrderData",
    "PolymarketMarketOrderData",
    "PolymarketRedeemPositionsRequest",
    "PolymarketRedeemPositionResult",
    "PolymarketRedeemPositionsData",
    "PolymarketSDKResponse",
    "PolymarketPositionsResponse",
    "PolymarketMarketOrderResponse",
    "PolymarketRedeemPositionsResponse",
    # Hyperliquid types
    "HyperliquidPlaceOrderRequest",
    "HyperliquidTransferRequest",
    "HyperliquidOrderInfo",
    "HyperliquidPerpBalance",
    "HyperliquidSpotBalance",
    "HyperliquidBalances",
    "HyperliquidPosition",
    "HyperliquidFill",
    "HyperliquidHistoricalOrder",
    "HyperliquidLiquidatedPosition",
    "HyperliquidLiquidation",
    "HyperliquidSDKResponse",
    "HyperliquidPlaceOrderResponse",
    "HyperliquidOrderResponse",
    "HyperliquidDeleteOrderResponse",
    "HyperliquidBalancesResponse",
    "HyperliquidPositionsResponse",
    "HyperliquidOpenOrdersResponse",
    "HyperliquidOrderFillsResponse",
    "HyperliquidHistoricalOrdersResponse",
    "HyperliquidTransferResponse",
    "HyperliquidLiquidationsResponse",
    # Swidge types
    "SwidgeWallet",
    "SwidgeData",
    "SwidgeExecuteResponseData",
    "SwidgeUnsignedStep",
    "SwidgeEvmTransactionDetails",
    "SwidgeFee",
    "SwidgePriceImpact",
    "SwidgeQuoteAsset",
    "SwidgeStatusInfo",
    "SwidgeTransactionStep",
    "QUOTE_RESULT",
    # Request types
    "SignAndSendRequest",
    "AddLogRequest",
    "EvmMessageSignRequest",
    "EthereumSignRequest",
    "SolanaSignRequest",
    "SwidgeQuoteRequest",
    "UpdateJobStatusRequest",
    # Response types
    "SignAndSendData",
    "SignAndSendResponse",
    "EvmMessageSignData",
    "EvmMessageSignResponse",
    "LogResponse",
    "SwidgeQuoteResponse",
    "SwidgeExecuteResponse",
    "UpdateJobStatusResponse",
    # Configuration types
    "SDKConfig",
]
