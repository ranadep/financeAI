// frontend/src/components/PortfolioList.js
import { LineChart, Line, Tooltip, ResponsiveContainer } from "recharts";

const Chip = ({ direction, pct }) => {
  const bg = direction === "up" ? "#e6ffed" : direction === "down" ? "#ffeaea" : "#eee";
  const color = direction === "up" ? "#1a7f37" : direction === "down" ? "#b42318" : "#333";
  const arrow = direction === "up" ? "↑" : direction === "down" ? "↓" : "→";
  return (
    <span style={{ background: bg, color, padding: "2px 8px", borderRadius: 999 }}>
      {arrow} {pct?.toFixed(2)}%
    </span>
  );
};

export default function PortfolioList({ items }) {
  return (
    <div style={{ display: "grid", gap: 12 }}>
      {items.map((it, idx) => {
        const data = (it.sparkline || []).map((v, i) => ({ i, v }));
        return (
          <div key={idx} style={{ border: "1px solid #ddd", borderRadius: 10, padding: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontWeight: 600 }}>
                  {it.matched_name || it.ticker || it.input}
                </div>
                <div style={{ fontSize: 12, color: "#666" }}>{it.ticker || "Unresolved"}</div>
              </div>
              {it.error ? (
                <span style={{ color: "#b42318" }}>{it.error}</span>
              ) : (
                <Chip direction={it.direction} pct={it.change_pct} />
              )}
            </div>
            {!it.error && data.length > 0 && (
              <div style={{ width: "100%", height: 60, marginTop: 8 }}>
                <ResponsiveContainer>
                  <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                    <Tooltip formatter={(v) => v.toFixed(2)} />
                    <Line type="monotone" dataKey="v" dot={false} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
