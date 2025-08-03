// frontend/src/App.js
import { useEffect, useState } from "react";
import { fetchTop5, fetchPortfolioDaily } from "./api";
import StockCard from "./components/StockCard";
import PortfolioForm from "./components/PortfolioForm";
import PortfolioList from "./components/PortfolioList";
import ExpenseTracker from "./components/ExpenseTracker";
import AICoach from "./components/AIcoach";
import InvestmentAdvisor from "./components/InvestmentAdvisor";
import { Route, Routes, Link } from 'react-router-dom';
import VoiceAssistant from "./components/VoiceAssistant";


function App() {
  const [top5, setTop5] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [loadingTop, setLoadingTop] = useState(false);
  const [loadingPf, setLoadingPf] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setLoadingTop(true);
        const picks = await fetchTop5();
        setTop5(picks);
      } catch (e) {
        setError("Failed to load top picks. Is the backend running?");
      } finally {
        setLoadingTop(false);
      }
    })();
  }, []);

  const handlePortfolioSubmit = async (companies) => {
    try {
      setError("");
      setLoadingPf(true);
      const data = await fetchPortfolioDaily(companies);
      setPortfolio(data);
    } catch (e) {
      setError("Failed to load portfolio performance.");
    } finally {
      setLoadingPf(false);
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <nav style={{ marginBottom: 20, borderBottom: "1px solid #ccc", paddingBottom: 10, paddingTop: 10 }}>
        <Link to="/" style={{ marginRight: 12 }}>Home</Link>
        <Link to="/expenses" style={{ marginRight: 12 }}>Expense Tracker</Link>
        <Link to="/ai-coach" style={{ marginRight: 12 }}>AI Coach</Link>
        <Link to="/investment" style={{ marginRight: 12 }}>Investment Advisor</Link>
      </nav>

      <Routes>
        <Route
          path="/"
          element={
            <>
              <h1>AI Stock Advisor</h1>

              <section style={{ marginTop: 24 }}>
                <h2>Top 5 Today (S&amp;P 500)</h2>
                {loadingTop && <p>Loading top picks…</p>}
                {!loadingTop && top5.length === 0 && <p>No picks available.</p>}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
                  {top5.map((s) => (
                    <StockCard key={s.ticker} stock={s} />
                  ))}
                </div>
              </section>

              <section style={{ marginTop: 32 }}>
                <h2>My Portfolio — Daily Up/Down</h2>
                <PortfolioForm onSubmit={handlePortfolioSubmit} />
                {loadingPf && <p>Checking your portfolio…</p>}
                {error && <p style={{ color: "#b42318" }}>{error}</p>}
                <PortfolioList items={portfolio} />
              </section>
            </>
          }
        />

        <Route path="/expenses" element={<ExpenseTracker />} />
        <Route path="/ai-coach" element={<AICoach />} />
        <Route path="/investment" element={<InvestmentAdvisor />} /> 
      </Routes>
    </div>
  );
}

export default App;
