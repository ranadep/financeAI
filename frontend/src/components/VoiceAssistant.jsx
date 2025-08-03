import React, { useState, useEffect } from "react";
import axios from "axios";

const VoiceAssistant = () => {
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [listening, setListening] = useState(false);
  let recognition;

  if (window.SpeechRecognition || window.webkitSpeechRecognition) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
  }

  const startListening = () => {
    if (!recognition) return alert("Speech Recognition not supported in this browser.");

    setListening(true);
    recognition.start();

    recognition.onresult = (event) => {
      const result = event.results[0][0].transcript;
      setTranscript(result);
      setListening(false);
      sendQuery(result);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setListening(false);
    };
  };

  const sendQuery = async (question) => {
    try {
      const res = await axios.post("http://localhost:8000/ai/voice-query", {
        question,
      });
      setResponse(res.data.response);
    } catch (err) {
      console.error("Failed to fetch voice response:", err);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto space-y-4">
      <button
        onClick={startListening}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        🎤 {listening ? "Listening..." : "Ask AI Coach"}
      </button>

      {transcript && (
        <p className="text-gray-700">🗣️ You said: <strong>{transcript}</strong></p>
      )}

      {response && (
        <p className="text-green-700 bg-gray-100 p-3 rounded">
          🤖 AI: {response}
        </p>
      )}
    </div>
  );
};

export default VoiceAssistant;
