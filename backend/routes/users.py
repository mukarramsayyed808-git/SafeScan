from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from database import get_db
from models.schemas import ProfileUpdate, AllergyUpdate
from utils.auth import get_current_user

router = APIRouter()

@router.get("/profile")
async def get_profile(uid: str = Depends(get_current_user)):
    db = get_db()
    u = await db.users.find_one({"_id": ObjectId(uid)})
    if not u:
        raise HTTPException(404, "User not found")
    return {
        "id": str(u["_id"]),
        "name": u["name"],
        "email": u["email"],
        "allergies": u.get("allergies", []),
        "dietary_preferences": u.get("dietary_preferences", []),
        "medical_conditions": u.get("medical_conditions", []),
        "custom_avoid_list": u.get("custom_avoid_list", []),
        "onboarding_done": u.get("onboarding_done", False),
    }

@router.put("/profile")
async def update_profile(body: ProfileUpdate, uid: str = Depends(get_current_user)):
    db = get_db()
    update = {k: v for k, v in body.dict().items() if v is not None}
    if not update:
        raise HTTPException(400, "Nothing to update")
    await db.users.update_one({"_id": ObjectId(uid)}, {"$set": update})
    return {"message": "Profile updated"}

@router.put("/allergies")
async def update_allergies(body: AllergyUpdate, uid: str = Depends(get_current_user)):
    db = get_db()
    await db.users.update_one(
        {"_id": ObjectId(uid)},
        {"$set": {
            "allergies": body.allergies,
            "dietary_preferences": body.dietary_preferences,
            "medical_conditions": body.medical_conditions,
            "custom_avoid_list": body.custom_avoid_list,
            "onboarding_done": True,
        }}
    )
    return {"message": "Preferences saved"}