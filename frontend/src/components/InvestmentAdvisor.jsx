import React, { useState } from "react";
import axios from "axios";

export default function InvestmentAdvisor() {
  const [symbols, setSymbols] = useState("");
  const [results, setResults] = useState([]);

  const handleAnalyze = async () => {
    const stocks = symbols.split(",").map(s => s.trim().toUpperCase());
    try {
      const res = await axios.post("http://localhost:8000/investment/analyze", { stocks });
      setResults(res.data.analysis);
    } catch (err) {
      console.error("Failed to analyze stocks:", err.message);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-blue-700">📊 Investment Analyzer</h1>
      <input
        type="text"
        value={symbols}
        onChange={(e) => setSymbols(e.target.value)}
        placeholder="Enter stocks (e.g. AAPL, TSLA, GOOGL)"
        className="border p-2 rounded w-full"
      />
      <button onClick={handleAnalyze} className="bg-blue-600 text-white px-4 py-2 rounded">
        🔍 Analyze
      </button>

      {results.length > 0 && (
        <div className="bg-white p-6 rounded shadow space-y-4">
          {results.map((r, i) => (
            <div key={i} className="border-b pb-2">
              <h2 className="text-xl font-semibold">{r.symbol}</h2>
              <p>Current Price: {r.price}</p>
              <p>Trend: {r.trend}</p>
              <p className="font-medium text-blue-700">{r.advice}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
