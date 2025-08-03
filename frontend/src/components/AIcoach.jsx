import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = "en-US";
recognition.continuous = false;
recognition.interimResults = false;

function AICoach() {
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [insights, setInsights] = useState([]);
  const [adaptiveBudget, setAdaptiveBudget] = useState(null);
  const [voiceInput, setVoiceInput] = useState("");
  const [voiceResponse, setVoiceResponse] = useState("");
  const [listening, setListening] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const hasSpokenRef = useRef(false);
  const timeoutRef = useRef(null);

  const fetchInsights = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/ai/coach-insights/${month}`);
      setInsights(res.data.insights || []);
    } catch (err) {
      console.error("Error fetching insights:", err.message);
    }
  };

  const fetchAdaptiveBudget = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/ai/adaptive-budget/${month}`);
      setAdaptiveBudget(res.data);
    } catch (err) {
      console.error("Error fetching budget:", err.message);
    }
  };

  const startListening = () => {
    if (listening) return; // avoid duplicates

    setListening(true);
    setStatusMsg("🎙️ Listening...");

    hasSpokenRef.current = false;
    recognition.start();

    // Stop after 5 seconds automatically
    timeoutRef.current = setTimeout(() => {
      recognition.stop();
    }, 10000);
  };

  recognition.onresult = async (event) => {
    hasSpokenRef.current = true;
    clearTimeout(timeoutRef.current);

    const transcript = event.results[0][0].transcript;
    setVoiceInput(transcript);
    setStatusMsg("💬 Processing...");

    try {
      const res = await axios.post("http://localhost:8000/ai/voice-query", {
        question: transcript,
      });
      setVoiceResponse(res.data.response);
      setStatusMsg("✅ Answered");
    } catch (err) {
      setVoiceResponse("Sorry, I couldn't process that.");
      setStatusMsg("⚠️ Error");
    }

    setListening(false);
  };

  recognition.onerror = (e) => {
    console.error("Speech recognition error:", e.error);
    setStatusMsg("⚠️ Mic error");
    setListening(false);
    clearTimeout(timeoutRef.current);
  };

  recognition.onend = () => {
    clearTimeout(timeoutRef.current);
    if (!hasSpokenRef.current && listening) {
      // Restart once if user didn’t speak
      recognition.start();
      timeoutRef.current = setTimeout(() => {
        recognition.stop();
      }, 5000);
    } else {
      setListening(false);
    }
  };

  useEffect(() => {
    fetchInsights();
    fetchAdaptiveBudget();
    return () => {
      clearTimeout(timeoutRef.current);
      recognition.abort();
    };
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
        className={`px-4 py-2 rounded ${
          listening ? "bg-red-600" : "bg-blue-500"
        } text-white`}
        disabled={listening}
      >
        🎤 {listening ? "Listening..." : "Ask a Question"}
      </button>

      {statusMsg && (
        <div className="text-sm text-gray-600 italic mt-1">{statusMsg}</div>
      )}

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
