// src/App.jsx
import { Routes, Route } from "react-router-dom";
import AICoach from "./components/AIcoach"; // <- import this

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/ai-coach" element={<AICoach />} /> {/* New Route */}
    </Routes>
  );
}
