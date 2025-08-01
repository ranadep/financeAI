from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["myFinance"]  # or your custom DB name
expenses_collection = db["expenses"]
