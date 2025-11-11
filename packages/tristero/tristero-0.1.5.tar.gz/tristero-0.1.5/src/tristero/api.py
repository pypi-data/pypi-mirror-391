from enum import Enum
from typing import Any, Optional
import httpx
from websockets.asyncio.client import connect
from tristero.config import get_config

class ChainID(str, Enum):
    arbitrum = "42161"
    avalanche = "43114"
    base = "8453"
    blast = "81457"
    bsc = "56"
    celo = "42220"
    ethereum = "1"
    mantle = "5000"
    mode = "34443"
    opbnb = "204"
    optimism = "10"
    polygon = "137"
    scroll = "534352"
    solana = "1151111081099710"
    tron = "728126428"
    unichain = "130"
    sei = "1329"
    sonic = "146"
    linea = "59144"
    worldchain = "480"
    codex = "81224"
    plume = "98866"
    hyperevm = "999"

_WRAPPED_GAS_ADDRESSES = {
    ChainID.ethereum: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    ChainID.unichain: "0x4200000000000000000000000000000000000006",
    ChainID.optimism: "0x4200000000000000000000000000000000000006",
    ChainID.arbitrum: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
    ChainID.avalanche: "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
    ChainID.polygon: "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    ChainID.base: "0x4200000000000000000000000000000000000006",
    ChainID.bsc: "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    ChainID.blast: "0x4300000000000000000000000000000000000004",
    ChainID.mode: "0x4200000000000000000000000000000000000006",
    ChainID.solana: "So11111111111111111111111111111111111111112",
    ChainID.sonic: "0x039e2fB66102314Ce7b64Ce5Ce3E5183bc94aD38",
    ChainID.linea: "0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f",
    ChainID.sei: "0xE30feDd158A2e3b13e9badaeABaFc5516e95e8C7",
    ChainID.worldchain: "0x4200000000000000000000000000000000000006",
    ChainID.plume: "0xEa237441c92CAe6FC17Caaf9a7acB3f953be4bd1",
    ChainID.hyperevm: "0x5555555555555555555555555555555555555555",
}

_PERMIT2_CONTRACT_ADDRESSES = {
    ChainID.ethereum: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.avalanche: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.arbitrum: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.base: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.bsc: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.optimism: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.polygon: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.unichain: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.linea: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.worldchain: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.sonic: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.sei: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.blast: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.mode: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.scroll: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.plume: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    ChainID.hyperevm: "0x000000000022D473030F116dDEE9F6B43aC78BA3",
}

class APIException(Exception):
    pass

class QuoteException(Exception):
    pass

def handle_resp(resp: httpx.Response):
    try:
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        try:
            data = resp.json()
        except Exception as json_e:
            if resp.text:
                raise APIException(resp.text)
            else:
                raise e
        raise APIException(data)

async def t_get(client: httpx.AsyncClient, url: str):
    resp = await client.get(url, headers=get_config().headers, timeout=20)
    return handle_resp(resp)


async def t_post(client: httpx.AsyncClient, url: str, body: Optional[dict[str, Any]]):
    resp = await client.post(url, headers=get_config().headers, json=body, timeout=20)
    return handle_resp(resp)


def native_address(chain_id: ChainID) -> str:
    return "0x0000000000000000000000000000000000000000"


def or_native(chain_id: ChainID, address: str):
    return native_address(chain_id) if address == "native" else address


async def get_quote(
    from_wallet: str,
    to_wallet: str,
    from_chain_id: ChainID,
    from_address: str,
    to_chain_id: ChainID,
    to_address: str,
    amount: int,
):
    from_chain_id = from_chain_id
    to_chain_id = to_chain_id

    from_token_address = or_native(from_chain_id, from_address)
    to_token_address = or_native(to_chain_id, to_address)

    async with httpx.AsyncClient() as c:
        data = {
            "src_chain_id": from_chain_id.value,
            "src_token_address": from_token_address,
            "src_token_quantity": str(int(amount)),
            "src_wallet_address": from_wallet,
            "dst_chain_id": to_chain_id.value,
            "dst_token_address": to_token_address,
            "dst_wallet_address": to_wallet,
        }
        resp = await c.post(
            get_config().quoter_url,
            json=data,
        )
        # print(data, resp)
        try:
            return handle_resp(resp)
        except Exception as e:
            raise QuoteException(e, data) from e


async def fill_order(signature: str, domain: dict[str, Any], message: dict[str, Any]):
    async with httpx.AsyncClient() as c:
        data = {"signature": signature, "domain": domain, "message": message}
        resp = await c.post(
            get_config().filler_url,
            json=data,
        )
        return handle_resp(resp)

async def poll_updates(order_id: str):
    ws = await connect(f"{get_config().ws_url}/{order_id}")
    return ws
