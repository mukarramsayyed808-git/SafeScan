from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime
from database import get_db
from models.schemas import ReviewCreate
from utils.auth import get_current_user

router = APIRouter()

@router.get("/{product_name}/reviews")
async def get_reviews(product_name: str):
    db = get_db()
    # Only moderator-approved reviews are visible to the public.
    cursor = db.reviews.find({"product_name": product_name, "status": "approved"}).sort("created_at", -1).limit(50)
    reviews = []
    async for r in cursor:
        reviews.append({
            "id":            str(r["_id"]),
            "user_name":     r.get("user_name", "Anonymous"),
            "rating":        r["rating"],
            "text":          r["text"],
            "helpful_count": r.get("helpful_count", 0),
            "created_at":    r["created_at"].isoformat(),
        })
    average = round(sum(review["rating"] for review in reviews) / len(reviews), 1) if reviews else 0
    return {
        "reviews": reviews,
        "average_rating": average,
        "review_count": len(reviews),
    }


@router.post("/{product_name}/reviews")
async def create_review(
    product_name: str,
    body: ReviewCreate,
    uid: str = Depends(get_current_user),
):
    if body.product_name != product_name:
        raise HTTPException(400, "Product name does not match the review destination")
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(uid)})
    if not user:
        raise HTTPException(404, "User not found")
    existing = await db.reviews.find_one({"product_name": product_name, "user_id": uid})
    if existing:
        raise HTTPException(409, "You have already reviewed this product")
    doc = {
        "product_name": product_name,
        "user_id":      uid,
        "user_name":    user["name"] if user else "Anonymous",
        "rating":       body.rating,
        "text":         body.text,
        "helpful_count": 0,
        "status":       "pending",
        "created_at":   datetime.utcnow(),
    }
    result = await db.reviews.insert_one(doc)
    return {"id": str(result.inserted_id), "status": "pending", "message": "Review submitted for admin approval"}


@router.post("/{product_name}/reviews/{review_id}/helpful")
async def mark_helpful(product_name: str, review_id: str, uid: str = Depends(get_current_user)):
    db = get_db()
    result = await db.reviews.update_one(
        {"_id": ObjectId(review_id), "product_name": product_name, "status": "approved"},
        {"$inc": {"helpful_count": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Approved review not found")
    return {"message": "Marked as helpful"}
