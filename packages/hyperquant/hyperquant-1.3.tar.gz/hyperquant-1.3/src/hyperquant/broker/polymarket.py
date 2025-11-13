from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any, Iterable, Iterator, Literal, Mapping, Sequence

import json

import aiohttp
import pybotters
import pybotters.ws

from .models.polymarket import PolymarketDataStore
from .auth import Auth

DEFAULT_REST_ENDPOINT = "https://clob.polymarket.com"
DEFAULT_WS_ENDPOINT = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
GAMMA_EVENTS_API = "https://gamma-api.polymarket.com/events"
DEFAULT_DATA_ENDPOINT = "https://data-api.polymarket.com"
DEFAULT_BASE_SLUG = "btc-updown-15m"
DEFAULT_INTERVAL = 15 * 60
DEFAULT_WINDOW = 8
API_NAME = "polymarket"
END_CURSOR = "LTE="
USDC_CONTRACT = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ERC20_BALANCE_OF_ABI = (
    "[{\"constant\":true,\"inputs\":[{\"name\":\"account\",\"type\":\"address\"}],"
    "\"name\":\"balanceOf\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],"
    "\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"}]"
)
DEFAULT_POLYGON_RPCS = (
    "https://polygon.llamarpc.com",
    "https://polygon-rpc.com",
    "https://rpc.ankr.com/polygon",
)


def _iter_offsets(window: int) -> Iterator[int]:
    yield 0
    for step in range(1, window + 1):
        yield step
        yield -step


def _parse_list(value: Any) -> list[Any]:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    if value is None:
        return []
    return list(value)


def _accepting_orders(market: Mapping[str, Any]) -> bool:
    accepting = market.get("acceptingOrders") or market.get("accepting_orders")
    if isinstance(accepting, str):
        return accepting.lower() == "true"
    return bool(accepting)


class Polymarket:
    """Polymarket CLOB client with REST helpers, stores and WS subscriptions."""

    def __init__(
        self,
        client: pybotters.Client,
        *,
        rest_api: str | None = None,
        ws_public: str | None = None,
        private_key: str | None = None,
        chain_id: int | None = None,
        signature_type: int | None = None,
        funder: str | None = None
    ) -> None:
        self.client = client
        self.rest_api = (rest_api or DEFAULT_REST_ENDPOINT).rstrip("/")
        self.ws_public = ws_public or DEFAULT_WS_ENDPOINT

        self.chain_id = chain_id or 137
        # Default to POLY_GNOSIS_SAFE (2) to match common proxy flows used in examples/tests.
        # Users can override via constructor.
        self.signature_type = signature_type if signature_type is not None else 2
        self.funder = funder

        self.store = PolymarketDataStore()
        self._ws_public: pybotters.ws.WebSocketApp | None = None
        self._ws_public_ready = asyncio.Event()
        self._ws_personal: pybotters.ws.WebSocketApp | None = None

        self._ensure_session_entry(private_key=private_key, funder=funder)

    async def __aenter__(self) -> "Polymarket":
        await self.create_or_derive_api_creds()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - 
        await self.aclose()

    async def aclose(self) -> None:
        if self._ws_public is not None:
            with suppress(Exception):
                await self._ws_public.current_ws.close()
            self._ws_public = None
            self._ws_public_ready.clear()

    # ------------------------------------------------------------------
    # Store helpers

    async def update(
        self,
        update_type: Literal[
            "all",
            "markets",
            "book",
            "books",
            "position",
            "history_position",
            "orders",
        ] = "all",
        *,
        token_ids: Sequence[str] | str | None = None,
        limit: int | None = None,
        funder: str | None = None,

    ) -> None:
        """Refresh cached data using Polymarket REST endpoints."""

        include_detail = update_type in {"all", "detail", "markets"}
        include_books = update_type in {"all", "book", "books"}
        include_position = update_type in {"all", "position"}
        include_history_position = update_type in {"all", "history_position"}
        include_orders = update_type in {"all", "orders"}

        if include_books and token_ids is None:
            raise ValueError("token_ids are required when updating books")

        tasks: list[tuple[str, Any]] = []
        if include_detail:
            params = {"limit": limit} if limit else None
            tasks.append(
                (
                    "detail",
                    asyncio.create_task(
                        self._rest("GET", "/markets", params=params)
                    ),
                )
            )

        if include_books and token_ids is not None:
            body = [{"token_id": tid} for tid in self._token_list(token_ids)]
            tasks.append(
                (
                    "books",
                    asyncio.create_task(
                        self._rest("POST", "/books", json=body)
                    ),
                )
            )
        
        if include_position or include_history_position:
            funder = funder or self.funder
            path = '/positions' if include_position else '/closed-positions'
            tasks.append(
                (
                    "position",
                    asyncio.create_task(
                        self._rest(
                            "GET",
                            path,
                            params={"user": funder},
                            host=DEFAULT_DATA_ENDPOINT
                        )
                    ),
                )
            )

        if include_orders:
            tasks.append(("orders", asyncio.create_task(self.get_orders())))
        

        if not tasks:
            raise ValueError(f"Unsupported update_type={update_type}")

        results: dict[str, Any] = {}
        for key, fut in tasks:
            results[key] = await fut


        if "books" in results:
            entries = results["books"].get("data") or results["books"]
            for entry in entries or []:
                message = {
                    "event_type": "book",
                    "asset_id": entry.get("asset_id") or entry.get("token_id"),
                    "bids": entry.get("bids"),
                    "asks": entry.get("asks"),
                }
                self.store.book._on_message(message)
        
        if "position" in results or "history_position" in results:
            data = results["position"]
            self.store.position._on_response(data)

        if "orders" in results:
            orders = results["orders"]
            self.store.orders._on_response(orders)


        

    async def sub_books(
        self,
        token_ids: Sequence[str] | str,
    ) -> pybotters.ws.WebSocketApp:
        """Subscribe to public order-book updates for the provided token ids."""

        tokens = self._token_list(token_ids)
        payload = {"type": "market", "assets_ids": tokens}
        self._ws_public = self.client.ws_connect(
            self.ws_public,
            send_json=payload,
            hdlr_json=self.store.onmessage,
        )
        await self._ws_public._event.wait()
        return self._ws_public
    
    async def sub_personal(
        self,
        callback: Any = None,
        markets: Sequence[str] | None = None,
    ) -> pybotters.ws.WebSocketApp:
        """Subscribe to personal updates (requires authentication)."""

        creds = self._api_creds()
        if not creds:
            raise RuntimeError("Polymarket API credentials are required for personal subscriptions")

        def _handler(message, ws=None):
            self.store.onmessage(message, ws)
            if callback:
                callback(message, ws)

        effective_cb = _handler if callback else self.store.onmessage

        api_key = creds.get("api_key")
        api_secret = creds.get("api_secret")
        api_passphrase = creds.get("api_passphrase")
        if not api_key or not api_secret or not api_passphrase:
            raise RuntimeError("Polymarket API key/secret/passphrase missing; call create_or_derive_api_creds")

        auth = {"apiKey": api_key, "secret": api_secret, "passphrase": api_passphrase}
        payload = {"markets": list(markets or []), "type": "user", "auth": auth}

        self._ws_personal = self.client.ws_connect(
            "wss://ws-subscriptions-clob.polymarket.com/ws/user",
            hdlr_json=effective_cb,
            auth=None,
        )
        await self._ws_personal._event.wait()
        await self._ws_personal.current_ws.send_json(payload)
        return self._ws_personal

    # ------------------------------------------------------------------
    # Public REST endpoints

    async def get_markets(self, **params: Any) -> Any:
        return await self._rest("GET", "/markets", params=params or None)

    async def get_market(self, market_id: str) -> Any:
        return await self._rest("GET", f"/markets/{market_id}")

    async def get_market_by_slug(self, slug: str) -> Any:
        """Fetch a market using its human-readable slug."""
        # https://gamma-api.polymarket.com/markets/slug/{slug}
        return await self._rest("GET", f"/slug/{slug}", host='https://gamma-api.polymarket.com/markets')
    
    async def get_order_book(self, token_id: str) -> Any:
        return await self._rest("GET", "/book", params={"token_id": token_id})

    async def get_order_books(self, token_ids: Sequence[str] | str) -> Any:
        body = [{"token_id": tid} for tid in self._token_list(token_ids)]
        return await self._rest("POST", "/books", json=body)

    async def get_midpoint(self, token_id: str) -> Any:
        return await self._rest("GET", "/midpoint", params={"token_id": token_id})

    async def get_midpoints(self, token_ids: Sequence[str] | str) -> Any:
        body = [{"token_id": tid} for tid in self._token_list(token_ids)]
        return await self._rest("POST", "/midpoints", json=body)

    async def get_price(self, token_id: str, side: str) -> Any:
        return await self._rest("GET", "/price", params={"token_id": token_id, "side": side})

    async def get_prices(self, requests: Iterable[Mapping[str, str]]) -> Any:
        body = [dict(req) for req in requests]
        return await self._rest("POST", "/prices", json=body)

    async def get_spread(self, token_id: str) -> Any:
        return await self._rest("GET", "/spread", params={"token_id": token_id})

    async def get_spreads(self, token_ids: Sequence[str] | str) -> Any:
        body = [{"token_id": tid} for tid in self._token_list(token_ids)]
        return await self._rest("POST", "/spreads", json=body)

    async def get_last_trade_price(self, token_id: str) -> Any:
        return await self._rest("GET", "/last-trade-price", params={"token_id": token_id})

    async def get_last_trades_prices(self, token_ids: Sequence[str] | str) -> Any:
        body = [{"token_id": tid} for tid in self._token_list(token_ids)]
        return await self._rest("POST", "/last-trades-prices", json=body)

    async def get_tick_size(self, token_id: str) -> Any:
        return await self._rest("GET", "/tick-size", params={"token_id": token_id})

    async def get_neg_risk(self, token_id: str) -> Any:
        return await self._rest("GET", "/neg-risk", params={"token_id": token_id})

    async def get_fee_rate(self, token_id: str) -> Any:
        return await self._rest("GET", "/fee-rate", params={"token_id": token_id})

    # ------------------------------------------------------------------
    # Credential management (Level 1 / Level 2)

    async def create_api_key(self, nonce: int | None = None) -> dict[str, Any]:
        params = {"nonce": nonce} if nonce is not None else None
        data = await self._rest("POST", "/auth/api-key", params=params)
        self._store_api_creds(data)
        return data

    async def derive_api_key(self, nonce: int | None = None) -> dict[str, Any]:
        params = {"nonce": nonce} if nonce is not None else None
        data = await self._rest("GET", "/auth/derive-api-key", params=params)
        self._store_api_creds(data)
        return data

    async def create_or_derive_api_creds(self, nonce: int | None = None) -> dict[str, Any]:
        try:
            return await self.derive_api_key(nonce)
        except Exception:
            return await self.create_api_key(nonce)

    async def get_api_keys(self) -> Any:
        return await self._rest("GET", "/auth/api-keys")

    async def delete_api_key(self) -> Any:
        return await self._rest("DELETE", "/auth/api-key")

    async def get_closed_only_mode(self) -> Any:
        return await self._rest("GET", "/auth/ban-status/closed-only")

    # ------------------------------------------------------------------
    # Trading helpers (Level 2)

    async def post_order(
        self,
        signed_order: Mapping[str, Any],
        *,
        order_type: str = "GTC",
        owner: str | None = None,
    ) -> Any:
        """Low-level publish for an already-signed order.

        Prefer ``place_order`` for a compact, user-friendly API.
        """
        payload = {
            "order": dict(signed_order),
            "owner": self._owner_key(owner),
            "orderType": order_type,
        }
        return await self._rest("POST", "/order", json=payload)

    # ------------------------------------------------------------------
    # Compact order placement (py_clob_client-like)

    @staticmethod
    def _round_down(x: float, sig_digits: int) -> float:
        from math import floor

        return floor(x * (10**sig_digits)) / (10**sig_digits)

    @staticmethod
    def _round_normal(x: float, sig_digits: int) -> float:
        return round(x * (10**sig_digits)) / (10**sig_digits)

    @staticmethod
    def _round_up(x: float, sig_digits: int) -> float:
        from math import ceil

        return ceil(x * (10**sig_digits)) / (10**sig_digits)

    @staticmethod
    def _decimal_places(x: float) -> int:
        from decimal import Decimal

        return abs(Decimal(x.__str__()).as_tuple().exponent)

    @classmethod
    def _to_token_decimals(cls, x: float) -> int:
        f = (10**6) * x
        if cls._decimal_places(f) > 0:
            f = cls._round_normal(f, 0)
        return int(f)

    @staticmethod
    def _contracts(chain_id: int, neg_risk: bool = False) -> dict[str, str]:
        """Minimal contract config (avoid external deps)."""
        cfg = {
            False: {
                137: {
                    "exchange": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
                    "collateral": USDC_CONTRACT,
                    "conditional_tokens": "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
                },
                80002: {
                    "exchange": "0xdFE02Eb6733538f8Ea35D585af8DE5958AD99E40",
                    "collateral": "0x9c4e1703476e875070ee25b56a58b008cfb8fa78",
                    "conditional_tokens": "0x69308FB512518e39F9b16112fA8d994F4e2Bf8bB",
                },
            },
            True: {
                137: {
                    "exchange": "0xC5d563A36AE78145C45a50134d48A1215220f80a",
                    "collateral": USDC_CONTRACT,
                    "conditional_tokens": "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
                },
                80002: {
                    "exchange": "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296",
                    "collateral": "0x9c4e1703476e875070ee25b56a58b008cfb8fa78",
                    "conditional_tokens": "0x69308FB512518e39F9b16112fA8d994F4e2Bf8bB",
                },
            },
        }
        try:
            return cfg[bool(neg_risk)][int(chain_id)]
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"Unsupported chain_id={chain_id} for Polymarket") from e

    @staticmethod
    def _rounding_for_tick(tick_size: str | float) -> tuple[int, int, int]:
        """Return (price_digits, size_digits, amount_digits) for tick_size."""
        ts = str(tick_size)
        mapping = {
            "0.1": (1, 2, 3),
            "0.01": (2, 2, 4),
            "0.001": (3, 2, 5),
            "0.0001": (4, 2, 6),
        }
        return mapping.get(ts, (2, 2, 4))

    async def place_order(
        self,
        *,
        token_id: str,
        side: str,
        price: float,
        size: float,
        order_type: str = "GTC",
        tick_size: str | float | None = None,
        fee_rate_bps: int | None = None,
        expiration: int | None = None,
        taker: str = ZERO_ADDRESS,
        neg_risk: bool = False,
        owner: str | None = None,
        nonce: int | None = None,
    ) -> Any:
        """Create, sign and submit an order with a compact interface.

        Parameters
        - token_id: outcome token id
        - side: 'BUY' | 'SELL'
        - price: float price
        - size: float size (in outcome tokens)
        - order_type: 'GTC' (default) or other server-accepted types
        - fee_rate_bps: optional fee bps; defaults to market fee
        - expiration: unix seconds; defaults to 0 (no expiry)
        - taker: zero address by default (public order)
        - neg_risk: whether market is negative risk
        - owner: API key owner (defaults to current credentials)
        - nonce: onchain nonce, default 0
        """

        # Ensure L2 creds exist
        if not self._api_creds():
            raise RuntimeError("Polymarket API credentials missing; call create_or_derive_api_creds first")

        private_key, maker_addr, signer_addr = self._get_signing_context()
        signed_dict = await self._build_signed_order(
            private_key=private_key,
            maker_addr=maker_addr,
            signer_addr=signer_addr,
            token_id=token_id,
            side=side,
            price=price,
            size=size,
            tick_size=tick_size,
            fee_rate_bps=fee_rate_bps,
            expiration=expiration,
            taker=taker,
            neg_risk=neg_risk,
            nonce=nonce,
        )

        # Submit (use aiohttp session directly with HMAC headers for performance)
        payload = {
            "order": signed_dict,
            "owner": self._owner_key(owner),
            "orderType": order_type,
        }
        return await self._signed_request_via_session("POST", "/order", payload)

    async def _signed_request_via_session(
        self, method: str, path: str, body: Mapping[str, Any] | list[Any] | None
    ) -> Any:
        import time, base64, hmac, hashlib
        from eth_account import Account as _A
        import aiohttp

        method = method.upper()
        session: aiohttp.ClientSession = getattr(self.client, "_session", None)
        if session is None:
            raise RuntimeError("pybotters client session missing")
        creds = getattr(session, "_polymarket_api_creds", None)
        if not creds:
            raise RuntimeError("Polymarket API creds missing; call create_or_derive_api_creds")
        api_key = creds.get("api_key")
        api_secret = creds.get("api_secret")
        api_passphrase = creds.get("api_passphrase")

        entry = getattr(session, "_apis", {}).get(API_NAME, [])
        private_key = entry[0] if entry else None
        addr = _A.from_key(private_key).address if private_key else None

        ts = int(time.time())
        request_path = path
        url = f"{self.rest_api}{request_path}"
        payload_obj = dict(body) if isinstance(body, dict) else body
        serialized = (
            str(payload_obj).replace("'", '"') if payload_obj is not None else ""
        )
        secret_bytes = base64.urlsafe_b64decode(api_secret)
        msg = f"{ts}{method}{request_path}{serialized}"
        sig = hmac.new(secret_bytes, msg.encode("utf-8"), hashlib.sha256).digest()
        sign_b64 = base64.urlsafe_b64encode(sig).decode("utf-8")

        headers = {
            "POLY_ADDRESS": addr,
            "POLY_SIGNATURE": sign_b64,
            "POLY_TIMESTAMP": str(ts),
            "POLY_API_KEY": api_key,
            "POLY_PASSPHRASE": api_passphrase,
            "Content-Type": "application/json",
        }

        async with session.request(method, url, headers=headers, data=(serialized or None)) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise RuntimeError(f"Polymarket {method} {path} failed: {resp.status} {text}")
            try:
                return await resp.json()
            except Exception:
                return await resp.text()

    def _get_signing_context(self) -> tuple[str, str, str]:
        from eth_account import Account as _A

        session = getattr(self.client, "_session", None)
        apis = getattr(session, "_apis", {}) if session else {}
        entry = list(apis.get(API_NAME, [])) if isinstance(apis, dict) else []
        private_key = entry[0] if entry and entry[0] else None
        if not private_key:
            raise RuntimeError("Polymarket private key not configured in apis.json")
        if not str(private_key).startswith("0x"):
            private_key = f"0x{private_key}"

        signer_addr = _A.from_key(private_key).address
        maker_addr = self.funder or signer_addr
        return private_key, maker_addr, signer_addr

    async def _build_signed_order(
        self,
        *,
        private_key: str,
        maker_addr: str,
        signer_addr: str,
        token_id: str,
        side: str,
        price: float,
        size: float,
        tick_size: str | float | None,
        fee_rate_bps: int | None,
        expiration: int | None,
        taker: str,
        neg_risk: bool,
        nonce: int | None,
    ) -> dict[str, Any]:
        side = side.upper()

        tick = await self._resolve_tick_size(token_id, tick_size)
        fee_bps = await self._resolve_fee_rate(token_id, fee_rate_bps)

        price_d, size_d, amt_d = self._rounding_for_tick(tick)
        price = float(self._round_normal(price, price_d))

        if side == "BUY":
            taker_amt_raw = self._round_down(float(size), size_d)
            maker_amt_raw = taker_amt_raw * price
            if self._decimal_places(maker_amt_raw) > amt_d:
                tmp = self._round_up(maker_amt_raw, amt_d + 4)
                maker_amt_raw = tmp if self._decimal_places(tmp) <= amt_d else self._round_down(tmp, amt_d)
        elif side == "SELL":
            maker_amt_raw = self._round_down(float(size), size_d)
            taker_amt_raw = maker_amt_raw * price
            if self._decimal_places(taker_amt_raw) > amt_d:
                tmp = self._round_up(taker_amt_raw, amt_d + 4)
                taker_amt_raw = tmp if self._decimal_places(tmp) <= amt_d else self._round_down(tmp, amt_d)
        else:
            raise ValueError("side must be 'BUY' or 'SELL'")

        maker_amount = self._to_token_decimals(maker_amt_raw)
        taker_amount = self._to_token_decimals(taker_amt_raw)

        contract = self._contracts(self.chain_id, neg_risk)
        side_flag = 0 if side == "BUY" else 1
        sig_type = int(self.signature_type)

        return Auth.sign_polymarket_order(
            private_key=private_key,
            chain_id=self.chain_id,
            exchange_address=contract["exchange"],
            order={
                "maker": maker_addr,
                "signer": signer_addr,
                "taker": taker or ZERO_ADDRESS,
                "tokenId": str(token_id),
                "makerAmount": int(maker_amount),
                "takerAmount": int(taker_amount),
                "expiration": int(expiration or 0),
                "nonce": int(nonce or 0),
                "feeRateBps": int(fee_bps or 0),
                "side": side_flag,
                "signatureType": sig_type,
            },
        )

    async def _resolve_tick_size(self, token_id: str, tick_size: str | float | None) -> str:
        if tick_size is not None:
            return str(tick_size)
        tick_resp = await self.get_tick_size(token_id)
        if isinstance(tick_resp, dict):
            return str(tick_resp.get("minimum_tick_size") or tick_resp.get("tick_size") or "0.01")
        return str(tick_resp)

    async def _resolve_fee_rate(self, token_id: str, fee_rate_bps: int | None) -> int:
        if fee_rate_bps is not None:
            return int(fee_rate_bps)
        fee_resp = await self.get_fee_rate(token_id)
        if isinstance(fee_resp, dict):
            return int(fee_resp.get("base_fee", 0))
        return int(fee_resp or 0)

    async def _signed_request_via_session(
        self, method: str, path: str, body: Mapping[str, Any] | list[Any] | None
    ) -> Any:
        import time, base64, hmac, hashlib
        from eth_account import Account as _A
        import aiohttp

        method = method.upper()
        session: aiohttp.ClientSession = getattr(self.client, "_session", None)
        if session is None:
            raise RuntimeError("pybotters client session missing")
        creds = getattr(session, "_polymarket_api_creds", None)
        if not creds:
            raise RuntimeError("Polymarket API creds missing; call create_or_derive_api_creds")
        api_key = creds.get("api_key")
        api_secret = creds.get("api_secret")
        api_passphrase = creds.get("api_passphrase")

        entry = getattr(session, "_apis", {}).get(API_NAME, [])
        private_key = entry[0] if entry else None
        addr = _A.from_key(private_key).address if private_key else None

        ts = int(time.time())
        request_path = path
        url = f"{self.rest_api}{request_path}"
        if isinstance(body, dict):
            payload_obj = dict(body)
        else:
            payload_obj = body
        serialized = (
            str(payload_obj).replace("'", '"') if payload_obj is not None else ""
        )
        secret_bytes = base64.urlsafe_b64decode(api_secret)
        msg = f"{ts}{method}{request_path}{serialized}"
        sig = hmac.new(secret_bytes, msg.encode("utf-8"), hashlib.sha256).digest()
        sign_b64 = base64.urlsafe_b64encode(sig).decode("utf-8")

        headers = {
            "POLY_ADDRESS": addr,
            "POLY_SIGNATURE": sign_b64,
            "POLY_TIMESTAMP": str(ts),
            "POLY_API_KEY": api_key,
            "POLY_PASSPHRASE": api_passphrase,
            "Content-Type": "application/json",
        }

        async with session.request(method, url, headers=headers, data=(serialized or None)) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise RuntimeError(f"Polymarket {method} {path} failed: {resp.status} {text}")
            try:
                return await resp.json()
            except Exception:
                return await resp.text()

    async def post_orders(
        self,
        orders: Iterable[tuple[Mapping[str, Any], str]],
        *,
        owner: str | None = None,
    ) -> Any:
        owner_key = self._owner_key(owner)
        body = [
            {
                "order": dict(order),
                "owner": owner_key,
                "orderType": order_type,
            }
            for order, order_type in orders
        ]
        return await self._signed_request_via_session("POST", "/orders", body)

    async def place_orders(
        self,
        items: Iterable[Mapping[str, Any]],
        *,
        owner: str | None = None,
    ) -> Any:
        """Create, sign and submit multiple orders.

        Each item must include: token_id, side, price, size
        Optional per-item: tick_size, fee_rate_bps, expiration, taker, neg_risk, nonce, order_type
        .. code:: json

            [
                {
                    "errorMsg": "",
                    "orderID": "0x4b9c3ee4dee8653f15f716653e8ac83f0a086a38597e6ec4b72be2389c79b8b4",
                    "takingAmount": "",
                    "makingAmount": "",
                    "status": "live",
                    "success": true
                },
                {
                    "errorMsg": "",
                    "orderID": "0xb3507e9fda9541c3e038afcb4f24b96efcfa667d46cf5e9e52c41620711818df",
                    "takingAmount": "",
                    "makingAmount": "",
                    "status": "live",
                    "success": true
                }
            ]
        """
        private_key, maker_addr, signer_addr = self._get_signing_context()
        owner_key = self._owner_key(owner)

        result_body: list[dict[str, Any]] = []
        for it in items:
            token_id = str(it["token_id"])
            side = str(it["side"]).upper()
            price = float(it["price"])
            size = float(it["size"])
            order_type = str(it.get("order_type", "GTC"))
            tick_size = it.get("tick_size")
            fee_rate_bps = it.get("fee_rate_bps")
            expiration = it.get("expiration")
            taker = it.get("taker", ZERO_ADDRESS)
            neg_risk = bool(it.get("neg_risk", False))
            nonce = it.get("nonce")

            signed = await self._build_signed_order(
                private_key=private_key,
                maker_addr=maker_addr,
                signer_addr=signer_addr,
                token_id=token_id,
                side=side,
                price=price,
                size=size,
                tick_size=tick_size,
                fee_rate_bps=fee_rate_bps,
                expiration=expiration,
                taker=taker,
                neg_risk=neg_risk,
                nonce=nonce,
            )

            result_body.append(
                {
                    "order": signed,
                    "owner": owner_key,
                    "orderType": order_type,
                }
            )

        return await self._signed_request_via_session("POST", "/orders", result_body)

    async def cancel(self, order_id: str) -> Any:
        """
        {'not_canceled': {}, 'canceled': ['0xb3507e9fda9541c3e038afcb4f24b96efcfa667d46cf5e9e52c41620711818df', '0x4b9c3ee4dee8653f15f716653e8ac83f0a086a38597e6ec4b72be2389c79b8b4']}
        """
        return await self._signed_request_via_session("DELETE", "/order", {"orderID": order_id})

    async def cancel_orders(self, order_ids: Sequence[str]) -> Any:
        """
        {'not_canceled': {}, 'canceled': ['0xb3507e9fda9541c3e038afcb4f24b96efcfa667d46cf5e9e52c41620711818df', '0x4b9c3ee4dee8653f15f716653e8ac83f0a086a38597e6ec4b72be2389c79b8b4']}
        """
        return await self._signed_request_via_session("DELETE", "/orders", list(order_ids))

    async def cancel_all(self) -> Any:
        """
        {'not_canceled': {}, 'canceled': ['0xb3507e9fda9541c3e038afcb4f24b96efcfa667d46cf5e9e52c41620711818df', '0x4b9c3ee4dee8653f15f716653e8ac83f0a086a38597e6ec4b72be2389c79b8b4']}
        """
        return await self._signed_request_via_session("DELETE", "/cancel-all", None)

    async def cancel_market_orders(self, market: str = "", asset_id: str = "") -> Any:
        body = {"market": market, "asset_id": asset_id}
        return await self._signed_request_via_session("DELETE", "/cancel-market-orders", body)

    async def get_order(self, order_id: str) -> Any:
        return await self._rest("GET", f"/data/order/{order_id}")

    async def get_orders(self, params: Mapping[str, Any] | None = None) -> list[Any]:
        return await self._paginate("/data/orders", params)

    async def get_trades(self, params: Mapping[str, Any] | None = None) -> list[Any]:
        return await self._paginate("/data/trades", params)

    async def get_notifications(self, signature_type: int | None = None) -> Any:
        sig = signature_type if signature_type is not None else self.signature_type
        query = {"signature_type": str(sig)}
        return await self._rest("GET", "/notifications", params=query)

    async def drop_notifications(self, ids: Sequence[str] | None = None) -> Any:
        params = {"ids": ",".join(ids)} if ids else None
        return await self._rest("DELETE", "/notifications", params=params)

    async def get_balance_allowance(self, **params: Any) -> Any:
        return await self._rest("GET", "/balance-allowance", params=params or None)

    async def update_balance_allowance(self, **params: Any) -> Any:
        return await self._rest("POST", "/balance-allowance/update", json=params or None)

    async def get_usdc(
        self,
        wallet: str = None,
        rpc_urls: Sequence[str] | None = None,
    ) -> float:
        if wallet is None:
            # 找代理钱包, apis['polymarket'][2]
            entry = self._api_entry()
            if not entry or len(entry) < 3 or not entry[2]:
                raise RuntimeError("Polymarket funder wallet address is not configured")
            wallet = entry[2]

        urls = list(rpc_urls or [])
        if not urls:
            urls.extend(DEFAULT_POLYGON_RPCS)

        last_error: Exception | None = None
        for url in urls:
            try:
                balance = await asyncio.to_thread(self._call_usdc_balance, url, wallet)
                return balance
            except Exception as exc:  # pragma: no cover - network failure fallback
                last_error = exc
                continue

        raise RuntimeError("Unable to fetch USDC balance") from last_error

    @staticmethod
    def _call_usdc_balance(rpc_url: str, wallet: str) -> float:
        w3 = _get_web3(rpc_url)
        contract = w3.eth.contract(
            address=w3.to_checksum_address(USDC_CONTRACT),
            abi=ERC20_BALANCE_OF_ABI,
        )
        balance = contract.functions.balanceOf(w3.to_checksum_address(wallet)).call()
        return balance / 10 ** 6

    # ------------------------------------------------------------------
    # Internal utilities

    async def _fetch_event(self, slug: str) -> dict | None:
        resp = await self.client.get(GAMMA_EVENTS_API, params={"slug": slug})
        payload = await resp.json()
        if isinstance(payload, list) and payload:
            return payload[0]
        return None

    async def find_active_market(
        self,
        *,
        base_slug: str = DEFAULT_BASE_SLUG,
        interval: int = DEFAULT_INTERVAL,
        window: int = DEFAULT_WINDOW,
    ) -> tuple[str, dict, dict]:
        
        """
        返回值: slug, event, market
        https://docs.polymarket.com/api-reference/markets/get-market-by-id
        """
    
        now_ts = int(datetime.now(UTC).timestamp())
        base_ts = (now_ts // interval) * interval

        for offset in _iter_offsets(window):
            ts = base_ts + offset * interval
            if ts < 0:
                continue
            slug = f"{base_slug}-{ts}"
            event = await self._fetch_event(slug)
            if not event:
                continue

            def parse_field(value):
                """尝试将字符串 JSON 转为对象，否则原样返回"""
                if isinstance(value, str):
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return value
            
            event = {k: parse_field(v) for k, v in event.items()}

            for market in event.get("markets", []):
                if _accepting_orders(market):
                    market = {k: parse_field(v) for k, v in market.items()}
                    return slug, event, market

        raise RuntimeError(
            f"未在 {base_slug} 的 +/-{window} 个区间内找到可交易的市场"
        )

    async def resolve_active_market_tokens(
        self,
        *,
        base_slug: str = DEFAULT_BASE_SLUG,
        interval: int = DEFAULT_INTERVAL,
        window: int = DEFAULT_WINDOW,
    ) -> tuple[str, dict, dict, list[Any], list[Any]]:
        slug, event, market = await self.find_active_market(
            base_slug=base_slug,
            interval=interval,
            window=window,
        )

        outcomes = _parse_list(market.get("outcomes"))
        token_ids = _parse_list(market.get("clobTokenIds"))

        if not outcomes or not token_ids:
            raise RuntimeError("market 数据缺少 outcomes 或 clobTokenIds 字段")
        if len(outcomes) != len(token_ids):
            raise RuntimeError("outcomes 与 clobTokenIds 数量不匹配")

        return slug, event, market, outcomes, token_ids

    async def _rest(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        host: str | None = None,
    ) -> Any:
        
        url = f"{host}{path}" if host else f"{self.rest_api}{path}"
        request_kwargs: dict[str, Any] = {}
        if params:
            request_kwargs["params"] = {k: v for k, v in params.items() if v is not None}
        if json is not None:
            request_kwargs["json"] = json

        requester = getattr(self.client, method.lower())
        resp = await requester(url, **request_kwargs)
        if resp.status >= 400:
            text = await resp.text()
            raise RuntimeError(f"Polymarket {method} {path} failed: {resp.status} {text}")
        if resp.content_length == 0:
            return None
        return await resp.json()

    async def _paginate(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
    ) -> list[Any]:
        filters = {k: v for k, v in (params or {}).items() if v is not None}
        cursor = "MA=="
        results: list[Any] = []
        while cursor != END_CURSOR:
            query = dict(filters)
            if cursor:
                query["next_cursor"] = cursor
            payload = await self._rest("GET", path, params=query or None)
            cursor = payload.get("next_cursor", END_CURSOR)
            results.extend(payload.get("data", []))
        return results

    def _token_list(self, token_ids: Sequence[str] | str) -> list[str]:
        if isinstance(token_ids, str):
            tokens = [token_ids]
        else:
            tokens = list(token_ids)
        tokens = [tid for tid in tokens if tid]
        if not tokens:
            raise ValueError("token_ids must not be empty")
        return tokens

    def _owner_key(self, owner: str | None = None) -> str:
        if owner:
            return owner
        creds = self._api_creds()
        api_key = creds.get("api_key") if creds else None
        if not api_key:
            raise RuntimeError("Polymarket API key missing; call create_or_derive_api_creds first")
        return api_key

    def _api_entry(self) -> list[Any] | None:
        session = getattr(self.client, "_session", None)
        if session is None:
            return None
        apis = getattr(session, "_apis", None) or session.__dict__.get("_apis")
        if apis is None:
            return None
        return apis.get(API_NAME)

    def _api_creds(self) -> dict[str, Any] | None:
        session = getattr(self.client, "_session", None)
        if session is None:
            return None
        return getattr(session, "_polymarket_api_creds", None)

    def _store_api_creds(self, data: Mapping[str, Any]) -> None:
        session = getattr(self.client, "_session", None)
        if session is None:
            raise RuntimeError("pybotters Client session not initialized for Polymarket creds")
        creds = {
            "api_key": data.get("apiKey") or data.get("api_key"),
            "api_secret": data.get("secret") or data.get("api_secret"),
            "api_passphrase": data.get("passphrase") or data.get("api_passphrase"),
        }
        if not creds["api_key"] or not creds["api_secret"] or not creds["api_passphrase"]:
            raise RuntimeError("Polymarket API creds response missing key/secret/passphrase")
        session.__dict__["_polymarket_api_creds"] = creds
        apis = session.__dict__.get("_apis")
        if isinstance(apis, dict):
            entry = list(apis.get(API_NAME, []))
            while len(entry) < 7:
                entry.append("")
            entry[4] = creds["api_key"]
            entry[5] = creds["api_secret"]
            entry[6] = creds["api_passphrase"]
            apis[API_NAME] = entry

    def _ensure_session_entry(
        self,
        *,
        private_key: str | None,
        funder: str | None,
    ) -> None:
        session = getattr(self.client, "_session", None)
        if session is None:
            raise RuntimeError("pybotters.Client session not initialized")
        apis = getattr(session, "_apis", None)
        if apis is None:
            raise RuntimeError("pybotters Client missing _apis; load apis.json when creating the client")

        entry = list(apis.get(API_NAME, []))
        if not entry and not private_key:
            raise RuntimeError(
                "Polymarket credentials not found in apis.json; please add your private key"
            )

        while len(entry) < 3:
            entry.append("")

        existing_pk = entry[0]
        normalized_pk: str | None = None
        if private_key:
            normalized_pk = (
                private_key if private_key.startswith("0x") else f"0x{private_key}"
            )
        elif existing_pk:
            normalized_pk = (
                existing_pk if existing_pk.startswith("0x") else f"0x{existing_pk}"
            )

        if not normalized_pk:
            raise RuntimeError("Polymarket需要钱包私钥 (apis['polymarket'][0])")

        entry[0] = normalized_pk
        if funder:
            entry[2] = funder
        self.funder = entry[2] or self.funder

        apis[API_NAME] = entry
        session.__dict__["_apis"] = apis
        session.__dict__["_polymarket_chain_id"] = self.chain_id
        session.__dict__["_polymarket_signature_type"] = self.signature_type

@lru_cache(maxsize=8)
def _get_web3(rpc_url: str):
    from web3 import Web3

    provider = Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10})
    w3 = Web3(provider)
    if not w3.is_connected():
        raise RuntimeError(f"Failed to connect Polygon RPC: {rpc_url}")
    return w3
