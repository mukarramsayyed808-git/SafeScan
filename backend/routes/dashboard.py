from fastapi import APIRouter, Depends
from database import get_db
from utils.auth import get_current_user
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats")
async def get_stats(uid: str = Depends(get_current_user)):
    db = get_db()
    month_ago = datetime.utcnow() - timedelta(days=30)

    total     = await db.scans.count_documents({"user_id": uid})
    safe      = await db.scans.count_documents({"user_id": uid, "verdict": "safe"})
    caution   = await db.scans.count_documents({"user_id": uid, "verdict": "caution"})
    unsafe    = await db.scans.count_documents({"user_id": uid, "verdict": "unsafe"})
    favorites = await db.scans.count_documents({"user_id": uid, "is_favorite": True})

    # Allergens avoided this month = scans where triggered_allergies is non-empty
    pipeline = [
        {"$match": {"user_id": uid, "scanned_at": {"$gte": month_ago}, "triggered_allergies": {"$ne": []}}},
        {"$unwind": "$triggered_allergies"},
        {"$group": {"_id": "$triggered_allergies", "count": {"$sum": 1}}},
    ]
    allergen_cursor = db.scans.aggregate(pipeline)
    allergens_avoided = []
    async for doc in allergen_cursor:
        allergens_avoided.append({"name": doc["_id"], "count": doc["count"]})

    # Recent scans (last 5)
    recent = []
    cursor = db.scans.find({"user_id": uid}).sort("scanned_at", -1).limit(5)
    async for s in cursor:
        recent.append({
            "id":           str(s["_id"]),
            "verdict":      s.get("verdict"),
            "health_score": s.get("health_score"),
            "scanned_at":   s["scanned_at"].isoformat(),
            "image_url":    s.get("image_url", ""),
        })

    return {
        "total_scans":      total,
        "safe":             safe,
        "caution":          caution,
        "unsafe":           unsafe,
        "favorites":        favorites,
        "allergens_avoided": allergens_avoided,
        "recent_scans":     recent,
    }