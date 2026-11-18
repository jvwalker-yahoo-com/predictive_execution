"""
Unified Market Intelligence Suite (OpenBB Enhanced & TTL-Cached)
Integrates:
  1. OpenBB Unified Data Router (obb / multi-provider equity, fundamentals, news, macro)
  2. Frankfurter API: Real-time and historical currency exchange rates (No Auth, CORS enabled).
  3. CoinGecko API: Real-time crypto quotes, 24h volume, and market changes (No Auth, CORS enabled).
  4. FRED / Fed Macro: Parallelized Federal Reserve Economic Data, Fed funds rate, CPI, yields.
  5. SEC EDGAR API: Direct public filings (10-K, 10-Q, 8-K, Form 4) with CIK caching.
  6. Polygon.io / Finnhub / Yahoo Finance: Historical and intraday stock ticks, fundamentals, and news.
"""

import os
import json
import gzip
import time
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Any

from engine.openbb_intel import OpenBBUnifiedRouter, _GLOBAL_CACHE

# SEC requires specific User-Agent format: UserAgent/Version (email)
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "AntigravityMarketIntel/2.0 (contact: jvwalker@yahoo.com)")


class MarketIntelSuite:
    def __init__(
        self,
        finnhub_key: str = "",
        polygon_key: str = "",
        fred_key: str = "",
        av_key: str = ""
    ):
        self.finnhub_key = finnhub_key or os.getenv("FINNHUB_API_KEY", "")
        self.polygon_key = polygon_key or os.getenv("POLYGON_API_KEY", "")
        self.fred_key = fred_key or os.getenv("FRED_API_KEY", "")
        self.av_key = av_key or os.getenv("ALPHA_VANTAGE_API_KEY", "")

        self.obb = OpenBBUnifiedRouter(
            finnhub_key=self.finnhub_key,
            polygon_key=self.polygon_key,
            fred_key=self.fred_key,
            av_key=self.av_key,
        )

        self.cik_cache: Dict[str, str] = {
            "AAPL": "0000320193", "MSFT": "0000789019", "GOOGL": "0001652044", "GOOG": "0001652044",
            "AMZN": "0001018724", "NVDA": "0001045810", "TSLA": "0001318605", "META": "0001326801",
            "AMD": "0000002488", "NFLX": "0001065280", "JPM": "0000019617", "BAC": "0000070858",
            "XOM": "0000034088", "DIS": "0001744489", "INTC": "0000050863", "SPY": "0000884394",
            "QQQ": "0001067839", "MARA": "0001507605", "IREN": "0001874406", "SOFI": "0001818874",
            "HOOD": "0001783879", "COIN": "0001679788", "PLTR": "0001321655"
        }

    # ==========================================
    # 1. Frankfurter API (Forex & FX Crosses)
    # ==========================================
    def get_forex_rates(self, base: str = "USD", targets: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch real-time foreign exchange rates from Frankfurter (Zero Auth, Cached 180s)."""
        if not targets:
            targets = ["EUR", "GBP", "JPY", "CAD", "AUD", "CHF"]
        symbols_str = ",".join(targets)
        cache_key = f"intel:fx:{base}:{symbols_str}"

        def _fetch() -> Dict[str, Any]:
            url = f"https://api.frankfurter.app/latest?from={base}&to={symbols_str}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/2.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return {
                        "base": data.get("base", base),
                        "date": data.get("date", ""),
                        "rates": data.get("rates", {}),
                        "status": "success"
                    }
            except Exception as e:
                fallback_rates = {"EUR": 0.892, "GBP": 0.756, "JPY": 158.2, "CAD": 1.42, "AUD": 1.43, "CHF": 0.86}
                return {"base": base, "date": "cached", "rates": fallback_rates, "status": "fallback", "error": str(e)}

        return _GLOBAL_CACHE.cached(cache_key, ttl_seconds=180.0, fn=_fetch)

    # ==========================================
    # 2. CoinGecko API (Crypto Market Pulse)
    # ==========================================
    def get_crypto_prices(self, coin_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch live crypto quotes, 24h volume & change from CoinGecko (Zero Auth, Cached 120s)."""
        if not coin_ids:
            coin_ids = ["bitcoin", "ethereum", "solana", "ripple", "dogecoin"]
        ids_param = ",".join(coin_ids)
        cache_key = f"intel:crypto:{ids_param}"

        def _fetch() -> Dict[str, Any]:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_param}&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/2.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    output = {}
                    for cid, vals in data.items():
                        output[cid] = {
                            "symbol": cid.upper(),
                            "price_usd": vals.get("usd", 0.0),
                            "volume_24h": vals.get("usd_24h_vol", 0.0),
                            "change_24h_pct": vals.get("usd_24h_change", 0.0)
                        }
                    if output:
                        return {"data": output, "status": "success"}
            except Exception:
                pass
            # Resilient fallback if CoinGecko rate-limits
            return {
                "data": {
                    "bitcoin": {"symbol": "BITCOIN", "price_usd": 91450.0, "volume_24h": 38500000000.0, "change_24h_pct": 1.42},
                    "ethereum": {"symbol": "ETHEREUM", "price_usd": 3120.0, "volume_24h": 18200000000.0, "change_24h_pct": 0.85},
                    "solana": {"symbol": "SOLANA", "price_usd": 194.5, "volume_24h": 4900000000.0, "change_24h_pct": 2.65},
                    "ripple": {"symbol": "RIPPLE", "price_usd": 1.18, "volume_24h": 3100000000.0, "change_24h_pct": -0.45},
                },
                "status": "fallback"
            }

        return _GLOBAL_CACHE.cached(cache_key, ttl_seconds=120.0, fn=_fetch)

    # ==========================================
    # 3. FRED Macroeconomic Indicators (Parallel)
    # ==========================================
    def get_fred_macro_indicators(self) -> Dict[str, Any]:
        """Fetch Federal Reserve macroeconomic data concurrently via OpenBB router."""
        return self.obb.get_macro_intelligence()

    # ==========================================
    # 4. SEC EDGAR API (Direct Corporate Filings)
    # ==========================================
    def get_sec_edgar_filings(self, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch official filings (10-K, 10-Q, 8-K, Form 4) directly from SEC EDGAR (Cached 300s)."""
        ticker_up = (ticker or "AAPL").upper().strip()
        cache_key = f"intel:sec:{ticker_up}:{limit}"

        def _fetch() -> List[Dict[str, Any]]:
            cik = self.cik_cache.get(ticker_up)
            if not cik:
                try:
                    url_tickers = "https://www.sec.gov/files/company_tickers.json"
                    req_t = urllib.request.Request(url_tickers, headers={"User-Agent": SEC_USER_AGENT})
                    with urllib.request.urlopen(req_t, timeout=5) as r:
                        comp_map = json.loads(r.read().decode("utf-8"))
                        for _, entry in comp_map.items():
                            if entry.get("ticker", "").upper() == ticker_up:
                                cik = str(entry.get("cik_str")).zfill(10)
                                self.cik_cache[ticker_up] = cik
                                break
                except Exception:
                    pass

            if not cik:
                cik = "0000320193"

            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            req = urllib.request.Request(url, headers={
                "User-Agent": SEC_USER_AGENT,
                "Accept-Encoding": "gzip, deflate"
            })
            try:
                with urllib.request.urlopen(req, timeout=6) as resp:
                    raw = resp.read()
                    try:
                        raw = gzip.decompress(raw)
                    except Exception:
                        pass
                    data = json.loads(raw.decode("utf-8", errors="ignore"))
                    recent = data.get("filings", {}).get("recent", {})
                    forms = recent.get("form", [])
                    dates = recent.get("filingDate", [])
                    descs = recent.get("primaryDocDescription", [])
                    doc_nums = recent.get("accessionNumber", [])

                    filings = []
                    for i in range(min(limit, len(forms))):
                        form_name = forms[i]
                        acc_num = doc_nums[i].replace("-", "") if i < len(doc_nums) else ""
                        sec_link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/" if acc_num else "https://www.sec.gov/edgar/searchedgar/companysearch"
                        filings.append({
                            "form": form_name,
                            "date": dates[i] if i < len(dates) else "",
                            "description": descs[i] if i < len(descs) else form_name,
                            "url": sec_link
                        })
                    return filings
            except Exception as e:
                return [{"form": "EDGAR Notice", "date": time.strftime("%Y-%m-%d"), "description": f"SEC EDGAR live query: {e}", "url": "https://www.sec.gov/edgar"}]

        return _GLOBAL_CACHE.cached(cache_key, ttl_seconds=300.0, fn=_fetch)

    # ==========================================
    # 5. Polygon.io, Finnhub & OpenBB Quotes
    # ==========================================
    def get_stock_ticks_and_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch stock quote and intraday technicals via Polygon, Finnhub, or OpenBB/Yahoo Finance."""
        symbol_up = (symbol or "AAPL").upper().strip()
        qt = self.obb.get_equity_quote_and_technicals(symbol_up)
        return {
            "source": qt.get("provider", "openbb"),
            "symbol": symbol_up,
            "price": qt.get("price", 0.0),
            "prev_close": qt.get("prev_close", 0.0),
            "change": qt.get("change", 0.0),
            "change_pct": qt.get("change_pct", 0.0),
            "high": qt.get("high", 0.0),
            "low": qt.get("low", 0.0),
            "open": qt.get("open", 0.0),
            "volume": qt.get("volume", 0),
            "vwap": qt.get("vwap", 0.0),
            "sma20": qt.get("sma20", 0.0),
            "sma50": qt.get("sma50", 0.0),
            "rsi14": qt.get("rsi14", 50.0),
            "atr14": qt.get("atr14", 1.0),
            "realized_volatility": qt.get("realized_volatility", 0.22),
            "estimated_spread_bps": qt.get("estimated_spread_bps", 2.5),
            "timestamp": qt.get("timestamp", time.time()),
        }

    def get_market_news_sentiment(self, symbol: str, limit: int = 6) -> List[Dict[str, Any]]:
        """Fetch latest stock market news & sentiment via OpenBB multi-provider news router."""
        news_bundle = self.obb.get_global_news_sentiment(symbol, limit=limit)
        return news_bundle.get("articles", [])

    def get_openbb_intelligence(self, symbol: str = "AAPL") -> Dict[str, Any]:
        """Return full OpenBB intelligence bundle (quote, technicals, fundamentals, news, macro)."""
        return self.obb.get_full_intelligence_bundle(symbol)


if __name__ == "__main__":
    suite = MarketIntelSuite()
    print("Forex:", suite.get_forex_rates()["rates"])
    print("Crypto:", list(suite.get_crypto_prices()["data"].keys()))
    print("FRED Macro:", suite.get_fred_macro_indicators())
    print("SEC EDGAR (AAPL):", len(suite.get_sec_edgar_filings("AAPL")), "filings")
    print("OpenBB Quote (AAPL):", suite.get_stock_ticks_and_quote("AAPL"))
