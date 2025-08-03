import pyttsx3 
import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
import requests

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    q.put(bytes(indata))

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("🎙️ Listening... Speak now.")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text")

def handle_query(query, month="2025-08"):
    # Example basic logic
    query = query.lower()
    if "spend" in query and "food" in query:
        res = requests.get(f"http://localhost:8000/expenses/{month}")
        data = res.json()
        print(data)
        food_total = sum(float(e["amount"]) for e in data if e["category"].lower() == "food")
        return f"You spent ${food_total:.2f} on food in {month}."

    elif "overspend" in query:
        res = requests.get(f"http://localhost:8000/ai/coach-insights/{month}")
        insights = res.json().get("insights", [])
        return " ".join(insights)

    elif "budget" in query:
        res = requests.get(f"http://localhost:8000/ai/adaptive-budget/{month}")
        data = res.json()
        return f"Your recommended budget is ${data['recommendation']}, based on an average spend of ${data['averageSpend']}."

    elif "tip" in query:
        return "Try tracking small daily expenses — they add up quickly!"

    else:
        return "Sorry, I didn't understand that. Try asking about spending or budget."

# Main loop
if __name__ == "__main__":
    while True:
        query = listen()
        if query:
            print("You said:", query)
            response = handle_query(query)
            print("🤖 Coach says:", response)
            speak(response)


def query_ollama(prompt: str, model="phi") -> str:
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        return res.json()["response"]
    except Exception as e:
        print("Error querying Ollama:", e)
        return "Sorry, I couldn't answer that."
