from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Iterable

from pybotters.store import DataStore, DataStoreCollection
from pybotters.ws import ClientWebSocketResponse

if TYPE_CHECKING:
    from pybotters.typedefs import Item

   
class Position(DataStore):
    """Position DataStore keyed by Polymarket token id."""

    _KEYS = ["asset", "outcome"]

    def _on_response(self, msg: Item) -> None:
        self._update(msg)


class Fill(DataStore):
    """Fill records keyed by maker order id."""

    _KEYS = ["order_id"]

    @staticmethod
    def _from_trade(trade: dict[str, Any], maker: dict[str, Any]) -> dict[str, Any] | None:
        order_id = maker.get("order_id")
        if not order_id:
            return None

        record = {
            "order_id": order_id,
            "trade_id": trade.get("id"),
            "asset_id": maker.get("asset_id") or trade.get("asset_id"),
            "market": trade.get("market"),
            "outcome": maker.get("outcome") or trade.get("outcome"),
            "matched_amount": maker.get("matched_amount") or trade.get("size"),
            "price": maker.get("price") or trade.get("price"),
            "status": trade.get("status"),
            "match_time": trade.get("match_time") or trade.get("timestamp"),
            "maker_owner": maker.get("owner"),
            "taker_order_id": trade.get("taker_order_id"),
            "side": maker.get("side") or trade.get("side"),
        }

        for key in ("matched_amount", "price"):
            value = record.get(key)
            if value is None:
                continue
            try:
                record[key] = float(value)
            except (TypeError, ValueError):
                pass

        return record

    def _on_trade(self, trade: dict[str, Any]) -> None:
        status = str(trade.get("status") or "").upper()
        if status != "MATCHED":
            return
        maker_orders = trade.get("maker_orders") or []
        upserts: list[dict[str, Any]] = []
        for maker in maker_orders:
            record = self._from_trade(trade, maker)
            if not record:
                continue
            upserts.append(record)

        if not upserts:
            return

        for record in upserts:
            key = {"order_id": record["order_id"]}
            if self.get(key):
                self._update([record])
            else:
                self._insert([record])


class Order(DataStore):
    """User orders keyed by order id (REST + WS)."""

    _KEYS = ["id"]

    @staticmethod
    def _normalize(entry: dict[str, Any]) -> dict[str, Any] | None:
        oid = entry.get("id")
        if not oid:
            return None
        normalized = dict(entry)
        # numeric fields
        for field in ("price", "original_size", "size_matched"):
            val = normalized.get(field)
            try:
                if val is not None:
                    normalized[field] = float(val)
            except (TypeError, ValueError):
                pass
        return normalized

    def _on_response(self, items: list[dict[str, Any]] | dict[str, Any]) -> None:
        rows: list[dict[str, Any]] = []
        if isinstance(items, dict):
            items = [items]
        for it in items or []:
            norm = self._normalize(it)
            if norm:
                rows.append(norm)
        self._clear()
        if rows:
            self._insert(rows)

    def _on_message(self, msg: dict[str, Any]) -> None:
        norm = self._normalize(msg)
        if not norm:
            return
        key = {"id": norm["id"]}
        if self.get(key):
            self._update([norm])
        else:
            self._insert([norm])


class Trade(DataStore):
    """User trades keyed by trade id."""

    _KEYS = ["id"]

    @staticmethod
    def _normalize(entry: dict[str, Any]) -> dict[str, Any] | None:
        trade_id = entry.get("id")
        if not trade_id:
            return None
        normalized = dict(entry)
        for field in ("price", "size", "fee_rate_bps"):
            value = normalized.get(field)
            if value is None:
                continue
            try:
                normalized[field] = float(value)
            except (TypeError, ValueError):
                pass
        return normalized

    def _on_message(self, msg: dict[str, Any]) -> None:
        normalized = self._normalize(msg) or {}
        trade_id = normalized.get("id")
        if not trade_id:
            return
        if self.get({"id": trade_id}):
            self._update([normalized])
        else:
            self._insert([normalized])


class Book(DataStore):
    """Full depth order book keyed by Polymarket token id."""

    _KEYS = ["s", "S", "p"]

    def _init(self) -> None:
        self.id_to_alias: dict[str, str] = {}

    def update_aliases(self, mapping: dict[str, str]) -> None:
        if not mapping:
            return
        self.id_to_alias.update(mapping)

    def _alias(self, asset_id: str | None) -> tuple[str, str | None] | tuple[None, None]:
        if asset_id is None:
            return None, None
        alias = self.id_to_alias.get(asset_id)
        return asset_id, alias

    def _normalize_levels(
        self,
        entries: Iterable[dict[str, Any]] | None,
        *,
        side: str,
        symbol: str,
        alias: str | None,
    ) -> list[dict[str, Any]]:
        if not entries:
            return []
        normalized: list[dict[str, Any]] = []
        for entry in entries:
            try:
                price = float(entry["price"])
                size = float(entry["size"])
            except (KeyError, TypeError, ValueError):
                continue
            record = {"s": symbol, "S": side, "p": price, "q": size}
            if alias is not None:
                record["alias"] = alias
            normalized.append(record)
        return normalized

    def _on_message(self, msg: dict[str, Any]) -> None:
        msg_type = msg.get("event_type")
        if msg_type not in {"book", "price_change"}:
            return

        asset_id = msg.get("asset_id") or msg.get("token_id")
        symbol, alias = self._alias(asset_id)
        if symbol is None:
            return

        if msg_type == "book":
            bids = self._normalize_levels(msg.get("bids"), side="b", symbol=symbol, alias=alias)
            asks = self._normalize_levels(msg.get("asks"), side="a", symbol=symbol, alias=alias)
            if bids:
                self._insert(bids)
            if asks:
                self._insert(asks)
            return

        price_changes = msg.get("price_changes") or []
        updates: list[dict[str, Any]] = []
        removals: list[dict[str, Any]] = []
        for change in price_changes:
            side = "b" if change.get("side") == "BUY" else "a"
            try:
                price = float(change["price"])
                size = float(change["size"])
            except (KeyError, TypeError, ValueError):
                continue
            record = {"s": symbol, "S": side, "p": price}
            if alias is not None:
                record["alias"] = alias
            if size == 0:
                removals.append({"s": symbol, "S": side, "p": price})
            else:
                record["q"] = size
                updates.append(record)

        if removals:
            self._delete(removals)
        if updates:
            self._update(updates)

    def sorted(
        self, query: Item | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="S",
            item_asc_key="a",
            item_desc_key="b",
            sort_key="p",
            query=query,
            limit=limit,
        )


class Detail(DataStore):
    """Market metadata keyed by Polymarket token id."""

    _KEYS = ["token_id"]

    @staticmethod
    def _normalize_entry(market: dict[str, Any], token: dict[str, Any]) -> dict[str, Any]:
        slug = market.get("market_slug") or market.get("question") or market.get("id")
        outcome = token.get("outcome")
        alias = slug if outcome is None else f"{slug}:{outcome}"

        tick_size = (
            market.get("minimum_tick_size")
            or market.get("orderPriceMinTickSize")
            or market.get("order_price_min_tick_size")
        )
        step_size = (
            market.get("minimum_order_size")
            or market.get("orderMinSize")
            or market.get("order_min_size")
        )

        try:
            tick_size = float(tick_size) if tick_size is not None else None
        except (TypeError, ValueError):
            tick_size = None
        try:
            step_size = float(step_size) if step_size is not None else None
        except (TypeError, ValueError):
            step_size = None

        return {
            "token_id": token.get("token_id") or token.get("id"),
            "asset_id": token.get("token_id") or token.get("id"),
            "alias": alias,
            "question": market.get("question"),
            "outcome": outcome,
            "active": market.get("active"),
            "closed": market.get("closed"),
            "neg_risk": market.get("neg_risk"),
            "tick_size": tick_size if tick_size is not None else 0.01,
            "step_size": step_size if step_size is not None else 1.0,
            "minimum_order_size": step_size if step_size is not None else 1.0,
            "minimum_tick_size": tick_size if tick_size is not None else 0.01,
        }

    def on_response(self, markets: Iterable[dict[str, Any]]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        records: list[dict[str, Any]] = []
        for market in markets or []:
            tokens = market.get("tokens") or []
            if not tokens:
                token_ids = market.get("clobTokenIds") or []
                outcomes = market.get("outcomes") or []

                if isinstance(token_ids, str):
                    try:
                        token_ids = json.loads(token_ids)
                    except json.JSONDecodeError:
                        token_ids = [token_ids]
                if isinstance(outcomes, str):
                    try:
                        outcomes = json.loads(outcomes)
                    except json.JSONDecodeError:
                        outcomes = [outcomes]

                if not isinstance(token_ids, list):
                    token_ids = [token_ids]
                if not isinstance(outcomes, list):
                    outcomes = [outcomes]

                tokens = [
                    {"token_id": tid, "outcome": outcomes[idx] if idx < len(outcomes) else None}
                    for idx, tid in enumerate(token_ids)
                    if tid
                ]

            for token in tokens:
                normalized = self._normalize_entry(market, token)
                # Add or update additional fields from market
                normalized.update({
                    "condition_id": market.get("conditionId"),
                    "slug": market.get("slug"),
                    "end_date": market.get("endDate"),
                    "start_date": market.get("startDate"),
                    "icon": market.get("icon"),
                    "image": market.get("image"),
                    "liquidity": market.get("liquidityNum") or market.get("liquidity"),
                    "volume": market.get("volumeNum") or market.get("volume"),
                    "accepting_orders": market.get("acceptingOrders"),
                    "spread": market.get("spread"),
                    "best_bid": market.get("bestBid"),
                    "best_ask": market.get("bestAsk"),
                })
                token_id = normalized.get("token_id")
                if not token_id:
                    continue
                records.append(normalized)
                mapping[token_id] = normalized.get("alias") or token_id

        self._update(records)
        return mapping


class PolymarketDataStore(DataStoreCollection):
    """Polymarket-specific DataStore aggregate."""

    def _init(self) -> None:
        self._create("book", datastore_class=Book)
        self._create("detail", datastore_class=Detail)
        self._create("position", datastore_class=Position)
        self._create("order", datastore_class=Order)
        self._create("trade", datastore_class=Trade)
        self._create("fill", datastore_class=Fill)

    @property
    def book(self) -> Book:
        """Order Book DataStore
        _key: k (asset_id), S (side), p (price)

        .. code:: json
            [{
                "k": "asset_id",
                "S": "b" | "a",
                "p": "price",
                "q": "size"
            }]
        """
        return self._get("book")

    @property
    def detail(self) -> Detail:
        """
        Market metadata keyed by token id.

        .. code:: json
            
            [
                {
                    "token_id": "14992165475527298486519422865149275159537493330633013685269145597531945526992",
                    "asset_id": "14992165475527298486519422865149275159537493330633013685269145597531945526992",
                    "alias": "Bitcoin Up or Down - November 12, 12:30AM-12:45AM ET:Down",
                    "question": "Bitcoin Up or Down - November 12, 12:30AM-12:45AM ET",
                    "outcome": "Down",
                    "active": true,
                    "closed": false,
                    "neg_risk": null,
                    "tick_size": 0.01,
                    "step_size": 5.0,
                    "minimum_order_size": 5.0,
                    "minimum_tick_size": 0.01,
                    "condition_id": "0xb64133e5ae9710fab2533cfd3c48cba142347e4bab36822964ca4cca4b7660d2",
                    "slug": "btc-updown-15m-1762925400",
                    "end_date": "2025-11-12T05:45:00Z",
                    "start_date": "2025-11-11T05:32:59.491174Z",
                    "icon": "https://polymarket-upload.s3.us-east-2.amazonaws.com/BTC+fullsize.png",
                    "image": "https://polymarket-upload.s3.us-east-2.amazonaws.com/BTC+fullsize.png",
                    "liquidity": 59948.1793,
                    "volume": 12214.600385,
                    "accepting_orders": true,
                    "spread": 0.01,
                    "best_bid": 0.5,
                    "best_ask": 0.51
                }
            ]
        """

        return self._get("detail")
    
    @property
    def position(self) -> Position:
        """

        .. code:: python
        
            [{
                # 🔑 基础信息
                "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",  # 代理钱包地址（用于代表用户在链上的交易地址）
                "asset": "<string>",                                          # outcome token 资产地址或 symbol
                "conditionId": "0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917",  # 市场条件 ID（event 的唯一标识）
                
                # 💰 交易与价格信息
                "size": 123,             # 当前持仓数量（仅在未平仓时存在）
                "avgPrice": 123,         # 平均买入价（每个 outcome token 的均价）
                "curPrice": 123,         # 当前市场价格
                "initialValue": 123,     # 初始建仓总价值（avgPrice × size）
                "currentValue": 123,     # 当前持仓市值（curPrice × size）

                # 📊 盈亏指标
                "cashPnl": 123,             # 未实现盈亏（当前浮动盈亏）
                "percentPnl": 123,          # 未实现盈亏百分比
                "realizedPnl": 123,         # 已实现盈亏（平仓后的实际收益）
                "percentRealizedPnl": 123,  # 已实现盈亏百分比（相对成本的收益率）

                # 🧮 累计交易信息
                "totalBought": 123,  # 累计买入数量（含历史）
                
                # ⚙️ 状态标志
                "redeemable": True,   # 是否可赎回（True 表示市场已结算且你是赢家，可提取 USDC）
                "mergeable": True,    # 是否可合并（多笔相同 outcome 可合并为一笔）
                "negativeRisk": True, # 是否为负风险组合（风险对冲导致净敞口为负）
                
                # 🧠 市场元数据
                "title": "<string>",          # 市场标题（如 “Bitcoin up or down 15m”）
                "slug": "<string>",           # outcome 唯一 slug（对应前端页面路径的一部分）
                "eventSlug": "<string>",      # event slug（整个预测事件的唯一路径标识）
                "icon": "<string>",           # 图标 URL（一般为事件关联资产）
                "outcome": "<string>",        # 当前持有的 outcome 名称（例如 “Yes” 或 “No”）
                "outcomeIndex": 123,          # outcome 在该市场中的索引（0 或 1）
                "oppositeOutcome": "<string>",# 对立 outcome 名称
                "oppositeAsset": "<string>",  # 对立 outcome token 地址
                "endDate": "<string>",        # 市场结束时间（UTC ISO 格式字符串）
            }]
        """

        return self._get("position")

    @property
    def orders(self) -> Order:
        """User orders keyed by order id.

        Example row (from REST get_orders):

        .. code:: json
            {
              "id": "0xd4359d…",
              "status": "LIVE",
              "owner": "<api-key>",
              "maker_address": "0x…",
              "market": "0x…",
              "asset_id": "317234…",
              "side": "BUY",
              "original_size": 5.0,
              "size_matched": 0.0,
              "price": 0.02,
              "outcome": "Up",
              "order_type": "GTC",
              "created_at": 1762912331
            }
        """

        return self._get("order")

    @property
    def trade(self) -> Trade:
        """User trade stream keyed by trade id.

        Columns include Polymarket websocket ``trade`` payloads, e.g.

        .. code:: json
            {
                "event_type": "trade",
                "id": "28c4d2eb-bbea-40e7-a9f0-b2fdb56b2c2e",
                "market": "0xbd31…",
                "asset_id": "521143…",
                "side": "BUY",
                "price": 0.57,
                "size": 10,
                "status": "MATCHED",
                "maker_orders": [ ... ]
            }
        """

        return self._get("trade")

    @property
    def fill(self) -> Fill:
        """Maker-order fills keyed by ``order_id``.

        A row is created whenever a trade arrives with ``status == 'MATCHED'``.
        ``matched_amount`` and ``price`` are stored as floats for quick PnL math.

        .. code:: json
            {
                "order_id": "0xb46574626be7eb57a8fa643eac5623bdb2ec42104e2dc3441576a6ed8d0cc0ed",
                "owner": "1aa9c6be-02d2-c021-c5fc-0c5b64ba8fd6",
                "maker_address": "0x64A46A989363eb21DAB87CD53d57A4567Ccbc103",
                "matched_amount": "1.35",
                "price": "0.73",
                "fee_rate_bps": "0",
                "asset_id": "60833383978754019365794467018212448484210363665632025956221025028271757152271",
                "outcome": "Up",
                "outcome_index": 0,
                "side": "BUY"
            }
        """

        return self._get("fill")

    def onmessage(self, msg: Any, ws: ClientWebSocketResponse | None = None) -> None:
        # 判定msg是否为list
        lst_msg = msg if isinstance(msg, list) else [msg]
        for m in lst_msg:
            raw_type = m.get("event_type") or m.get("type")
            if not raw_type:
                continue
            msg_type = str(raw_type).lower()
            if msg_type in {"book", "price_change"}:
                self.book._on_message(m)
            elif msg_type == "order":
                self.order._on_message(m)
            elif msg_type == "trade":
                self.trade._on_message(m)
                self.fill._on_trade(m)
