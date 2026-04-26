import asyncio
import json
import re

import yfinance as yf

from graph.state import Evidence, AgentStep, GraphState

# Known Indian market ticker mappings for common name → yfinance symbol
_TICKER_MAP = {
    "nifty": "^NSEI",
    "nsei": "^NSEI",
    "sensex": "^BSESN",
    "bse": "^BSESN",
    "infosys": "INFY",
    "infy": "INFY",
    "tcs": "TCS.NS",
    "hdfc": "HDFCBANK.NS",
    "reliance": "RELIANCE.NS",
    "wipro": "WIPRO.NS",
    "bajaj": "BAJFINANCE.NS",
}

# Regex: uppercase letters 1-6 chars optionally followed by .NS or .BO
_TICKER_RE = re.compile(r'\b([A-Z]{1,6}(?:\.(?:NS|BO))?)\b')


def _extract_ticker(query: str) -> str:
    """
    Extract the most likely ticker symbol from the query.
    Priority: known-name map → explicit uppercase symbol → fallback to ^NSEI.
    """
    query_lower = query.lower()

    # 1. Check for known entity names
    for name, symbol in _TICKER_MAP.items():
        if name in query_lower:
            return symbol

    # 2. Look for an explicit ticker pattern (3-6 uppercase letters)
    # Skip common English stop-words that are all-caps by convention
    _STOP_WORDS = {"RBI", "SEBI", "IRDAI", "GDP", "FII", "NPA", "IT", "AI"}
    for match in _TICKER_RE.finditer(query):
        candidate = match.group(1)
        if candidate not in _STOP_WORDS and 2 <= len(candidate.replace(".NS", "").replace(".BO", "")) <= 6:
            return candidate

    # 3. Fallback: NIFTY 50
    return "^NSEI"


async def _fetch_market_data(query: str) -> dict:
    """Runs the blocking yfinance call in a thread executor."""
    loop = asyncio.get_event_loop()
    ticker_symbol = _extract_ticker(query)

    def _sync_fetch():
        ticker = yf.Ticker(ticker_symbol)
        try:
            info = ticker.fast_info
            return {
                "ticker": ticker_symbol,
                "price": getattr(info, "last_price", None),
                "market_cap": getattr(info, "market_cap", None),
                "currency": getattr(info, "currency", None),
            }
        except Exception as e:
            return {"ticker": ticker_symbol, "error": str(e)}

    return await loop.run_in_executor(None, _sync_fetch)


async def financial_data_node(state: GraphState) -> dict:
    """
    Live market data worker.
    Fetches real-time quotes via yfinance (blocking call offloaded to a thread).
    Returns only the keys this node updates.
    """
    step = AgentStep(
        agent_name="financial_data",
        status="running",
        summary="Fetching live market data...",
        detail="Querying Yahoo Finance API",
    )

    data = await _fetch_market_data(state["query"])

    evidence = [
        Evidence(
            source=f"Yahoo Finance – {data.get('ticker', 'N/A')} (live)",
            passage=json.dumps(data),
            relevance_score=0.9,
        )
    ]

    step["status"] = "done"
    step["summary"] = f"Live market data retrieved for {data.get('ticker', 'N/A')}"

    return {"evidence": evidence, "steps": [step]}
