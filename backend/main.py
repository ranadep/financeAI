# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from collections import defaultdict
from pymongo import MongoClient
from bson import ObjectId

from scraper.stock_scraper import get_stock_data, get_daily_change, get_intraday_sparkline
from recommender.advisor import recommend_stocks
from universe.universe import resolve_companies_to_tickers

from insights import router as insights_router
from routers import agent_api as ai_coach  # adjust if path is different
from routers import investment as investment_router
from routers import ai_router

import requests

'''
def query_ollama(prompt: str, model: str = "phi", stream: bool = False) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response received.")
    except Exception as e:
        print(f"❌ Error querying Ollama: {e}")
        return "AI failed to generate a response."
'''

def query_ollama(prompt: str, context: str = "", model: str = "phi", stream: bool = False) -> str:
    url = "http://localhost:11434/api/generate"
    
    full_prompt = f"""
    You are a personal finance assistant. Use the data provided to answer the user's question.
    Only give advice based on the user's real financial data if relevant.

    User's Financial Data:
    {context}

    User's Question:
    {prompt}
    """

    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": stream
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response received.")
    except Exception as e:
        print(f"❌ Error querying Ollama: {e}")
        return "AI failed to generate a response."


# ✅ MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["financeAI"]  # ✅ Removed space from name
expenses = db["expenses"]      # Collection reference

# ✅ FastAPI app setup
app = FastAPI()
app.include_router(insights_router, prefix="/insights")
app.include_router(ai_coach.router)
app.include_router(investment_router.router)
app.include_router(ai_router.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Pydantic models
class PortfolioRequest(BaseModel):
    companies: List[str]

class Expense(BaseModel):
    amount: float
    category: str
    description: str
    date: str  # Format: YYYY-MM-DD
    month: str  # Format: YYYY-MM

# ✅ Root route
@app.get("/")
def root():
    return {"message": "AI Stock Advisor API"}

@app.get("/test-db")
def test_db():
    test_doc = {"test": "connection"}
    result = expenses.insert_one(test_doc)
    return {"inserted_id": str(result.inserted_id)}


# ✅ Stock-related routes
@app.get("/stocks/{ticker}")
def stock_data(ticker: str):
    return get_stock_data(ticker)

@app.get("/top-picks")
def top_picks():
    return recommend_stocks(n=5)

@app.get("/recommendations")
def recommendations(n: int = 5):
    return recommend_stocks(n=n)

@app.get("/screen/top5")
def screen_top5():
    return recommend_stocks(n=5)

@app.post("/portfolio/daily")
def portfolio_daily(req: PortfolioRequest):
    resolved = resolve_companies_to_tickers(req.companies)
    out = []
    for r in resolved:
        if not r["ticker"]:
            out.append({**r, "error": "Unable to resolve to an S&P 500 ticker"})
            continue
        change = get_daily_change(r["ticker"])
        spark = get_intraday_sparkline(r["ticker"])
        out.append({
            **r,
            **change,
            "sparkline": spark
        })
    return out

# ✅ Expenses routes
@app.post("/expenses")
def add_expense(expense: dict):
    date = expense.get("date")
    if not date:
        raise HTTPException(status_code=400, detail="Missing date")

    # Add the month field from the date
    expense["month"] = date[:7]

    result = expenses.insert_one(expense)  # <-- use `expenses` not `collection`
    return {"id": str(result.inserted_id)}

@app.delete("/expenses/{id}")
def delete_expense(id: str):
    result = expenses.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted"}


@app.get("/expenses/{month}")
def get_expenses(month: str):
    start = datetime.strptime(month, "%Y-%m")
    end = start.replace(day=28) + timedelta(days=4)
    end = end.replace(day=1)

    cursor = expenses.find({
        "month": month
    })

    total = 0
    category_totals = defaultdict(float)
    all_expenses = []

    for doc in cursor:
        total += doc["amount"]
        category_totals[doc["category"]] += doc["amount"]
        doc["_id"] = str(doc["_id"])  # convert ObjectId to str
        all_expenses.append(doc)

    return {
        "total": total,
        "categories": category_totals,
        "expenses": all_expenses
    }

# AI Agent routes
@app.get("/coach-insights/{month}")
def ai_coach_insights(month: str):
    expenses_list = list(expenses.find({"month": month}))
    insights = []

    # Overspending detection (except rent)
    category_totals = {}
    for exp in expenses_list:
        if exp["category"] != "Rent":
            category_totals[exp["category"]] = category_totals.get(exp["category"], 0) + float(exp["amount"])

    for cat, total in category_totals.items():
        if total > 200:  # Threshold
            insights.append(f"You may be overspending on {cat} (${total:.2f}). Consider reducing this.")

    # Adaptive budgeting
    budget = 1000
    total_spent = sum(float(exp["amount"]) for exp in expenses_list)
    if total_spent > budget:
        insights.append("You're currently over your budget. Let's consider reducing next month's budget or cutting back.")

    if not insights:
        insights.append("Everything looks great this month. Keep it up!")

    return {"insights": insights}


def get_insights(month: str) -> list:
    """Get spending insights for a given month"""
    expenses_list = list(expenses.find({"month": month}))
    insights = []
    
    if not expenses_list:
        return ["No spending data available for this month."]
    
    # Calculate category totals
    category_totals = {}
    for exp in expenses_list:
        category_totals[exp["category"]] = category_totals.get(exp["category"], 0) + float(exp["amount"])
    
    # Generate insights
    for category, total in category_totals.items():
        if total > 200:
            insights.append(f"High spending on {category}: ${total:.2f}")
    
    if not insights:
        insights.append("Spending looks reasonable this month.")
    
    return insights

def get_adaptive_budget(month: str) -> dict:
    """Get adaptive budget recommendations for a given month"""
    expenses_list = list(expenses.find({"month": month}))
    
    if not expenses_list:
        return {"recommendation": 1000, "averageSpend": 0}
    
    total_spent = sum(float(exp["amount"]) for exp in expenses_list)
    avg_spend = total_spent / len(expenses_list) if expenses_list else 0
    
    # Simple budget recommendation
    recommendation = max(1000, total_spent * 1.1)  # 10% buffer
    
    return {
        "recommendation": round(recommendation, 2),
        "averageSpend": round(avg_spend, 2)
    }


class VoiceQuery(BaseModel):
    question: str

@app.post("/ai/voice-query")
def voice_query(data: VoiceQuery):
    question = data.question
    month = datetime.now().strftime("%Y-%m")

    # Fetch your actual spending insights and budget data
    insights = get_insights(month)  # e.g., returns a list of strings
    budget = get_adaptive_budget(month)  # e.g., {"recommendation": ..., "averageSpend": ...}

    context = f"""
    Insights for {month}:
    - {"; ".join(insights)}

    Adaptive Budget:
    - Recommended Budget: ${budget['recommendation']}
    - Average Spend: ${budget['averageSpend']}
    """
    response = query_ollama(prompt=question, context=context)
    return {"response": response}

