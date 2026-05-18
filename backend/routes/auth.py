from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from database import get_db
from models.schemas import RegisterRequest, LoginRequest, TokenResponse
from utils.auth import hash_password, verify_password, create_token

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest):
    db = get_db()
    if await db.users.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "name": body.name,
        "email": body.email,
        "password_hash": hash_password(body.password),
        "allergies": [],
        "dietary_preferences": [],
        "medical_conditions": [],
        "custom_avoid_list": [],
        "onboarding_done": False,
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(user)
    uid = str(result.inserted_id)
    return TokenResponse(access_token=create_token(uid), user_id=uid, name=body.name)

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    db = get_db()
    user = await db.users.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    uid = str(user["_id"])
    return TokenResponse(access_token=create_token(uid), user_id=uid, name=user["name"])

@router.get("/me")
async def me(user_id: str = __import__('fastapi').Depends(__import__('utils.auth', fromlist=['get_current_user']).get_current_user)):
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "allergies": user.get("allergies", []),
        "dietary_preferences": user.get("dietary_preferences", []),
        "medical_conditions": user.get("medical_conditions", []),
        "custom_avoid_list": user.get("custom_avoid_list", []),
        "onboarding_done": user.get("onboarding_done", False),
    }