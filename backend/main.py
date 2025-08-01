# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from collections import defaultdict
from pymongo import MongoClient

from scraper.stock_scraper import get_stock_data, get_daily_change, get_intraday_sparkline
from recommender.advisor import recommend_stocks
from universe.universe import resolve_companies_to_tickers

# ✅ MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["financeAI"]  # ✅ Removed space from name
expenses = db["expenses"]      # Collection reference

# ✅ FastAPI app setup
app = FastAPI()

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
def add_expense(expense: Expense):
    expenses.insert_one(expense.dict())
    return {"message": "Expense added"}

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

