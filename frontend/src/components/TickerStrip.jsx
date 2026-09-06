import { useEffect, useState } from "react";
import { getMarketSnapshot } from "../api";

function TickerStrip() {
  const [snapshot, setSnapshot] = useState([]);

  useEffect(() => {
    getMarketSnapshot().then(setSnapshot).catch(() => {});
  }, []);

  if (!snapshot.length) return null;

  return (
    <div className="ticker-strip">
      {snapshot.map((item) => (
        <div className="ticker-item" key={item.name}>
          <div className="ticker-name">{item.name}</div>
          <div className="ticker-price">{item.price.toLocaleString()}</div>
          <div className={item.change_pct >= 0 ? "ticker-up" : "ticker-down"}>
            {item.change_pct >= 0 ? "▲" : "▼"} {Math.abs(item.change_pct)}%
          </div>
        </div>
      ))}
    </div>
  );
}

export default TickerStrip;