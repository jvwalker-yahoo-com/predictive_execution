
## 2026-10-21 OpenBB Integration
- Added OpenBB SDK to requirements.
- Created `engine/openbb_intel.py` with data retrieval helpers.
- Updated `engine/predict.py` to incorporate macro, news, and fundamentals signals.
- Updated `.env` placeholders for OpenBB API keys.
- Updated documentation in README.
- Committed and pushed to GitHub.
- Rendered Streamlit app locally.

## 2026-10-21 AI Agent Audit 401 "User not found" Diagnosis & Fix
- Root Cause Identified: The button "Run AI Agent Audit" opens `trading-agents-app-ct37xl3kkrvlt7r3iibenl.streamlit.app` (source: `TradingBot` / `trading-agents-hub`).
- The app had a hardcoded expired fallback OpenRouter API key (`sk-or-v1-51fd...`) which was rejected by OpenRouter with `401: {"error":{"message":"User not found.","code":401}}`.
- Fixes Applied:
  1. Removed dead hardcoded credentials from `TradingBot/app.py`.
  2. Implemented dynamic key resolution: URL query param (`?key=...`) -> Streamlit Cloud Secrets (`st.secrets["OPENROUTER_API_KEY"]`) -> Environment variable.
  3. Added an interactive "🔑 API Key Configuration" expander in the left sidebar of the TradingAgents app so users can paste any active key or inspect their configuration without modifying code.
  4. Added graceful error handling so authentication failures explain the issue and direct the user to the sidebar rather than rendering raw JSON error dumps across the agent cards.
  5. Added automatic Yahoo Finance fallback for analyst targets and consensus when Finnhub is rate-limited or unauthorized (preventing `$N/A`).
  6. Updated `stock-signal-scanner/app.py` to forward `OPENROUTER_API_KEY` seamlessly to the audit hub when available.
  7. Committed and pushed updates to `jvwalker-yahoo-com/trading-agents-hub` (`main`) and `jvwalker-yahoo-com/stock-signal-scanner` (`main`).

## 2026-10-21 OpenRouter Key Verified & Applied
- Verified user-provided OpenRouter API key (`sk-or-v1-4d9...4fb`).
- Key authenticated successfully (`200 OK`) and completed real LLM inference with model `openai/gpt-4o-mini`.
- Updated Windows User environment variable `OPENROUTER_API_KEY`.
- Updated local `.env` configurations across `stock-signal-scanner`, `TradingBot`, `sotck_predict`, and `autonomous-trading-cockpit`.
- Confirmed repos are clean and secure (no API keys committed or exposed to Git).
