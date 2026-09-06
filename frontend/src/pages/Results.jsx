import { useLocation, useNavigate } from "react-router-dom";
import PriceChart from "../components/PriceChart";
import "./Results.css";

function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;

  if (!result) {
    return (
      <div className="results-wrapper">
        <p style={{ color: "#8A93A6" }}>No analysis data found.</p>
        <button className="back-button" onClick={() => navigate("/home")}>← Back to Home</button>
      </div>
    );
  }

  const {
    ticker, currency, latest_close, predicted_price, predicted_return_pct,
    rsi, macd_signal, xgb_mape, naive_mape, report,
  } = result;

  const isPositive = predicted_return_pct >= 0;
  const modelBeatsBaseline = xgb_mape < naive_mape;

  return (
    <div className="results-wrapper">
      <button className="back-button" onClick={() => navigate("/home")}>← New Analysis</button>
      <div className="results-title">{ticker}</div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Latest Close</div>
          <div className="metric-value">{currency}{latest_close}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Predicted Next Close</div>
          <div className="metric-value">{currency}{predicted_price}</div>
          <div className={isPositive ? "metric-delta-pos" : "metric-delta-neg"}>
            {isPositive ? "+" : ""}{predicted_return_pct}%
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">RSI (14-day)</div>
          <div className="metric-value">{rsi}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">MACD Signal</div>
          <div className="metric-value" style={{ fontSize: "1.05rem", textTransform: "capitalize" }}>
            {macd_signal}
          </div>
        </div>
      </div>

      <div className="results-body">
        <div className="chart-card">
          <div className="section-title">📈 Price History</div>
          <PriceChart ticker={ticker} currency={currency} />
        </div>

        <div className="perf-card">
          <div className="section-title">🎯 Model Performance</div>
          <div className="perf-row">
            <div className="metric-label">XGBoost MAPE</div>
            <div className="metric-value" style={{ fontSize: "1.2rem" }}>{xgb_mape}%</div>
          </div>
          <div className="perf-row">
            <div className="metric-label">Naive Baseline MAPE</div>
            <div className="metric-value" style={{ fontSize: "1.2rem" }}>{naive_mape}%</div>
          </div>
          <div className={`perf-verdict ${modelBeatsBaseline ? "perf-good" : "perf-warn"}`}>
            {modelBeatsBaseline ? "✓ Model beats naive baseline" : "⚠ Naive baseline performs comparably or better"}
          </div>
        </div>
      </div>

      <div className="report-card">
        <div className="section-title">📝 AI Analyst Note</div>
        {report}
      </div>

      <div className="results-disclaimer">
        Quantis is an educational multi-agent AI project. Nothing here constitutes financial advice.
      </div>
    </div>
  );
}

export default Results;