"""
Swidge cross-chain swap operations.

This module provides the SwidgeApi class for cross-chain swaps and bridges
using the Swidge protocol.
"""

import json
from typing import TYPE_CHECKING, Any, overload

from .client import APIError
from .types import (
    SwidgeData,
    SwidgeExecuteResponse,
    SwidgeExecuteResponseData,
    SwidgeQuoteRequest,
    SwidgeQuoteResponse,
)

if TYPE_CHECKING:
    from .agent_sdk import AgentSdk


def _ensure_string_error(error: Any) -> str:
    """
    Ensure error is always a string, converting dicts/objects to JSON if needed.

    Args:
        error: Error value that might be a string, dict, or other type

    Returns:
        String representation of the error
    """
    if error is None:
        return "Unknown error"
    elif isinstance(error, dict):
        return json.dumps(error)
    else:
        return str(error)


class SwidgeApi:
    """Cross-chain swap operations using Swidge.

    Workflow: quote() -> execute(quote.data) -> check result.data.status
    """

    def __init__(self, sdk: "AgentSdk"):
        self._sdk = sdk

    def quote(self, request: SwidgeQuoteRequest | dict) -> SwidgeQuoteResponse:
        """Get a cross-chain swap or bridge quote.

        Args:
            request: Quote parameters with wallet info, amount, and optional tokens/slippage.
                from: Source wallet {"network": "ethereum:1", "address": "0x..."}
                to: Destination wallet {"network": "ethereum:42161", "address": "0x..."}
                amount: Amount in smallest unit (e.g., "1000000000000000000" for 1 ETH)
                fromToken: Source token address (optional, omit for native tokens)
                toToken: Destination token address (optional, omit for native tokens)
                slippage: Slippage tolerance % as string (default: "0.5")

        Returns:
            SwidgeQuoteResponse with pricing, fees, and transaction steps.

        Example:
            quote = sdk.swidge.quote({
                "from": {"network": "ethereum:1", "address": user_address},
                "to": {"network": "ethereum:42161", "address": user_address},
                "amount": "1000000000000000000",  # 1 ETH
                "toToken": "0x2f2a2543B76A4166549F7aaB2e75BEF0aefC5b0f"  # WBTC
            })
        """
        return self._handle_swidge_quote(request)

    @overload
    def execute(self, quote_data: SwidgeData) -> SwidgeExecuteResponse: ...

    @overload
    def execute(self, quote_data: list[SwidgeData]) -> list[SwidgeExecuteResponse]: ...

    def execute(
        self, quote_data: SwidgeData | list[SwidgeData]
    ) -> SwidgeExecuteResponse | list[SwidgeExecuteResponse]:
        """Execute a cross-chain swap or bridge using a quote.

        Supports both single and bulk execution:
        - Pass a single quote → get a single response
        - Pass a list of quotes → get a list of responses

        Args:
            quote_data: Complete quote object(s) from sdk.swidge.quote().

        Returns:
            SwidgeExecuteResponse or list of responses (matching input type) with transaction status and details.

        Example:
            # Single execution (type-safe pattern)
            quote = sdk.swidge.quote({...})
            if quote.success and quote.data is not None:
                result = sdk.swidge.execute(quote.data)
                if result.success and result.data is not None:
                    print(f"Status: {result.data.status}")

            # Bulk execution (type-safe pattern)
            quote1 = sdk.swidge.quote({...})
            quote2 = sdk.swidge.quote({...})
            if (quote1.success and quote1.data is not None and
                quote2.success and quote2.data is not None):
                results = sdk.swidge.execute([quote1.data, quote2.data])
                for result in results:
                    if result.success and result.data is not None:
                        print(f"Status: {result.data.status}")
        """
        return self._handle_swidge_execute(quote_data)

    def _handle_swidge_quote(
        self, request: SwidgeQuoteRequest | dict
    ) -> SwidgeQuoteResponse:
        """Handle swidge quote requests."""
        self._sdk._log("SWIDGE_QUOTE", {"request": request})

        try:
            # Handle both dict and Pydantic model inputs
            if isinstance(request, dict):
                request_obj = SwidgeQuoteRequest(**request)
            else:
                request_obj = request

            response = self._sdk.client.post(
                "/v1/swap/quote",
                request_obj.model_dump(mode="json", by_alias=True, exclude_unset=True),
            )

            # Parse into SwidgeData with extra="allow" to preserve all API fields
            # This is critical - we must not drop any fields the API returns
            if not isinstance(response, dict):
                raise ValueError("Expected dict response from swidge quote endpoint")
            return SwidgeQuoteResponse(
                success=True,
                error=None,
                data=SwidgeData(**response["data"]),
                error_details=None,
            )
        except APIError as api_error:
            # APIError has both error and message from API response
            self._sdk._log("=== SWIDGE QUOTE ERROR ===")
            self._sdk._log("Error:", api_error.error_message)
            self._sdk._log("=========================")

            return SwidgeQuoteResponse(
                success=False,
                data=None,
                error=_ensure_string_error(
                    api_error.error_message
                ),  # Always ensure it's a string
                error_details=api_error.error_details,  # Contains both 'error' and 'message' from API
            )
        except Exception as error:
            # Handle unexpected non-API errors
            error_message = _ensure_string_error(
                str(error) or "Failed to get swidge quote"
            )
            return SwidgeQuoteResponse(
                success=False,
                data=None,
                error=error_message,
                error_details={"type": type(error).__name__},
            )

    @overload
    def _handle_swidge_execute(
        self, quote_data: SwidgeData
    ) -> SwidgeExecuteResponse: ...

    @overload
    def _handle_swidge_execute(
        self, quote_data: list[SwidgeData]
    ) -> list[SwidgeExecuteResponse]: ...

    def _handle_swidge_execute(
        self, quote_data: SwidgeData | list[SwidgeData]
    ) -> SwidgeExecuteResponse | list[SwidgeExecuteResponse]:
        """Handle swidge execute requests (single or bulk)."""

        # Log execution type
        if isinstance(quote_data, list):
            self._sdk._log("SWIDGE_EXECUTE", {"quotes": f"{len(quote_data)} quotes"})
        else:
            self._sdk._log("SWIDGE_EXECUTE", {"quote": quote_data})

        try:
            # Prepare payload - handle both single and list cases
            payload: list[dict[str, Any]] | dict[str, Any]
            if isinstance(quote_data, list):
                # Serialize each quote in the list
                payload = []
                for quote in quote_data:
                    quote_payload = quote.model_dump(
                        mode="json", by_alias=True, exclude_none=False
                    )

                    # Strip None values from gas-related fields in transaction details
                    if "steps" in quote_payload:
                        for step in quote_payload["steps"]:
                            if (
                                step.get("type") == "transaction"
                                and "transactionDetails" in step
                            ):
                                tx_details = step["transactionDetails"]
                                if tx_details.get("type") == "evm":
                                    # Remove None values for optional number fields
                                    for field in [
                                        "gas",
                                        "maxFeePerGas",
                                        "maxPriorityFeePerGas",
                                    ]:
                                        if (
                                            field in tx_details
                                            and tx_details[field] is None
                                        ):
                                            del tx_details[field]

                    payload.append(quote_payload)
            else:
                # Single quote serialization
                payload = quote_data.model_dump(
                    mode="json", by_alias=True, exclude_none=False
                )

                # Strip None values from gas-related fields in transaction details
                if "steps" in payload:
                    for step in payload["steps"]:
                        if (
                            step.get("type") == "transaction"
                            and "transactionDetails" in step
                        ):
                            tx_details = step["transactionDetails"]
                            if tx_details.get("type") == "evm":
                                # Remove None values for optional number fields
                                for field in [
                                    "gas",
                                    "maxFeePerGas",
                                    "maxPriorityFeePerGas",
                                ]:
                                    if (
                                        field in tx_details
                                        and tx_details[field] is None
                                    ):
                                        del tx_details[field]

            # Always use the single /execute endpoint
            response = self._sdk.client.post(
                "/v1/swap/execute",
                payload,
            )

            # Extract data from standardized API response
            if not isinstance(response, dict):
                raise ValueError("Expected dict response from swidge execute endpoint")

            response_data = response["data"]

            # Handle response based on input type
            if isinstance(quote_data, list):
                # Response should be a list
                if not isinstance(response_data, list):
                    raise ValueError("Expected list response for bulk execution")

                wrapped_responses = []
                for item in response_data:
                    execute_data = SwidgeExecuteResponseData(**item)
                    # success=True only if status is 'success'
                    is_success = execute_data.status == "success"
                    wrapped_responses.append(
                        SwidgeExecuteResponse(
                            success=is_success,
                            error=execute_data.error if not is_success else None,
                            data=execute_data,
                            error_details=None,
                        )
                    )
                return wrapped_responses
            else:
                # Single response
                if not isinstance(response_data, dict):
                    raise ValueError("Expected dict response for single execution")
                execute_data = SwidgeExecuteResponseData(**response_data)
                # success=True only if status is 'success'
                is_success = execute_data.status == "success"
                return SwidgeExecuteResponse(
                    success=is_success,
                    error=execute_data.error if not is_success else None,
                    data=execute_data,
                    error_details=None,
                )

        except APIError as api_error:
            # APIError has both error and message from API response
            self._sdk._log("=== SWIDGE EXECUTE ERROR ===")
            self._sdk._log("Error:", api_error.error_message)
            self._sdk._log("============================")

            error_response = SwidgeExecuteResponse(
                success=False,
                data=None,
                error=_ensure_string_error(api_error.error_message),
                error_details=api_error.error_details,
            )

            # Return matching type based on input
            if isinstance(quote_data, list):
                return [error_response]
            else:
                return error_response

        except Exception as error:
            # Handle unexpected non-API errors
            error_message = _ensure_string_error(
                str(error) or "Failed to execute swidge swap"
            )
            error_response = SwidgeExecuteResponse(
                success=False,
                data=None,
                error=error_message,
                error_details={"type": type(error).__name__},
            )

            # Return matching type based on input
            if isinstance(quote_data, list):
                return [error_response]
            else:
                return error_response
