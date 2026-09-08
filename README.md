# Quantis — AI Multi-Agent Stock Analyst

An end-to-end, full-stack AI application that autonomously researches a stock: it fetches live market data, forecasts the next day's price with a machine learning model, honestly backtests that forecast, and writes a plain-English analyst note using a large language model — all orchestrated through a multi-agent pipeline.

Built as a portfolio project to explore agentic AI systems: multiple specialized agents (data, ML, and reporting) coordinated with **LangGraph**, wrapped in a full **React + FastAPI** application with authentication and live market data.

---

## What it does

1. **Search a stock** (US or Indian market) from a clean web interface
2. A **data agent** pulls live price history via `yfinance` and engineers technical indicators (RSI, MACD, moving averages)
3. An **ML agent** trains an XGBoost model to forecast the next day's closing price, and **honestly backtests it against a naive "no change" baseline** — no cherry-picked results
4. A **report agent**, running a local or cloud LLM, writes a short analyst note — but only using the exact numbers the ML agent produced. The accuracy comparison (does the model actually beat the baseline?) is computed in code, not left to the LLM to judge, which prevents the model from misreporting its own performance
5. Results are displayed with a price chart, key metrics, and the generated note

---

## Why this project is interesting

Most "AI stock predictor" projects quietly assume the model works and move on. This one doesn't:

- **It surfaces an honest, real finding**: on daily price prediction using technical indicators alone, XGBoost performs about the same as a naive baseline (predict "no change"). This isn't a failure — it's a well-documented reflection of market efficiency, and the app reports it plainly instead of overselling accuracy.
- **It has a hallucination guardrail.** Early versions had the LLM occasionally misread which model "won" the accuracy comparison (a known weakness of smaller LLMs doing numeric reasoning). The fix: the comparison is now computed deterministically in Python and handed to the LLM as a fixed verdict string — the LLM narrates it, it never judges it.
- **It runs on entirely free infrastructure.** The LLM report agent runs locally via **Ollama** (no API key, no per-token cost) during development, with an optional switch to a free-tier hosted LLM (Groq) for the deployed version.

---

## Architecture
React (Vite) frontend
│ REST calls (fetch)
▼
FastAPI backend ── JWT auth, SQLite (users + price history)
│
▼
LangGraph pipeline
┌─────────────┬──────────────┬────────────────┐
│ Data agent │ ML agent │ Report agent │
│ yfinance, │ XGBoost, │ Local/cloud │
│ RSI, MACD │ MAPE │ LLM, grounded │
│ │ backtest │ in the numbers │
└─────────────┴──────────────┴────────────────┘

---

## Tech stack

**Backend**
- Python, FastAPI, JWT authentication (PyJWT, bcrypt)
- LangGraph for agent orchestration
- yfinance for market data
- `ta` for technical indicators (RSI, MACD, moving averages)
- XGBoost for price forecasting, scikit-learn for evaluation metrics
- SQLite for user accounts and cached price history
- Ollama (local LLM) for report generation, with optional Groq API fallback for deployment
- `feedparser` for live news aggregation via RSS

**Frontend**
- React (Vite)
- React Router for client-side navigation
- Recharts for the price/forecast chart
- Custom CSS with light/dark theming via CSS variables
- No UI framework — hand-built design system

---

## Features

- 🔐 Real authentication — signup, login, JWT sessions, protected routes
- 📈 Live market ticker strip (major US and Indian indices)
- 🔍 Search any US or NSE-listed ticker
- 🤖 Multi-agent analysis pipeline (data → ML forecast → LLM report)
- 📊 Honest backtesting — XGBoost vs. naive baseline, reported as-is
- 📰 Curated live news, categorized (economy, corporate, market pulse)
- 🌗 Dark / light theme toggle
- 🇮🇳 Multi-currency support (USD / INR)

---

## Running it locally

### Backend

```bash
cd src
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r ../requirements.txt
uvicorn api:app --reload --port 8000
```

### LLM (local)

```bash
# Install Ollama from https://ollama.com, then:
ollama pull llama3.2:3b
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`.

---

## Honest limitations

- Daily price forecasts from technical indicators alone have limited predictive power — this is expected and discussed openly in the generated report, not hidden.
- Market movers and news are computed from a small tracked watchlist / RSS feed, not a full real-time exchange feed.
- The free-tier deployment has cold starts and a non-persistent database (by design, to keep hosting costs at zero).

---



