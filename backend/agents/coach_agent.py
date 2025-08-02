# backend/agents/coach_agent.py
from datetime import datetime
from collections import defaultdict
from pymongo.collection import Collection
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["financeAI"]
collection = db["expenses"]


FIXED_CATEGORIES = {"Rent", "Electricity", "Water"}
DEFAULT_BUDGET = 1000.0  # Can be replaced later per-user


class FinanceCoachAgent:
    def __init__(self, collection: Collection):
        self.collection = collection

    def analyze_month(self, month: str) -> dict:
        expenses = list(self.collection.find({"month": month}))
        if not expenses:
            return {"message": "No data found for this month.", "advice": []}

        category_totals = defaultdict(float)
        for e in expenses:
            category = e["category"]
            if category not in FIXED_CATEGORIES:
                category_totals[category] += float(e["amount"])

        advice = []
        for category, total in category_totals.items():
            if total > 200:  # Arbitrary threshold for now
                advice.append(
                    f"You're spending ${total:.2f} on {category}. Consider reducing it to stay within budget."
                )

        if not advice:
            advice.append("Nice job! You're managing discretionary spending well this month.")

        total_spent = sum(float(e["amount"]) for e in expenses)
        adaptive_budget = self.get_adaptive_budget(month)

        if total_spent > adaptive_budget:
            advice.append(f"You're ${total_spent - adaptive_budget:.2f} over your target budget of ${adaptive_budget:.2f}.")

        return {
            "month": month,
            "totalSpent": total_spent,
            "advice": advice,
        }

    def analyze_realtime(self) -> dict:
        today = datetime.today()
        current_month = today.strftime("%Y-%m")
        expenses = list(self.collection.find({"month": current_month}))

        total_spent = sum(float(e["amount"]) for e in expenses)
        day_of_month = today.day
        days_in_month = 30  # Approximate, or use calendar.monthrange()

        # Real-time budget pacing
        adaptive_budget = self.get_adaptive_budget(month)
        expected_spending = (day_of_month / days_in_month) * adaptive_budget
        warning = ""
        if total_spent > expected_spending + 50:  # +buffer
            warning = (
                f"🚨 You're spending faster than expected. "
                f"By day {day_of_month}, you should have spent ~${expected_spending:.2f} "
                f"but you've spent ${total_spent:.2f}."
            )

        return {
            "date": today.strftime("%Y-%m-%d"),
            "month": current_month,
            "totalSpent": total_spent,
            "expectedByNow": expected_spending,
            "realtimeWarning": warning or "✅ Spending is on track.",
        }
    def get_adaptive_budget(self, month: str) -> float:
        base = datetime.strptime(month + "-01", "%Y-%m-%d")
        months = [
            (base.replace(day=1).replace(month=base.month - i)).strftime("%Y-%m")
            for i in range(1, 4)
            if base.month - i > 0
        ]
        past_expenses = list(self.collection.find({"month": {"$in": months}}))
        if not past_expenses:
            return DEFAULT_BUDGET
        total = sum(float(e["amount"]) for e in past_expenses)
        return total / len(set(e["month"] for e in past_expenses))

