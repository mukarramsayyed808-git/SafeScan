from datetime import datetime, timedelta

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from models.schemas import LoginRequest, ReviewApprovalUpdate, TokenResponse
from utils.auth import create_token, get_current_admin, is_admin_email, verify_password

router = APIRouter()


def serialize_scan(scan: dict) -> dict:
    return {
        "id": str(scan["_id"]),
        "user_id": scan.get("user_id", ""),
        "user_name": scan.get("user_name", "Unknown user"),
        "user_email": scan.get("user_email", ""),
        "verdict": scan.get("verdict", "caution"),
        "health_score": scan.get("health_score", 0),
        "scanned_at": scan.get("scanned_at").isoformat() if scan.get("scanned_at") else None,
    }


@router.post("/login", response_model=TokenResponse)
async def admin_login(body: LoginRequest):
    """Authenticate an existing user and verify the server-side admin allowlist."""
    db = get_db()
    user = await db.users.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not is_admin_email(user.get("email", "")):
        raise HTTPException(status_code=403, detail="This account is not an administrator")
    return TokenResponse(
        access_token=create_token(str(user["_id"])),
        user_id=str(user["_id"]),
        name=user["name"],
    )


@router.get("/overview")
async def admin_overview(admin: dict = Depends(get_current_admin)):
    db = get_db()
    week_ago = datetime.utcnow() - timedelta(days=6)
    total_users = await db.users.count_documents({})
    total_scans = await db.scans.count_documents({})
    safe = await db.scans.count_documents({"verdict": "safe"})
    caution = await db.scans.count_documents({"verdict": "caution"})
    unsafe = await db.scans.count_documents({"verdict": "unsafe"})
    total_reviews = await db.reviews.count_documents({})

    average = await db.scans.aggregate([
        {"$group": {"_id": None, "value": {"$avg": "$health_score"}}}
    ]).to_list(length=1)
    daily = [
        {"date": row["_id"], "count": row["count"]}
        async for row in db.scans.aggregate([
            {"$match": {"scanned_at": {"$gte": week_ago}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$scanned_at"}},
                "count": {"$sum": 1},
            }},
            {"$sort": {"_id": 1}},
        ])
    ]
    recent = [
        serialize_scan(scan)
        async for scan in db.scans.aggregate([
            {"$sort": {"scanned_at": -1}}, {"$limit": 10},
            {"$lookup": {
                "from": "users", "let": {"scan_user_id": "$user_id"},
                "pipeline": [{"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$scan_user_id"]}}}],
                "as": "user",
            }},
            {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "user_id": 1, "verdict": 1, "health_score": 1, "scanned_at": 1,
                "user_name": "$user.name", "user_email": "$user.email",
            }},
        ])
    ]
    return {
        "admin_name": admin.get("name", "Admin"), "total_users": total_users,
        "total_scans": total_scans, "safe": safe, "caution": caution, "unsafe": unsafe,
        "total_reviews": total_reviews,
        "average_health_score": round(average[0]["value"], 1) if average else 0,
        "daily_scans": daily, "recent_scans": recent,
    }


@router.get("/users")
async def admin_users(admin: dict = Depends(get_current_admin)):
    db = get_db()
    users = []
    pipeline = [
        {"$lookup": {
            "from": "scans", "let": {"uid": {"$toString": "$_id"}},
            "pipeline": [{"$match": {"$expr": {"$eq": ["$user_id", "$$uid"]}}}],
            "as": "user_scans",
        }},
        {"$addFields": {"scan_count": {"$size": "$user_scans"}}},
        {"$project": {"password_hash": 0, "user_scans": 0}},
        {"$sort": {"created_at": -1}}, {"$limit": 100},
    ]
    async for user in db.users.aggregate(pipeline):
        users.append({
            "id": str(user["_id"]), "name": user.get("name", ""),
            "email": user.get("email", ""), "scan_count": user.get("scan_count", 0),
            "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
            "is_admin": is_admin_email(user.get("email", "")),
        })
    return users


@router.delete("/users/{user_id}")
async def admin_delete_user(user_id: str, admin: dict = Depends(get_current_admin)):
    if user_id == str(admin["_id"]):
        raise HTTPException(status_code=400, detail="You cannot delete your own administrator account")
    try:
        target_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    db = get_db()
    if not await db.users.find_one({"_id": target_id}):
        raise HTTPException(status_code=404, detail="User not found")
    await db.scans.delete_many({"user_id": user_id})
    await db.reviews.delete_many({"user_id": user_id})
    await db.users.delete_one({"_id": target_id})
    return {"message": "User and associated scans/reviews deleted"}


@router.get("/reviews")
async def admin_reviews(admin: dict = Depends(get_current_admin)):
    db = get_db()
    reviews = []
    async for review in db.reviews.find({}).sort("created_at", -1).limit(100):
        reviews.append({
            "id": str(review["_id"]), "product_name": review.get("product_name", "Unknown product"),
            "user_name": review.get("user_name", "Anonymous"), "rating": review.get("rating", 0),
            "text": review.get("text", ""), "helpful_count": review.get("helpful_count", 0),
            "status": review.get("status", "pending"),
            "created_at": review.get("created_at").isoformat() if review.get("created_at") else None,
        })
    return reviews


@router.patch("/reviews/{review_id}/approval")
async def admin_set_review_approval(
    review_id: str,
    body: ReviewApprovalUpdate,
    admin: dict = Depends(get_current_admin),
):
    try:
        review_id = ObjectId(review_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid review ID")
    status = "approved" if body.approved else "pending"
    result = await get_db().reviews.update_one({"_id": review_id}, {"$set": {"status": status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": f"Review {status}", "status": status}


@router.delete("/reviews/{review_id}")
async def admin_delete_review(review_id: str, admin: dict = Depends(get_current_admin)):
    try:
        review_id = ObjectId(review_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid review ID")
    result = await get_db().reviews.delete_one({"_id": review_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted"}
