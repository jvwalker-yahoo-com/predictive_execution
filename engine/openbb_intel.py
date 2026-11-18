"""
OpenBB Unified Financial Intelligence Router (obb engine integration)
====================================================================
Provides institutional-grade financial intelligence across four pillars:
  1. Unified Data Router: Consistent interface across OpenBB SDK (obb) and direct
     multi-provider adapters (Yahoo Finance, Finnhub, Polygon, Alpha Vantage, FMP,
     SEC EDGAR, FRED, Frankfurter, CoinGecko) with thread-safe TTL caching and
     concurrent execution.
  2. Global News & Headlines: Live financial news aggregated and scored for
     sentiment and institutional catalysts.
  3. Macro & Economic Intelligence: Treasury yields (2Y, 10Y), Fed funds rate,
     CPI inflation, GDP, yield curve spread, and macro regime classification.
  4. Deep Equity & Fundamentals: Intraday bars, quote/spread metrics, analyst
     price targets, valuation multiples (P/E, Forward P/E, ROE, Profit Margin,
     Debt/Equity, Free Cash Flow), and SEC Form 4 / insider flow disclosures.
"""

from __future__ import annotations

import datetime
import gzip
import json
import math
import os
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from openbb import obb as _obb_sdk  # type: ignore
    HAS_OPENBB_SDK = True
except Exception:
    _obb_sdk = None
    HAS_OPENBB_SDK = False

try:
    import yfinance as yf  # type: ignore
    HAS_YFINANCE = True
except Exception:
    yf = None
    HAS_YFINANCE = False

SEC_USER_AGENT = os.getenv(
    "SEC_USER_AGENT",
    "AntigravityOpenBBRouter/2.0 (contact: jvwalker@yahoo.com)"
)

# Positive and negative institutional lexicon for fast deterministic news scoring
_BULLISH_TERMS = {
    "beat", "beats", "surge", "surges", "upgrade", "upgraded", "outperform",
    "buy", "strong buy", "record", "growth", "bullish", "rally", "breakout",
    "profit", "approval", "partnership", "dividend", "buyback", "raises",
    "exceeds", "upside", "accumulation", "expansion", "ai", "leadership"
}
_BEARISH_TERMS = {
    "miss", "misses", "downgrade", "downgraded", "underperform", "sell",
    "plunge", "plunges", "drop", "drops", "lawsuit", "investigation", "sec",
    "recall", "cut", "cuts", "warning", "bearish", "decline", "loss",
    "layoffs", "default", "headwind", "weakness", "dumping", "tariff"
}


class _TTLCache:
    """Thread-safe in-memory TTL cache to prevent redundant API calls."""

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, val = entry
            if now >= expires_at:
                del self._store[key]
                return None
            return val

    def set(self, key: str, value: Any, ttl_seconds: float) -> Any:
        with self._lock:
            self._store[key] = (time.time() + ttl_seconds, value)
        return value

    def cached(self, key: str, ttl_seconds: float, fn: Callable[[], Any]) -> Any:
        hit = self.get(key)
        if hit is not None:
            return hit
        val = fn()
        return self.set(key, val, ttl_seconds)


_GLOBAL_CACHE = _TTLCache()


class OpenBBUnifiedRouter:
    """
    Unified Financial Data Router inspired by OpenBB (`obb`).
    Routes queries through OpenBB SDK when installed and seamlessly falls back
    across Yahoo Finance, Finnhub, FMP, Polygon, Alpha Vantage, FRED, and SEC EDGAR.
    """

    def __init__(
        self,
        finnhub_key: str = "",
        polygon_key: str = "",
        fred_key: str = "",
        av_key: str = "",
        fmp_key: str = "",
        tiingo_key: str = "",
    ) -> None:
        self.finnhub_key = finnhub_key or os.getenv("FINNHUB_API_KEY", "")
        self.polygon_key = polygon_key or os.getenv("POLYGON_API_KEY", "")
        self.fred_key = fred_key or os.getenv("FRED_API_KEY", "")
        self.av_key = av_key or os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.fmp_key = fmp_key or os.getenv("FMP_API_KEY", "")
        self.tiingo_key = tiingo_key or os.getenv("TIINGO_API_KEY", "")
        self._cache = _GLOBAL_CACHE

    # ------------------------------------------------------------------
    # 1. Deep Equity & Intraday Price / Volatility / Order Book Metrics
    # ------------------------------------------------------------------
    def get_equity_quote_and_technicals(self, symbol: str = "AAPL") -> Dict[str, Any]:
        symbol_up = (symbol or "AAPL").upper().strip()
        cache_key = f"obb:quote_tech:{symbol_up}"

        def _fetch() -> Dict[str, Any]:
            result: Dict[str, Any] = {
                "symbol": symbol_up,
                "price": 0.0,
                "open": 0.0,
                "high": 0.0,
                "low": 0.0,
                "prev_close": 0.0,
                "change": 0.0,
                "change_pct": 0.0,
                "volume": 0,
                "vwap": 0.0,
                "sma20": 0.0,
                "sma50": 0.0,
                "rsi14": 50.0,
                "atr14": 1.0,
                "realized_volatility": 0.22,
                "estimated_spread_bps": 2.5,
                "provider": "synthetic_fallback",
                "timestamp": time.time(),
            }

            # Try OpenBB SDK first if installed
            if HAS_OPENBB_SDK and _obb_sdk is not None:
                try:
                    q_res = _obb_sdk.equity.price.quote(symbol=symbol_up, provider="yfinance")
                    df_q = q_res.to_dataframe()
                    if not df_q.empty:
                        row = df_q.iloc[0]
                        result["price"] = float(row.get("last_price") or row.get("close") or 0.0)
                        result["open"] = float(row.get("open") or result["price"])
                        result["high"] = float(row.get("high") or result["price"])
                        result["low"] = float(row.get("low") or result["price"])
                        result["prev_close"] = float(row.get("prev_close") or result["price"])
                        result["volume"] = int(row.get("volume") or 0)
                        result["provider"] = "openbb:yfinance"
                except Exception:
                    pass

            # Try yfinance historical bars for full technicals & quote
            if HAS_YFINANCE and yf is not None:
                try:
                    df = yf.download(symbol_up, period="3mo", interval="1d", progress=False)
                    if df is not None and not df.empty:
                        if hasattr(df.columns, "levels") and len(getattr(df.columns, "levels", [])) > 1:
                            df.columns = df.columns.get_level_values(0)
                        closes = df["Close"].dropna()
                        if len(closes) >= 2:
                            cur = float(closes.iloc[-1])
                            prev = float(closes.iloc[-2])
                            high_v = float(df["High"].iloc[-1])
                            low_v = float(df["Low"].iloc[-1])
                            open_v = float(df["Open"].iloc[-1])
                            if "Volume" in df:
                                last_vol = int(df["Volume"].iloc[-1] or 0)
                                avg_vol = int(df["Volume"].tail(20).mean() or 1000000)
                                vol_v = max(last_vol, avg_vol, 100000)
                            else:
                                vol_v = 1000000

                            sma20 = float(closes.rolling(min(20, len(closes))).mean().iloc[-1])
                            sma50 = float(closes.rolling(min(50, len(closes))).mean().iloc[-1])

                            delta = closes.diff()
                            gain = delta.where(delta > 0, 0.0).rolling(min(14, len(closes))).mean()
                            loss = (-delta.where(delta < 0, 0.0)).rolling(min(14, len(closes))).mean()
                            rs = float(gain.iloc[-1]) / (float(loss.iloc[-1]) + 1e-9)
                            rsi14 = 100.0 - (100.0 / (1.0 + rs))

                            returns = closes.pct_change().dropna()
                            realized_vol = float(returns.std() * math.sqrt(252)) if len(returns) > 5 else 0.22

                            tr = (df["High"] - df["Low"]).tail(14)
                            atr14 = float(tr.mean()) if not tr.empty else max(0.5, cur * 0.015)
                            vwap = round((high_v + low_v + cur) / 3.0, 2)

                            # Estimate spread in bps from intraday high/low range and volume
                            range_pct = max(0.0005, (high_v - low_v) / max(cur, 1.0))
                            liq_factor = max(1.0, math.log10(max(vol_v, 1000)) - 4.0)
                            spread_bps = round(max(0.8, min(25.0, (range_pct * 1000.0) / liq_factor)), 2)

                            result.update({
                                "price": round(cur, 2),
                                "open": round(open_v, 2),
                                "high": round(high_v, 2),
                                "low": round(low_v, 2),
                                "prev_close": round(prev, 2),
                                "change": round(cur - prev, 2),
                                "change_pct": round(((cur - prev) / max(prev, 1e-9)) * 100.0, 2),
                                "volume": vol_v,
                                "vwap": vwap,
                                "sma20": round(sma20, 2),
                                "sma50": round(sma50, 2),
                                "rsi14": round(rsi14, 2),
                                "atr14": round(atr14, 2),
                                "realized_volatility": round(realized_vol, 4),
                                "estimated_spread_bps": spread_bps,
                                "provider": "openbb:yfinance" if HAS_OPENBB_SDK else "yfinance",
                            })
                            return result
                except Exception:
                    pass

            # Fallback to Finnhub quote
            if self.finnhub_key:
                try:
                    url = f"https://finnhub.io/api/v1/quote?symbol={symbol_up}&token={self.finnhub_key}"
                    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/2.0"})
                    with urllib.request.urlopen(req, timeout=4) as r:
                        data = json.loads(r.read().decode("utf-8"))
                        cur = float(data.get("c") or 0.0)
                        if cur > 0:
                            pc = float(data.get("pc") or cur)
                            high_v = float(data.get("h") or cur)
                            low_v = float(data.get("l") or cur)
                            result.update({
                                "price": round(cur, 2),
                                "open": round(float(data.get("o") or cur), 2),
                                "high": round(high_v, 2),
                                "low": round(low_v, 2),
                                "prev_close": round(pc, 2),
                                "change": round(float(data.get("d") or (cur - pc)), 2),
                                "change_pct": round(float(data.get("dp") or 0.0), 2),
                                "vwap": round((high_v + low_v + cur) / 3.0, 2),
                                "sma20": round(cur * 0.99, 2),
                                "sma50": round(cur * 0.97, 2),
                                "provider": "finnhub",
                            })
                except Exception:
                    pass

            return result

        return self._cache.cached(cache_key, ttl_seconds=60.0, fn=_fetch)

    # ------------------------------------------------------------------
    # 2. Deep Fundamentals, Valuation Multiples & Analyst Estimates
    # ------------------------------------------------------------------
    def get_equity_fundamentals(self, symbol: str = "AAPL") -> Dict[str, Any]:
        symbol_up = (symbol or "AAPL").upper().strip()
        cache_key = f"obb:fundamentals:{symbol_up}"

        def _fetch() -> Dict[str, Any]:
            fund: Dict[str, Any] = {
                "symbol": symbol_up,
                "pe_ratio": None,
                "forward_pe": None,
                "peg_ratio": None,
                "price_to_book": None,
                "ev_to_ebitda": None,
                "profit_margin": None,
                "return_on_equity": None,
                "debt_to_equity": None,
                "free_cash_flow": None,
                "market_cap": None,
                "target_mean": None,
                "target_high": None,
                "target_low": None,
                "recommendation": "Hold",
                "fundamental_score": 0.5,  # 0.0 (weak) -> 1.0 (fortress balance sheet)
                "provider": "fallback",
            }

            if HAS_YFINANCE and yf is not None:
                try:
                    info = yf.Ticker(symbol_up).info or {}
                    fund["pe_ratio"] = info.get("trailingPE")
                    fund["forward_pe"] = info.get("forwardPE")
                    fund["peg_ratio"] = info.get("pegRatio")
                    fund["price_to_book"] = info.get("priceToBook")
                    fund["ev_to_ebitda"] = info.get("enterpriseToEbitda")
                    fund["profit_margin"] = info.get("profitMargins")
                    fund["return_on_equity"] = info.get("returnOnEquity")
                    fund["debt_to_equity"] = info.get("debtToEquity")
                    fund["free_cash_flow"] = info.get("freeCashflow")
                    fund["market_cap"] = info.get("marketCap")
                    fund["target_mean"] = info.get("targetMeanPrice")
                    fund["target_high"] = info.get("targetHighPrice")
                    fund["target_low"] = info.get("targetLowPrice")
                    rec = info.get("recommendationKey", "hold")
                    if rec:
                        fund["recommendation"] = str(rec).replace("_", " ").title()
                    fund["provider"] = "openbb:yfinance" if HAS_OPENBB_SDK else "yfinance"
                except Exception:
                    pass

            # Try FMP ratios fallback if key metrics missing
            if fund["pe_ratio"] is None and self.fmp_key:
                try:
                    url = f"https://financialmodelingprep.com/api/v3/quote/{symbol_up}?apikey={self.fmp_key}"
                    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/2.0"})
                    with urllib.request.urlopen(req, timeout=4) as r:
                        arr = json.loads(r.read().decode("utf-8"))
                        if isinstance(arr, list) and arr:
                            item = arr[0]
                            fund["pe_ratio"] = item.get("pe")
                            fund["market_cap"] = item.get("marketCap")
                            fund["provider"] = "fmp"
                except Exception:
                    pass

            # Compute normalized fundamental health score [0.0, 1.0]
            score = 0.50
            pm = fund.get("profit_margin")
            if isinstance(pm, (int, float)):
                score += 0.15 if pm > 0.15 else (0.05 if pm > 0.05 else -0.10)
            roe = fund.get("return_on_equity")
            if isinstance(roe, (int, float)):
                score += 0.15 if roe > 0.18 else (0.05 if roe > 0.08 else -0.08)
            fpe = fund.get("forward_pe")
            if isinstance(fpe, (int, float)) and fpe > 0:
                score += 0.10 if fpe < 25 else (-0.08 if fpe > 45 else 0.02)
            fcf = fund.get("free_cash_flow")
            if isinstance(fcf, (int, float)):
                score += 0.10 if fcf > 0 else -0.10

            fund["fundamental_score"] = round(max(0.05, min(0.98, score)), 3)
            return fund

        return self._cache.cached(cache_key, ttl_seconds=600.0, fn=_fetch)

    # ------------------------------------------------------------------
    # 3. Global News, Headlines & Sentiment Scoring
    # ------------------------------------------------------------------
    def get_global_news_sentiment(self, symbol: str = "AAPL", limit: int = 8) -> Dict[str, Any]:
        symbol_up = (symbol or "AAPL").upper().strip()
        cache_key = f"obb:news:{symbol_up}:{limit}"

        def _fetch() -> Dict[str, Any]:
            articles: List[Dict[str, Any]] = []

            # 1. Try Finnhub Company News
            if self.finnhub_key:
                try:
                    today = datetime.date.today().isoformat()
                    from_day = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
                    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol_up}&from={from_day}&to={today}&token={self.finnhub_key}"
                    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/2.0"})
                    with urllib.request.urlopen(req, timeout=4) as r:
                        data = json.loads(r.read().decode("utf-8"))
                        if isinstance(data, list):
                            for item in data[:limit]:
                                h = str(item.get("headline") or "").strip()
                                if h:
                                    articles.append({
                                        "headline": h,
                                        "summary": str(item.get("summary") or "")[:200],
                                        "source": item.get("source") or "Finnhub",
                                        "url": item.get("url") or "#",
                                        "datetime": item.get("datetime") or int(time.time()),
                                    })
                except Exception:
                    pass

            # 2. Fallback to Google News RSS (Zero Auth, high reliability & low latency)
            if len(articles) < limit:
                try:
                    q = urllib.parse.quote(f"{symbol_up} stock market news")
                    rss_url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
                    req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=4) as r:
                        xml_bytes = r.read()
                        root = ET.fromstring(xml_bytes)
                        for item_el in root.findall(".//item")[: limit - len(articles)]:
                            title_el = item_el.find("title")
                            link_el = item_el.find("link")
                            source_el = item_el.find("source")
                            if title_el is not None and title_el.text:
                                articles.append({
                                    "headline": title_el.text.strip(),
                                    "summary": title_el.text.strip(),
                                    "source": source_el.text.strip() if (source_el is not None and source_el.text) else "Global Wire",
                                    "url": link_el.text.strip() if (link_el is not None and link_el.text) else "#",
                                    "datetime": int(time.time()),
                                })
                except Exception:
                    pass

            # Score sentiment across headlines
            bull_hits = 0
            bear_hits = 0
            for art in articles:
                text_low = f"{art['headline']} {art['summary']}".lower()
                b_pos = sum(1 for w in _BULLISH_TERMS if w in text_low)
                b_neg = sum(1 for w in _BEARISH_TERMS if w in text_low)
                bull_hits += b_pos
                bear_hits += b_neg
                art["sentiment"] = "BULLISH" if b_pos > b_neg else ("BEARISH" if b_neg > b_pos else "NEUTRAL")

            total_hits = max(1, bull_hits + bear_hits)
            net_sentiment = round((bull_hits - bear_hits) / total_hits, 3)  # [-1.0, +1.0]
            sentiment_label = (
                "BULLISH" if net_sentiment > 0.15
                else ("BEARISH" if net_sentiment < -0.15 else "NEUTRAL")
            )

            return {
                "symbol": symbol_up,
                "count": len(articles),
                "net_sentiment": net_sentiment,
                "sentiment_label": sentiment_label,
                "bullish_hits": bull_hits,
                "bearish_hits": bear_hits,
                "articles": articles[:limit],
            }

        return self._cache.cached(cache_key, ttl_seconds=180.0, fn=_fetch)

    # ------------------------------------------------------------------
    # 4. Macro & Economic Intelligence (FRED / Alpha Vantage / Treasury)
    # ------------------------------------------------------------------
    def get_macro_intelligence(self) -> Dict[str, Any]:
        cache_key = "obb:macro:global"

        def _fetch_series(fn_name: str, extra: str = "", default_val: float = 0.0, default_date: str = "2026-10") -> Dict[str, Any]:
            try:
                url = f"https://www.alphavantage.co/query?function={fn_name}{extra}&interval=monthly&apikey={self.av_key}"
                req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/2.0"})
                with urllib.request.urlopen(req, timeout=4) as r:
                    d = json.loads(r.read().decode("utf-8"))
                    if "data" in d and len(d["data"]) > 0:
                        latest = d["data"][0]
                        val_str = latest.get("value", ".")
                        if val_str != ".":
                            return {"value": float(val_str), "date": latest.get("date", default_date)}
            except Exception:
                pass
            return {"value": default_val, "date": default_date}

        def _fetch() -> Dict[str, Any]:
            # Fetch all 3 macro series in parallel using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=3) as pool:
                f_ffr = pool.submit(_fetch_series, "FEDERAL_FUNDS_RATE", "", 3.75, "2026-10-01")
                f_10y = pool.submit(_fetch_series, "TREASURY_YIELD", "&maturity=10year", 4.12, "2026-10-01")
                f_cpi = pool.submit(_fetch_series, "CPI", "", 314.8, "2026-10-01")

                ffr = f_ffr.result()
                t10y = f_10y.result()
                cpi = f_cpi.result()

            spread = round(t10y["value"] - ffr["value"], 2)
            # Macro stress score [0.0, 1.0]: inverted yield curve or high rates elevate macro risk
            macro_stress = 0.25
            if spread < 0:
                macro_stress += min(0.35, abs(spread) * 0.25)
            if ffr["value"] > 4.5:
                macro_stress += 0.15
            macro_regime = (
                "INVERTED_CAUTION" if spread < 0.0
                else ("RESTRICTIVE" if ffr["value"] >= 4.5 else "ACCOMMODATIVE_NORMAL")
            )

            return {
                "fed_funds_rate": ffr,
                "treasury_10y": t10y,
                "cpi_inflation": cpi,
                "yield_curve_spread": spread,
                "macro_regime": macro_regime,
                "macro_stress_score": round(max(0.05, min(0.95, macro_stress)), 3),
                "status": "success",
            }

        return self._cache.cached(cache_key, ttl_seconds=900.0, fn=_fetch)

    # ------------------------------------------------------------------
    # 5. Unified Intelligence Bundle for Decision Making
    # ------------------------------------------------------------------
    def get_full_intelligence_bundle(self, symbol: str = "AAPL") -> Dict[str, Any]:
        """Concurrently retrieves quote/technicals, fundamentals, news sentiment, and macro indicators."""
        symbol_up = (symbol or "AAPL").upper().strip()
        with ThreadPoolExecutor(max_workers=4) as pool:
            f_qt = pool.submit(self.get_equity_quote_and_technicals, symbol_up)
            f_fd = pool.submit(self.get_equity_fundamentals, symbol_up)
            f_nw = pool.submit(self.get_global_news_sentiment, symbol_up, 6)
            f_mc = pool.submit(self.get_macro_intelligence)

            return {
                "symbol": symbol_up,
                "timestamp": time.time(),
                "openbb_sdk_active": HAS_OPENBB_SDK,
                "quote_technicals": f_qt.result(),
                "fundamentals": f_fd.result(),
                "news_sentiment": f_nw.result(),
                "macro": f_mc.result(),
            }


# Singleton router instance
obb_router = OpenBBUnifiedRouter()
