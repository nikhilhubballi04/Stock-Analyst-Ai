from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from data_agent import process_ticker, get_latest_signals
from database import load_data
from ml_agent import backtest_naive, train_xgboost, forecast_next_day
from report_agent import generate_report


class PipelineState(TypedDict):
    ticker: str
    error: Optional[str]
    latest_close: Optional[float]
    predicted_price: Optional[float]
    predicted_return_pct: Optional[float]
    naive_mape: Optional[float]
    xgb_mape: Optional[float]
    rsi: Optional[float]
    macd_signal: Optional[str]
    report: Optional[str]


def data_node(state: PipelineState) -> PipelineState:
    ticker = state["ticker"]
    try:
        process_ticker(ticker, period="5y")
        return {**state, "error": None}
    except ValueError as e:
        return {**state, "error": str(e)}


def ml_node(state: PipelineState) -> PipelineState:
    if state.get("error"):
        return state

    ticker = state["ticker"]
    df = load_data(ticker)

    if df.empty or len(df) < 60:
        return {**state, "error": f"Not enough data for {ticker} to forecast reliably."}

    naive_mape = backtest_naive(df)
    model, feature_cols, xgb_mape = train_xgboost(df)
    predicted_price, predicted_return_pct = forecast_next_day(model, df, feature_cols)
    rsi, macd_signal = get_latest_signals(df)
    latest_close = df.sort_values("date").iloc[-1]["close"]

    return {
        **state,
        "latest_close": round(float(latest_close), 2),
        "predicted_price": predicted_price,
        "predicted_return_pct": predicted_return_pct,
        "naive_mape": naive_mape,
        "xgb_mape": xgb_mape,
        "rsi": rsi,
        "macd_signal": macd_signal,
    }


def report_node(state: PipelineState) -> PipelineState:
    if state.get("error"):
        return {**state, "report": f"Could not generate report: {state['error']}"}

    report = generate_report(
    ticker=state["ticker"],
    latest_close=state["latest_close"],
    predicted_price=state["predicted_price"],
    predicted_return_pct=state["predicted_return_pct"],
    naive_mape=state["naive_mape"],
    xgb_mape=state["xgb_mape"],
    rsi=state["rsi"],
    macd_signal=state["macd_signal"],
)
    return {**state, "report": report}


def build_pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("data_agent", data_node)
    graph.add_node("ml_agent", ml_node)
    graph.add_node("report_agent", report_node)

    graph.set_entry_point("data_agent")
    graph.add_edge("data_agent", "ml_agent")
    graph.add_edge("ml_agent", "report_agent")
    graph.add_edge("report_agent", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_pipeline()

    ticker = input("Enter a ticker symbol (e.g. AAPL, TSLA, BTC-USD): ").strip().upper()

    result = app.invoke({"ticker": ticker})

    print("\n" + "=" * 60)
    print(f"ANALYST NOTE — {ticker}")
    print("=" * 60)
    print(result["report"])
    print("=" * 60)