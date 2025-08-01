// frontend/src/components/PortfolioForm.js
import { useState } from "react";

export default function PortfolioForm({ onSubmit }) {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    const companies = input.split(",").map(s => s.trim()).filter(Boolean);
    onSubmit(companies);
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 16 }}>
      <label style={{ display: "block", marginBottom: 8 }}>
        Enter companies or tickers (comma-separated)
      </label>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="e.g., Apple, MSFT, NVIDIA, Tesla"
        style={{ width: "100%", padding: 8, marginBottom: 8 }}
      />
      <button type="submit">Check Daily Performance</button>
    </form>
  );
}
