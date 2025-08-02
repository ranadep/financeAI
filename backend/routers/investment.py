from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(prefix="/investment", tags=["Investment Advisor"])

# For now: fake stock prices + sentiment (since we aren't using paid APIs)
class InvestmentInput(BaseModel):
    stocks: list[str]  # e.g. ["AAPL", "TSLA", "GOOGL"]

@router.post("/analyze")
def analyze_investments(payload: InvestmentInput):
    insights = []
    for symbol in payload.stocks:
        mock_price = round(random.uniform(100, 1000), 2)
        trend = random.choice(["uptrend", "downtrend", "flat"])
        advice = {
            "uptrend": "📈 Consider holding or buying more.",
            "downtrend": "📉 You might want to watch closely or sell.",
            "flat": "🔍 No strong movement — hold for now."
        }[trend]

        insights.append({
            "symbol": symbol,
            "price": f"${mock_price}",
            "trend": trend,
            "advice": advice
        })

    return {"analysis": insights}
