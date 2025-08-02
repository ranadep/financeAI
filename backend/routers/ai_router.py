from fastapi import APIRouter
from pymongo import MongoClient
from datetime import datetime
import calendar

router = APIRouter()
client = MongoClient("mongodb://localhost:27017/")
db = client["financeAI"]
collection = db["expenses"]

@router.get("/ai/coach-insights/{month}")
def coach_insights(month: str):
    data = list(collection.find({"month": month}))
    if not data:
        return {"insights": ["No spending data for this month."]}

    insights = []

    # Exclude fixed costs like rent
    for item in data:
        if item["category"].lower() not in ["rent", "mortgage"]:
            if float(item["amount"]) > 200:
                insights.append(f"High spending in {item['category']}: ${item['amount']}")

    if not insights:
        insights = ["You're on track! Keep up the good budgeting habits."]

    return {"insights": insights}


@router.get("/ai/adaptive-budget/{month}")
def adaptive_budget(month: str):
    selected_month = datetime.strptime(month, "%Y-%m")
    prev_month = selected_month.replace(
        month=selected_month.month - 1 if selected_month.month > 1 else 12,
        year=selected_month.year if selected_month.month > 1 else selected_month.year - 1
    )

    this_month_exp = list(collection.find({"month": month}))
    last_month_exp = list(collection.find({"month": prev_month.strftime("%Y-%m")}))

    this_total = sum(float(x["amount"]) for x in this_month_exp)
    last_total = sum(float(x["amount"]) for x in last_month_exp)

    # Use average to compute new budget
    avg = (this_total + last_total) / 2 if last_total else 1000
    recommendation = round(avg + 0.1 * avg, 2)  # Add 10% buffer

    return {
        "averageSpend": round(avg, 2),
        "recommendation": recommendation
    }
