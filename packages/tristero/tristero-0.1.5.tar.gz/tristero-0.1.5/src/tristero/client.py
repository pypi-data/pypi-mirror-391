import asyncio
import json
import logging
from typing import Any, Optional, TypeVar

from eth_account.signers.local import LocalAccount
from pydantic import BaseModel

from tristero.api import ChainID, fill_order, poll_updates
from .permit2 import create_order
from web3 import AsyncBaseProvider, AsyncWeb3
import logging
from web3 import AsyncWeb3
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
logger = logging.getLogger(__name__)

P = TypeVar("P", bound=AsyncBaseProvider)

class WebSocketClosedError(Exception):
    pass

class SwapException(Exception):
    """Base exception for all swap-related errors."""
    pass


class StuckException(SwapException):
    """Raised when swap execution times out"""
    pass


class OrderFailedException(SwapException):
    """Order execution failed on-chain."""
    def __init__(self, message: str, order_id: str, details: dict[str, Any]):
        super().__init__(message)
        self.order_id = order_id
        self.details = details

class TokenSpec(BaseModel, frozen=True):
    chain_id: ChainID
    token_address: str

async def wait_for_completion(order_id: str):
    ws = await poll_updates(order_id)
    try:
        async for msg in ws:
            msg = json.loads(msg)
            logger.info(
                {
                    "message": f"failed={msg['failed']} completed={msg['completed']}",
                    "id": "order_update",
                    "payload": msg,
                }
            )
            if msg["failed"]:
                await ws.close()
                raise Exception(f"Swap failed: {ws.close_reason} {msg}")
            elif msg["completed"]:
                await ws.close()
                return msg

        # If we exit the loop without completed/failed, raise to retry
        raise WebSocketClosedError("WebSocket closed without completion status")
    except Exception:
        # Close cleanly if still open
        if not ws.close_code:
            await ws.close()
        raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(WebSocketClosedError)
)
async def wait_for_completion_with_retry(order_id: str):
    return await wait_for_completion(order_id)

async def start_swap(w3: AsyncWeb3[P], account: LocalAccount, from_t: TokenSpec, to_t: TokenSpec, raw_amount: int) -> str:
    """
    Execute a token swap operation.

    Args:
        w3: Web3 provider instance
        account: Account to execute swap from
        from_t: Source token specification
        to_t: Target token specification
        raw_amount: Amount in smallest unit (e.g., wei)

    Returns:
        Order ID for tracking the swap

    Raises:
        Exception: If order creation or submission fails
    """
    data, sig = await create_order(
        w3,
        account,
        from_t.chain_id,
        from_t.token_address,
        to_t.chain_id,
        to_t.token_address,
        raw_amount,
    )
    response = await fill_order(
        str(sig.signature.to_0x_hex()),
        data.domain.model_dump(by_alias=True, mode="json"),
        data.message.model_dump(by_alias=True, mode="json"),
    )

    return response['id']

async def execute_swap(
    w3: AsyncWeb3[P],
    account: LocalAccount,
    src_t: TokenSpec,
    dst_t: TokenSpec,
    raw_amount: int,
    retry: bool = True,
    timeout: Optional[float] = None
) -> dict[str, Any]:
    """Execute and wait for swap completion."""
    order_id = await start_swap(
        w3,
        account,
        src_t,
        dst_t,
        raw_amount
    )
    logger.info(f"Swap order placed: {order_id}")

    waiter = wait_for_completion_with_retry if retry else wait_for_completion

    try:
        if timeout is None:
            return await waiter(order_id)

        return await asyncio.wait_for(
            waiter(order_id),
            timeout=timeout
        )
    except asyncio.TimeoutError as exc:
        raise StuckException(f"Swap {order_id} timed out after {timeout}s") from exc
