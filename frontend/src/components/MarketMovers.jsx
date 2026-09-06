import { useEffect, useState } from "react";
import { getMarketMovers } from "../api";

function MarketMovers() {
  const [market, setMarket] = useState("US");
  const [gainers, setGainers] = useState([]);
  const [losers, setLosers] = useState([]);

  useEffect(() => {
    getMarketMovers(market)
      .then((data) => {
        setGainers(data.gainers || []);
        setLosers(data.losers || []);
      })
      .catch(() => {
        setGainers([]);
        setLosers([]);
      });
  }, [market]);

  return (
    <div>
      <div className="section-title">📊 Market Movers (Tracked Watchlist)</div>
      <div className="movers-toggle">
        <button
          className={market === "US" ? "active" : ""}
          onClick={() => setMarket("US")}
        >
          US
        </button>
        <button
          className={market === "NSE" ? "active" : ""}
          onClick={() => setMarket("NSE")}
        >
          India (NSE)
        </button>
      </div>

      <div className="movers-grid">
        <div className="movers-card">
          <h3>🟢 Top Gainers</h3>
          <table className="movers-table">
            <tbody>
              {gainers.length === 0 && (
                <tr><td className="mv-price">No gainers right now.</td></tr>
              )}
              {gainers.map((g) => (
                <tr key={g.symbol}>
                  <td className="mv-symbol">{g.symbol}</td>
                  <td className="mv-price">{g.price.toLocaleString()}</td>
                  <td className="mv-gain">▲ {g.change_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="movers-card">
          <h3>🔴 Top Losers</h3>
          <table className="movers-table">
            <tbody>
              {losers.length === 0 && (
                <tr><td className="mv-price">No losers right now.</td></tr>
              )}
              {losers.map((l) => (
                <tr key={l.symbol}>
                  <td className="mv-symbol">{l.symbol}</td>
                  <td className="mv-price">{l.price.toLocaleString()}</td>
                  <td className="mv-loss">▼ {Math.abs(l.change_pct)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default MarketMovers;