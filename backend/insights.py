from fastapi import APIRouter
from pymongo import MongoClient
from datetime import datetime
import calendar

router = APIRouter()
client = MongoClient("mongodb://localhost:27017/")
db = client["financeAI"]
collection = db["expenses"]


@router.get("/suggestions/{month}")
def get_suggestions(month: str):
    expenses = list(collection.find({"month": month}))
    if not expenses:
        return {"suggestions": ["No data found for this month."]}

    categories = {}
    for e in expenses:
        categories[e["category"]] = categories.get(e["category"], 0) + float(e["amount"])

    suggestions = []
    for category, total in categories.items():
        if total > 200:
            suggestions.append(f"Consider reducing your {category} spending — it’s ${total:.2f} this month.")

    if not suggestions:
        suggestions.append("You're spending within limits. Great job!")

    return {"suggestions": suggestions}


@router.get("/projection/{month}")
def get_projection(month: str):
    expenses = list(collection.find({"month": month}))
    if not expenses:
        return {"currentSpent": 0, "projectedMonthEnd": 0, "budget": 1000}

    try:
        selected_date = datetime.strptime(month, "%Y-%m")
    except ValueError:
        return {"error": "Invalid month format. Use YYYY-MM."}

    days_in_month = calendar.monthrange(selected_date.year, selected_date.month)[1]
    today = datetime.today()

    if today.year == selected_date.year and today.month == selected_date.month:
        current_day = min(today.day, days_in_month)
    else:
        current_day = days_in_month

    total_spent = sum(float(item["amount"]) for item in expenses)
    avg_per_day = total_spent / max(current_day, 1)
    projected = avg_per_day * days_in_month

    budget = 1000
    warning = ""
    if projected > budget:
        warning = f"You are exceeding your budget"

    return {
        "currentSpent": total_spent,
        "projectedMonthEnd": projected,
        "budget": budget,
        "warning": warning
    }


@router.get("/compare")
def compare_months(month1: str, month2: str):
    def get_totals(month):
        data = list(collection.find({"month": month}))
        total = sum(float(e["amount"]) for e in data)
        categories = {}
        for e in data:
            categories[e["category"]] = categories.get(e["category"], 0) + float(e["amount"])
        return total, categories

    total1, cats1 = get_totals(month1)
    total2, cats2 = get_totals(month2)

    if total1 == 0 and total2 == 0:
        summary = "No spending data available for comparison."
    elif total1 > 0 and total2 == 0:
        summary = f"You spent ${total1:.2f} this month. No spending was recorded last month."
    elif total2 > 0 and total1 == 0:
        summary = f"No spending this month. You spent ${total2:.2f} last month."
    else:
        diff = total1 - total2
        if diff > 0:
            summary = f"You spent ${abs(diff):.2f} more than the previous month."
        elif diff < 0:
            summary = f"You saved ${abs(diff):.2f} compared to the previous month."
        else:
            summary = "You spent the same as the previous month."

    category_changes = {}
    all_keys = set(cats1.keys()).union(cats2.keys())
    for key in all_keys:
        diff = cats1.get(key, 0) - cats2.get(key, 0)
        if diff > 0:
            category_changes[key] = {"change": f"+${diff:.2f}"}
        elif diff < 0:
            category_changes[key] = {"change": f"-${abs(diff):.2f}"}
        else:
            category_changes[key] = {"change": "$0.00"}

    return {
        "changeFromLastMonth": summary,
        "categories": category_changes
    }
