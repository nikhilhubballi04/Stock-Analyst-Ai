import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getPriceHistory } from "../api";

function PriceChart({ ticker, currency }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    getPriceHistory(ticker)
      .then((rows) => {
        const formatted = rows.map((r) => ({
          date: r.date,
          close: r.close,
          ma_20: r.ma_20,
          ma_50: r.ma_50,
        }));
        setData(formatted);
      })
      .catch(() => setData([]));
  }, [ticker]);

  if (!data) return <div className="loading-chart">Loading chart...</div>;
  if (data.length === 0) return <div className="loading-chart">No chart data available.</div>;

  return (
    <ResponsiveContainer width="100%" height={380}>
      <LineChart data={data}>
        <CartesianGrid stroke="rgba(128,128,128,0.15)" />
        <XAxis dataKey="date" stroke="#8A93A6" fontSize={11} tick={{ fill: "#8A93A6" }} minTickGap={40} />
        <YAxis stroke="#8A93A6" fontSize={11} tick={{ fill: "#8A93A6" }} label={{ value: `Price (${currency})`, angle: -90, position: "insideLeft", fill: "#8A93A6", fontSize: 11 }} />
        <Tooltip contentStyle={{ background: "#12151D", border: "1px solid #1F2430", borderRadius: "8px", color: "#F5F7FA" }} />
        <Legend wrapperStyle={{ fontSize: "0.82rem" }} />
        <Line type="monotone" dataKey="close" name="Close Price" stroke="#6366F1" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="ma_20" name="20-day MA" stroke="#34D399" strokeWidth={1.3} strokeDasharray="4 3" dot={false} />
        <Line type="monotone" dataKey="ma_50" name="50-day MA" stroke="#F59E0B" strokeWidth={1.3} strokeDasharray="4 3" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default PriceChart;