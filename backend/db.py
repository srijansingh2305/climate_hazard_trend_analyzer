from dotenv import load_dotenv
import os
import motor.motor_asyncio

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["climate-hazard-app"]
cache_collection = db["cache_results"]

async def cache_result(bounds, year_range, threshold, trends, summary, hazard):
    key = {
        "bounds": bounds,
        "year_range": year_range,
        "threshold": threshold,
        "hazard": hazard
    }
    data = {
        "trends": trends,
        "summary": summary
    }
    await cache_collection.update_one(key, {"$set": data}, upsert=True)

async def get_cached_result(bounds, year_range, threshold, hazard):
    key = {
        "bounds": bounds,
        "year_range": year_range,
        "threshold": threshold,
        "hazard": hazard
    }
    document = await cache_collection.find_one(key)
    return document

