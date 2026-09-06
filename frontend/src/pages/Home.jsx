import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeTicker, logout, getUserName } from "../api";
import { useTheme } from "../ThemeContext";
import TickerStrip from "../components/TickerStrip";
import MarketMovers from "../components/MarketMovers";
import NewsSection from "../components/NewsSection";
import "./Home.css";

const QUICK_TICKERS = ["AAPL", "TSLA", "MSFT", "NVDA", "RELIANCE", "TCS"];

function Home() {
  const [market, setMarket] = useState("US");
  const [ticker, setTicker] = useState("AAPL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  function handleMarketChange(value) {
    setMarket(value);
    setTicker(value === "US" ? "AAPL" : "RELIANCE");
  }

  async function runAnalysis(tickerToRun) {
    const finalTicker = tickerToRun || ticker;
    if (!finalTicker) return;

    setError("");
    setLoading(true);
    try {
      const result = await analyzeTicker(finalTicker, market === "India (NSE)" ? "India" : "US");
      navigate("/results", { state: { result } });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleQuickPick(qt) {
    setTicker(qt);
    if (qt === "RELIANCE" || qt === "TCS") {
      setMarket("India (NSE)");
    } else {
      setMarket("US");
    }
  }

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="home-wrapper">
      <div className="topbar">
        <span className="user-pill">👤 {getUserName()}</span>
        <div className="topbar-actions">
          <button className="pill-button" onClick={toggleTheme}>
            {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
          </button>
          <button className="pill-button" onClick={handleLogout}>Logout</button>
        </div>
      </div>

      <TickerStrip />

      <div className="search-hero">
        <span className="hero-badge">MULTI-AGENT AI PIPELINE</span>
        <div className="search-hero-title">Your AI Research Desk</div>
        <div className="search-hero-subtitle">
          Search any stock. Get an autonomous forecast and analyst note in seconds.
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="search-row">
        <div className="search-field" style={{ maxWidth: "160px" }}>
          <label>Market</label>
          <select value={market} onChange={(e) => handleMarketChange(e.target.value)}>
            <option value="US">US</option>
            <option value="India (NSE)">India (NSE)</option>
          </select>
        </div>
        <div className="search-field">
          <label>Ticker Symbol</label>
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="e.g. AAPL, TSLA, RELIANCE"
          />
        </div>
        <button className="run-button" onClick={() => runAnalysis()} disabled={loading}>
          {loading ? "Analyzing..." : "Run Analysis →"}
        </button>
      </div>

      <div className="popular-label">Popular</div>
      <div className="popular-row">
        {QUICK_TICKERS.map((qt) => (
          <button key={qt} className="chip-button" onClick={() => handleQuickPick(qt)}>
            {qt}
          </button>
        ))}
      </div>

      <MarketMovers />
      <NewsSection />
    </div>
  );
}

export default Home;