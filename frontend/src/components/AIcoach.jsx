import React, { useState, useEffect } from "react";
import axios from "axios";

function AICoach() {
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [insights, setInsights] = useState([]);
  const [adaptiveBudget, setAdaptiveBudget] = useState(null);
  const [voiceInput, setVoiceInput] = useState("");
  const [voiceResponse, setVoiceResponse] = useState("");
  const [listening, setListening] = useState(false);

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    setVoiceInput(transcript);
    try {
      const res = await axios.post("http://localhost:8000/ai/voice-query", { question: transcript });
      setVoiceResponse(res.data.response);
    } catch (err) {
      setVoiceResponse("Sorry, I couldn't process that.");
    }
  };

  recognition.onend = () => {
    setListening(false);
  };

  const startListening = () => {
    setListening(true);
    recognition.start();
  };

  const fetchInsights = async () => {
    const res = await axios.get(`http://localhost:8000/ai/coach-insights/${month}`);
    setInsights(res.data.insights || []);
  };

  const fetchAdaptiveBudget = async () => {
    const res = await axios.get(`http://localhost:8000/ai/adaptive-budget/${month}`);
    setAdaptiveBudget(res.data);
  };

  useEffect(() => {
    fetchInsights();
    fetchAdaptiveBudget();
  }, [month]);

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-blue-700">🤖 AI Financial Coach</h1>

      <div className="flex items-center space-x-4">
        <label>📆 Month:</label>
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          className="border p-2 rounded"
        />
      </div>

      <button
        onClick={startListening}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        🎤 Ask a Question
      </button>

      {voiceInput && (
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <strong>You asked:</strong> {voiceInput}
          <br />
          <strong>AI says:</strong> {voiceResponse}
        </div>
      )}

      {adaptiveBudget && (
        <div className="bg-white p-4 shadow rounded">
          <h2 className="text-lg font-semibold">📐 Adaptive Budget</h2>
          <p>Recommended Budget: ${adaptiveBudget.recommendation}</p>
          <p>Average Spend: ${adaptiveBudget.averageSpend}</p>
        </div>
      )}

      {insights.length > 0 && (
        <div className="bg-white p-4 shadow rounded">
          <h2 className="text-lg font-semibold">🧠 AI Coach Insights</h2>
          <ul className="list-disc pl-5">
            {insights.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default AICoach;
