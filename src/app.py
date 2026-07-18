import textwrap
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from pipeline import build_pipeline
from database import load_data, init_db, init_users_table, create_user, verify_user
from market_overview import get_market_snapshot
from market_movers import get_movers

st.set_page_config(page_title="Quantis | AI Market Analyst", page_icon="📈", layout="wide")

init_db()
init_users_table()

defaults = {
    "logged_in": False,
    "user_name": None,
    "user_email": None,
    "page": "login",
    "theme": "dark",
    "result": None,
    "ticker": None,
    "currency_symbol": "$",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def apply_theme():
    if st.session_state.theme == "dark":
        bg_gradient = "radial-gradient(circle at 15% 0%, rgba(99,102,241,0.12) 0%, transparent 40%), radial-gradient(circle at 85% 20%, rgba(52,211,153,0.08) 0%, transparent 35%), #05070D"
        card = "rgba(18, 21, 29, 0.75)"
        card_border = "rgba(255, 255, 255, 0.06)"
        text = "#F5F7FA"
        subtext = "#8A93A6"
        border = "#1F2430"
    else:
        bg_gradient = "radial-gradient(circle at 15% 0%, rgba(99,102,241,0.06) 0%, transparent 40%), #F7F8FA"
        card = "#FFFFFF"
        card_border = "#E3E6EC"
        text = "#111318"
        subtext = "#5A6274"
        border = "#E3E6EC"

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

        .stApp {{
            background: {bg_gradient};
            background-attachment: fixed;
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}

        .hero-title {{ font-size: 2.4rem; font-weight: 800; color: {text}; letter-spacing: -0.03em; }}
        .hero-subtitle {{ font-size: 0.95rem; color: {subtext}; margin-bottom: 1.5rem; }}
        .hero-badge {{
            display: inline-block; background: rgba(99,102,241,0.14); color: #A5B4FC;
            padding: 5px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;
            margin-bottom: 1rem; border: 1px solid rgba(99,102,241,0.3);
            backdrop-filter: blur(8px);
        }}

        .card {{
            background: {card};
            border: 1px solid {card_border};
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(12px);
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.18);
            transition: border-color 0.2s ease;
        }}
        .card:hover {{ border-color: rgba(99, 102, 241, 0.35); }}

        .metric-label {{ font-size: 0.78rem; color: {subtext}; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }}
        .metric-value {{ font-size: 1.7rem; font-weight: 700; color: {text}; letter-spacing: -0.02em; }}
        .metric-delta-positive {{ color: #34D399; font-size: 0.9rem; font-weight: 600; }}
        .metric-delta-negative {{ color: #F87171; font-size: 0.9rem; font-weight: 600; }}
        .section-title {{ font-size: 1.15rem; font-weight: 700; color: {text}; margin-bottom: 1rem; letter-spacing: -0.01em; }}

        .report-box {{
            background: {card};
            border: 1px solid {card_border};
            border-left: 3px solid #6366F1;
            border-radius: 14px;
            padding: 1.6rem;
            color: {text};
            line-height: 1.75;
            font-size: 0.95rem;
            backdrop-filter: blur(12px);
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.18);
        }}

        .disclaimer {{
            text-align: center; color: {subtext}; font-size: 0.8rem; margin-top: 2.5rem;
            padding-top: 1.5rem; border-top: 1px solid {border};
        }}

        .stButton > button {{
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
            color: white; border: none; border-radius: 10px;
            padding: 0.6rem 1.5rem; font-weight: 600; font-size: 0.88rem;
            box-shadow: 0 2px 12px rgba(99, 102, 241, 0.25);
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.45);
            transform: translateY(-1px);
        }}

        .topbar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }}
        .user-pill {{ color: {subtext}; font-size: 0.85rem; }}

        .ticker-strip {{
            display: flex; gap: 1.2rem; overflow-x: auto; padding: 1rem 1.2rem;
            border: 1px solid {card_border}; border-radius: 14px;
            background: {card};
            backdrop-filter: blur(12px);
            margin-bottom: 1.5rem;
        }}
        .ticker-item {{
            display: flex; flex-direction: column; min-width: 110px;
            padding: 0.3rem 1rem; border-right: 1px solid {border};
        }}
        .ticker-name {{ font-size: 0.72rem; color: {subtext}; font-weight: 500; text-transform: uppercase; letter-spacing: 0.03em; }}
        .ticker-price {{ font-size: 1.05rem; font-weight: 700; color: {text}; }}
        .ticker-up {{ color: #34D399; font-size: 0.82rem; font-weight: 600; }}
        .ticker-down {{ color: #F87171; font-size: 0.82rem; font-weight: 600; }}

        .search-hero {{ text-align: center; padding: 3rem 0 1.8rem 0; }}
        .search-hero-title {{
            font-size: 2.8rem; font-weight: 800; color: {text};
            letter-spacing: -0.04em; margin-bottom: 0.5rem;
            background: linear-gradient(135deg, {text} 30%, #A5B4FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .search-hero-subtitle {{ font-size: 1rem; color: {subtext}; margin-bottom: 1.8rem; }}

        .movers-table {{ width: 100%; border-collapse: collapse; }}
        .movers-table td {{
            padding: 0.7rem 0.4rem; border-bottom: 1px solid {border};
            font-size: 0.88rem; color: {text};
        }}
        .movers-table .mv-symbol {{ font-weight: 600; }}
        .movers-table .mv-price {{ color: {subtext}; }}
        .mv-gain {{ color: #34D399; font-weight: 600; }}
        .mv-loss {{ color: #F87171; font-weight: 600; }}

        .stTextInput > div > div > input, .stSelectbox > div > div, .stRadio > div {{
            background-color: {card} !important;
            border-radius: 10px !important;
        }}
    </style>
    """
    st.markdown(textwrap.dedent(css), unsafe_allow_html=True)


apply_theme()


def top_bar():
    col1, col2, col3, col4 = st.columns([4, 1.3, 1, 1])
    with col1:
        st.markdown(f'<span class="user-pill">👤 {st.session_state.user_name}</span>', unsafe_allow_html=True)
    with col2:
        if st.button("🏠 Home"):
            st.session_state.page = "home"
            st.rerun()
    with col3:
        theme_label = "☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark"
        if st.button(theme_label):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
    with col4:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_name = None
            st.session_state.page = "login"
            st.rerun()


def render_ticker_strip():
    snapshot = get_market_snapshot()
    if not snapshot:
        return
    items_html = ""
    for item in snapshot:
        direction_class = "ticker-up" if item["change_pct"] >= 0 else "ticker-down"
        arrow = "▲" if item["change_pct"] >= 0 else "▼"
        items_html += f'<div class="ticker-item"><div class="ticker-name">{item["name"]}</div><div class="ticker-price">{item["price"]:,}</div><div class="{direction_class}">{arrow} {abs(item["change_pct"])}%</div></div>'
    st.markdown(f'<div class="ticker-strip">{items_html}</div>', unsafe_allow_html=True)


def login_page():
    st.markdown('<div class="hero-badge">MULTI-AGENT AI PIPELINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Quantis Market Analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Sign in to run autonomous market analysis.</div>', unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Log In", use_container_width=True):
            if not email or not password:
                st.warning("Please enter both email and password.")
            else:
                success, result = verify_user(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_name = result
                    st.session_state.user_email = email
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error(result)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("Don't have an account?")
        if st.button("Create one →", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def signup_page():
    st.markdown('<div class="hero-badge">MULTI-AGENT AI PIPELINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Create your account</div>', unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up", use_container_width=True):
            if not all([name, email, password, confirm]):
                st.warning("Please fill in all fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success, message = create_user(email, name, password)
                if success:
                    st.success(message + " Please log in.")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(message)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def home_page():
    top_bar()
    render_ticker_strip()

    st.markdown('<div class="search-hero">', unsafe_allow_html=True)
    st.markdown('<div class="hero-badge">MULTI-AGENT AI PIPELINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="search-hero-title">Your AI Research Desk</div>', unsafe_allow_html=True)
    st.markdown('<div class="search-hero-subtitle">Search any stock. Get an autonomous forecast and analyst note in seconds.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    default_ticker = st.session_state.pop("_quick_pick", None)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        market = st.selectbox("Market", ["US", "India (NSE)"])
    with c2:
        raw_ticker = st.text_input(
            "Ticker Symbol",
            value=default_ticker or ("AAPL" if market == "US" else "RELIANCE"),
            placeholder="e.g. AAPL, TSLA, RELIANCE"
        ).strip().upper()
    with c3:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        run_button = st.button("Run Analysis →", use_container_width=True)

    st.markdown("<div style='height: 4px'></div>", unsafe_allow_html=True)
    st.caption("Popular")
    quick_cols = st.columns(6)
    quick_tickers = ["AAPL", "TSLA", "MSFT", "NVDA", "RELIANCE", "TCS"]
    for i, qt in enumerate(quick_tickers):
        with quick_cols[i]:
            if st.button(qt, key=f"quick_{qt}", use_container_width=True):
                st.session_state["_quick_pick"] = qt
                st.rerun()

    if run_button and raw_ticker:
        ticker = f"{raw_ticker}.NS" if market == "India (NSE)" and not raw_ticker.endswith(".NS") else raw_ticker
        currency_symbol = "₹" if market == "India (NSE)" else "$"

        with st.spinner(f"Agents working — fetching data, forecasting, writing report for {ticker}..."):
            app = build_pipeline()
            result = app.invoke({"ticker": ticker})

        st.session_state.result = result
        st.session_state.ticker = ticker
        st.session_state.currency_symbol = currency_symbol
        st.session_state.page = "results"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Market Movers (Tracked Watchlist)</div>', unsafe_allow_html=True)

    movers_market = st.radio("Movers market", ["US", "India (NSE)"], horizontal=True, label_visibility="collapsed")
    gainers, losers = get_movers("US" if movers_market == "US" else "NSE")

    gain_col, loss_col = st.columns(2)

    with gain_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**🟢 Top Gainers**")
        rows = ""
        for g in gainers:
            rows += f'<tr><td class="mv-symbol">{g["symbol"]}</td><td class="mv-price">{g["price"]:,}</td><td class="mv-gain">▲ {g["change_pct"]}%</td></tr>'
        if not rows:
            rows = '<tr><td class="mv-price">No gainers in tracked watchlist right now.</td></tr>'
        st.markdown(f'<table class="movers-table">{rows}</table>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with loss_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**🔴 Top Losers**")
        rows = ""
        for l in losers:
            rows += f'<tr><td class="mv-symbol">{l["symbol"]}</td><td class="mv-price">{l["price"]:,}</td><td class="mv-loss">▼ {abs(l["change_pct"])}%</td></tr>'
        if not rows:
            rows = '<tr><td class="mv-price">No losers in tracked watchlist right now.</td></tr>'
        st.markdown(f'<table class="movers-table">{rows}</table>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def results_page():
    top_bar()
    result = st.session_state.result
    ticker = st.session_state.ticker
    currency_symbol = st.session_state.currency_symbol

    if st.button("← New Analysis"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown(f'<div class="hero-title">{ticker}</div>', unsafe_allow_html=True)

    if result.get("error"):
        st.error(result["error"])
        return

    delta_class = "metric-delta-positive" if result["predicted_return_pct"] >= 0 else "metric-delta-negative"
    delta_sign = "+" if result["predicted_return_pct"] >= 0 else ""

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="card"><div class="metric-label">Latest Close</div><div class="metric-value">{currency_symbol}{result["latest_close"]}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="card"><div class="metric-label">Predicted Next Close</div><div class="metric-value">{currency_symbol}{result["predicted_price"]}</div><div class="{delta_class}">{delta_sign}{result["predicted_return_pct"]}%</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="card"><div class="metric-label">RSI (14-day)</div><div class="metric-value">{result["rsi"]}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="card"><div class="metric-label">MACD Signal</div><div class="metric-value" style="font-size:1.1rem; text-transform:capitalize;">{result["macd_signal"]}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    chart_col, perf_col = st.columns([2.3, 1])

    with chart_col:
        st.markdown('<div class="section-title">📈 Price History</div>', unsafe_allow_html=True)
        df = load_data(ticker)
        df["date"] = pd.to_datetime(df["date"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["date"], y=df["close"], name="Close Price", line=dict(color="#6366F1", width=2)))
        fig.add_trace(go.Scatter(x=df["date"], y=df["ma_20"], name="20-day MA", line=dict(color="#34D399", width=1.3, dash="dot")))
        fig.add_trace(go.Scatter(x=df["date"], y=df["ma_50"], name="50-day MA", line=dict(color="#F59E0B", width=1.3, dash="dot")))
        fig.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8A93A6", family="Inter"),
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
            yaxis=dict(gridcolor="rgba(128,128,128,0.15)", title=f"Price ({currency_symbol})"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with perf_col:
        st.markdown('<div class="section-title">🎯 Model Performance</div>', unsafe_allow_html=True)
        better = result["xgb_mape"] < result["naive_mape"]
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">XGBoost MAPE</div>
            <div class="metric-value" style="font-size:1.3rem;">{result['xgb_mape']}%</div><br>
            <div class="metric-label">Naive Baseline MAPE</div>
            <div class="metric-value" style="font-size:1.3rem;">{result['naive_mape']}%</div><br>
            <div style="font-size:0.82rem; font-weight:600; color:{'#34D399' if better else '#F59E0B'};">
                {'✓ Model beats naive baseline' if better else '⚠ Naive baseline performs comparably or better'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 AI Analyst Note</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="report-box">{result["report"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="disclaimer">Quantis is an educational multi-agent AI project. Nothing here constitutes financial advice.</div>', unsafe_allow_html=True)


if not st.session_state.logged_in:
    if st.session_state.page == "signup":
        signup_page()
    else:
        login_page()
else:
    if st.session_state.page == "results" and st.session_state.result:
        results_page()
    else:
        home_page()