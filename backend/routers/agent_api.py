from fastapi import APIRouter
from pymongo import MongoClient
from datetime import datetime, timedelta
import calendar

client = MongoClient("mongodb://localhost:27017/")
db = client["financeAI"]
collection = db["expenses"]

router = APIRouter(prefix="/ai", tags=["AI Coach"])

@router.get("/coach-insights/{month}")
def get_coach_insights(month: str):
    expenses = list(collection.find({"month": month}))
    if not expenses:
        return {"insights": ["No spending data found for this month."]}

    insights = []
    category_totals = {}

    for exp in expenses:
        cat = exp.get("category")
        amt = float(exp.get("amount", 0))
        if cat and cat != "Rent":  # Exclude Rent from overspending alerts
            category_totals[cat] = category_totals.get(cat, 0) + amt

    for cat, total in category_totals.items():
        if total > 200:
            insights.append(f"🔍 High spending detected in {cat}: ${total:.2f}")

    total_spent = sum(float(e["amount"]) for e in expenses)
    budget = 1000

    if total_spent > budget:
        insights.append("⚠️ You're exceeding your $1000 monthly budget!")

    if not insights:
        insights.append("✅ Great job! Your spending is within limits.")

    return {"insights": insights}

@router.get("/adaptive-budget/{month}")
def adaptive_budget(month: str):
    selected = datetime.strptime(month, "%Y-%m")
    months_to_consider = [
        (selected.replace(day=1) - timedelta(days=30*i)).strftime("%Y-%m")
        for i in range(1, 4)
    ]

    monthly_totals = []
    for m in months_to_consider:
        data = list(collection.find({"month": m}))
        total = sum(float(e["amount"]) for e in data)
        if total > 0:
            monthly_totals.append(total)

    if not monthly_totals:
        return {"recommendation": 1000, "reason": "No past data. Defaulting to $1000"}

    avg_spend = sum(monthly_totals) / len(monthly_totals)
    recommendation = round(avg_spend * 1.1, 2)  # Allow 10% buffer
    return {
        "recommendation": recommendation,
        "averageSpend": round(avg_spend, 2),
        "monthsConsidered": months_to_consider
    }