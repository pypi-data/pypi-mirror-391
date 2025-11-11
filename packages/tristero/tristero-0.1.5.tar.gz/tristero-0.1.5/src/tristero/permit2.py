import logging
from typing import Any, List, Optional, TypeVar, cast
from eth_account import Account
from eth_account.datastructures import SignedMessage, SignedTransaction
from eth_account.signers.base import BaseAccount
from eth_account.signers.local import LocalAccount
from eth_account.types import TransactionDictType
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
from web3 import AsyncBaseProvider, AsyncWeb3
from eth_typing import Address, ChecksumAddress
import time
import math
import random
import web3
from web3.contract import AsyncContract
from functools import cache, lru_cache
import json
from pathlib import Path
from importlib import resources as impresources

from web3 import Web3
from web3.eth import AsyncEth

from .api import (
    _WRAPPED_GAS_ADDRESSES,
    get_quote,
    _PERMIT2_CONTRACT_ADDRESSES,
    ChainID,
)

logger = logging.getLogger(__name__)

P = TypeVar("P", bound=AsyncBaseProvider)

PERMIT2_ABI_FILE = impresources.files("tristero.files") / "permit2_abi.json"
ERC20_ABI_FILE = impresources.files("tristero.files") / "erc20_abi.json"
PERMIT2_ABI = json.loads(PERMIT2_ABI_FILE.read_text())
ERC20_ABI = json.loads(ERC20_ABI_FILE.read_text())


@lru_cache(maxsize=None)
def get_permit2(eth: AsyncEth, permit2_address: str):
    return eth.contract(
        address=Web3.to_checksum_address(permit2_address), abi=PERMIT2_ABI
    )

@cache
def get_erc20_contract(w3: AsyncWeb3[P], token_address: str) -> AsyncContract:
    """Get ERC20 contract instance."""
    return w3.eth.contract(
        address=Web3.to_checksum_address(token_address), abi=ERC20_ABI
    )


class BaseSchema(BaseModel, frozen=True):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class TokenData(BaseSchema, frozen=True):
    address: str
    value: int


class ChainData(BaseSchema, frozen=True):
    chain_id: int
    token: TokenData


class OrderParameters(BaseSchema, frozen=True):
    src_asset: str
    dst_asset: str
    src_quantity: str
    dst_quantity: str
    min_quantity: str
    dark_salt: str


class OrderData(BaseSchema, frozen=True):
    parameters: OrderParameters
    deadline: int
    router_address: str
    filler_wallet_address: str
    order_type: str
    custom_data: List[bytes] = Field(default_factory=list)


class Quote(BaseSchema, frozen=True):
    order_data: OrderData


class SignedOrder(BaseSchema, frozen=True):
    sender: str
    parameters: OrderParameters
    deadline: str
    target: str
    filler: str
    order_type: str
    custom_data: List[bytes]


class TokenPermissions(BaseSchema, frozen=True):
    token: str
    amount: str


class EIP712Domain(BaseSchema, frozen=True):
    name: str
    chain_id: int
    verifying_contract: str


class PermitMessage(BaseSchema, frozen=True):
    permitted: TokenPermissions
    spender: str
    nonce: str
    deadline: str
    witness: SignedOrder


class SignatureData(BaseSchema, frozen=True):
    domain: EIP712Domain
    types: dict[str, Any]
    primary_type: str
    message: PermitMessage


def first_zero_bit(n: int) -> Optional[int]:
    if n > 0 and (n & (n + 1)) == 0:
        return None
    return (n ^ (n + 1)).bit_length() - 1


async def get_permit2_unordered_nonce(c: AsyncContract, wallet_address: str):
    startWord = random.randint(2**126, 2**189)
    endWord = startWord + 10
    wordPos = await anext(
        (
            ((w << 8) | bit)
            for w in range(startWord, endWord)
            if (
                bit := first_zero_bit(
                    await c.functions.nonceBitmap(wallet_address, w).call()
                )
            )
            is not None
        ),
        None,
    )
    if wordPos is None:
        raise Exception(f"No free unordered nonces in words {startWord}-{endWord}")
    return wordPos


async def prepare_data_for_signature(
    eth: AsyncEth,
    sell_data: ChainData,
    buy_data: ChainData,
    wallet_address: str,
    quote: Quote,
    destination_address: Optional[str] = None,
) -> SignatureData:
    """
    Prepare EIP-712 signature data for Permit2 witness transfer.

    Args:
        sell_data: Source chain and token data
        buy_data: Destination chain and token data
        wallet_address: User's wallet address
        quote: Quote data with order parameters and deadline
        destination_address: Optional destination address

    Returns:
        SignatureData with domain, types, primaryType, and message for signing
    """
    # Validate required fields
    if not quote.order_data.parameters.min_quantity:
        raise ValueError("Min quantity is required in the order_data.parameters")

    if not quote.order_data.router_address:
        raise ValueError("Router address is required in the order_data")

    if not quote.order_data.deadline:
        raise ValueError("Deadline is required in the order_data")

    from_chain = ChainID(str(sell_data.chain_id))

    deadline = quote.order_data.deadline

    # Handle native token address conversion
    token_address = (
        _WRAPPED_GAS_ADDRESSES[from_chain]
        if sell_data.token.address == "native"
        else sell_data.token.address
    )

    # Build witness object
    witness = SignedOrder(
        sender=wallet_address,
        parameters=OrderParameters(
            src_asset=token_address,
            dst_asset=buy_data.token.address,
            src_quantity=str(sell_data.token.value),
            dst_quantity=str(buy_data.token.value),
            min_quantity=quote.order_data.parameters.min_quantity,
            dark_salt=quote.order_data.parameters.dark_salt,
        ),
        deadline=str(deadline),
        target=destination_address or wallet_address,
        filler=quote.order_data.filler_wallet_address,
        order_type=quote.order_data.order_type,
        custom_data=quote.order_data.custom_data or [],
    )

    # Get Permit2 address
    permit2_address = _PERMIT2_CONTRACT_ADDRESSES.get(from_chain)
    if not permit2_address:
        raise ValueError("Permit2 not deployed on this chain.")

    spender = quote.order_data.router_address
    nonce = await get_permit2_unordered_nonce(
        get_permit2(eth, permit2_address), wallet_address
    )

    # EIP-712 domain
    domain = EIP712Domain(
        name="Permit2",
        chain_id=sell_data.chain_id,
        verifying_contract=permit2_address,
    )

    # EIP-712 types
    types = {
        "TokenPermissions": [
            {"name": "token", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "OrderParameters": [
            {"name": "srcAsset", "type": "address"},
            {"name": "dstAsset", "type": "address"},
            {"name": "srcQuantity", "type": "uint256"},
            {"name": "dstQuantity", "type": "uint256"},
            {"name": "minQuantity", "type": "uint256"},
            {"name": "darkSalt", "type": "uint128"},
        ],
        "SignedOrder": [
            {"name": "sender", "type": "address"},
            {"name": "parameters", "type": "OrderParameters"},
            {"name": "deadline", "type": "uint256"},
            {"name": "target", "type": "address"},
            {"name": "filler", "type": "address"},
            {"name": "orderType", "type": "string"},
            {"name": "customData", "type": "bytes[]"},
        ],
        "PermitWitnessTransferFrom": [
            {"name": "permitted", "type": "TokenPermissions"},
            {"name": "spender", "type": "address"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
            {"name": "witness", "type": "SignedOrder"},
        ],
    }

    # Build message
    message = PermitMessage(
        permitted=TokenPermissions(
            token=token_address,
            amount=str(sell_data.token.value),
        ),
        spender=spender,
        nonce=str(nonce),
        deadline=str(deadline),
        witness=witness,
    )

    return SignatureData(
        domain=domain,
        types=types,
        primary_type="PermitWitnessTransferFrom",
        message=message,
    )


async def sign_permit2(
    eth: AsyncEth,
    account: LocalAccount,
    wallet_address: str,
    src_amount: int,
    quote_data: dict[str, Any],
) -> tuple[SignatureData, SignedMessage]:
    from_chain_id = quote_data["src_token"]["chain_id"]
    from_address = quote_data["src_token"]["address"]
    to_chain_id = quote_data["dst_token"]["chain_id"]
    to_address = quote_data["dst_token"]["address"]

    order_data = quote_data["order_data"]
    dst_amount = int(order_data["parameters"]["dst_quantity"])

    to_sign = await prepare_data_for_signature(
        eth,
        ChainData(
            chain_id=from_chain_id,
            token=TokenData(address=from_address, value=src_amount),
        ),
        ChainData(
            chain_id=to_chain_id,
            token=TokenData(address=to_address, value=dst_amount),
        ),
        wallet_address,
        Quote(order_data=order_data),
    )
    # print(
    #     "Signing the following full message:",
    #     json.dumps(to_sign.model_dump(mode="json", by_alias=True)),
    # )
    signature = account.sign_typed_data(
        full_message=to_sign.model_dump(mode="json", by_alias=True)
    )
    return (to_sign, signature)


async def approve_permit2(
    w3: AsyncWeb3[P],
    account: LocalAccount,
    chain: ChainID,
    token_address: str,
    required_quantity: int,
    maxGas: int = 100000,
):
    wallet_address = account.address

    erc20 = get_erc20_contract(w3, token_address)
    permit2_contract = _PERMIT2_CONTRACT_ADDRESSES.get(chain)
    current_allowance = await erc20.functions.allowance(
        wallet_address, permit2_contract
    ).call()
    if current_allowance < required_quantity:
        logger.info(
            f"Approving {token_address}: allowance={current_allowance}, required={required_quantity}"
        )
        approve_fn = erc20.functions.approve(permit2_contract, 2**256 - 1)
        tx = await approve_fn.build_transaction(
            {
                "from": wallet_address,
                "nonce": await w3.eth.get_transaction_count(
                    w3.to_checksum_address(wallet_address)
                ),
                "gas": maxGas,  # Adjust as needed
                "gasPrice": await w3.eth.gas_price,
            }
        )

        # Sign and send transaction
        signed_tx: SignedTransaction = account.sign_transaction(tx.__dict__)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        logger.debug(f"→ Approval tx hash: {tx_hash.hex()}")
        return tx_hash.hex()


async def create_order(
    w3: AsyncWeb3[P],
    account: LocalAccount,
    src_chain: ChainID,
    src_token: str,
    dst_chain: ChainID,
    dst_token: str,
    raw_amount: int,
    to_address: Optional[str] = None,
):
    if not to_address:
        to_address = account.address
    q = await get_quote(
        account.address,
        to_address,
        src_chain,
        src_token,
        dst_chain,
        dst_token,
        raw_amount,
    )
    await approve_permit2(w3, account, src_chain, src_token, raw_amount)
    # print("Quote: ", json.dumps(q))
    return await sign_permit2(w3.eth, account, account.address, raw_amount, q)
