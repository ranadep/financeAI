# backend/models.py
from pydantic import BaseModel
from typing import Literal
from datetime import date

class Expense(BaseModel):
    amount: float
    category: Literal["Rent", "Electricity", "Water", "Outside Food", "Cooking Material", "Misc", "Clothing", "Electronics"]
    description: str = ""
    date: date
