from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime
import os, shutil, uuid
from database import get_db
from utils.auth import get_current_user
from services.ocr_service import extract_text
from services.gemini_service import analyze_ingredients, GeminiServiceError
from config import settings

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}
MAX_SIZE_MB = 10

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/image")
async def scan_image(
    file: UploadFile = File(...),
    uid: str = Depends(get_current_user),
):
    # --- Validate file ---
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}")

    img_bytes = await file.read()
    if len(img_bytes) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File too large (max {MAX_SIZE_MB}MB)")

    # --- Save image ---
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    fname = f"{uuid.uuid4().hex}.{ext}"
    fpath = os.path.join(settings.UPLOAD_DIR, fname)
    with open(fpath, "wb") as f:
        f.write(img_bytes)

    # --- OCR ---
    ocr_text = extract_text(img_bytes)

    # --- Get user profile ---
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(uid)})
    if not user:
        raise HTTPException(404, "User not found")

    profile = {
        "allergies":           user.get("allergies", []),
        "dietary_preferences": user.get("dietary_preferences", []),
        "medical_conditions":  user.get("medical_conditions", []),
        "custom_avoid_list":   user.get("custom_avoid_list", []),
    }

    # --- Gemini AI analysis ---
    try:
        analysis = await analyze_ingredients(img_bytes, file.content_type, ocr_text, profile)
    except GeminiServiceError as e:
        # Do not save an incomplete scan; give the browser an accurate retryable error.
        if os.path.exists(fpath):
            os.remove(fpath)
        raise HTTPException(e.status_code, f"AI analysis failed: {e.detail}")

    # --- Save scan to DB ---
    scan_doc = {
        "user_id":            uid,
        "image_url":          fpath,
        "ocr_text":           ocr_text,
        "ai_analysis":        analysis,
        "verdict":            analysis.get("overall_verdict", "caution"),
        "health_score":       analysis.get("health_score", 50),
        "triggered_allergies": analysis.get("triggered_allergies", []),
        "is_favorite":        False,
        "scanned_at":         datetime.utcnow(),
    }
    result = await db.scans.insert_one(scan_doc)

    return {
        "scan_id": str(result.inserted_id),
        "ocr_text": ocr_text,
        **analysis,
    }


@router.get("/history")
async def get_history(uid: str = Depends(get_current_user)):
    db = get_db()
    cursor = db.scans.find({"user_id": uid}).sort("scanned_at", -1).limit(50)
    scans = []
    async for s in cursor:
        scans.append({
            "id":                str(s["_id"]),
            "verdict":           s.get("verdict"),
            "health_score":      s.get("health_score"),
            "triggered_allergies": s.get("triggered_allergies", []),
            "is_favorite":       s.get("is_favorite", False),
            "scanned_at":        s["scanned_at"].isoformat(),
            "image_url":         s.get("image_url", ""),
        })
    return scans


@router.get("/{scan_id}")
async def get_scan(scan_id: str, uid: str = Depends(get_current_user)):
    db = get_db()
    try:
        s = await db.scans.find_one({"_id": ObjectId(scan_id), "user_id": uid})
    except Exception:
        raise HTTPException(400, "Invalid scan ID")
    if not s:
        raise HTTPException(404, "Scan not found")
    return {
        "id":          str(s["_id"]),
        "ocr_text":    s.get("ocr_text", ""),
        "scanned_at":  s["scanned_at"].isoformat(),
        "is_favorite": s.get("is_favorite", False),
        **s.get("ai_analysis", {}),
    }


@router.delete("/{scan_id}")
async def delete_scan(scan_id: str, uid: str = Depends(get_current_user)):
    db = get_db()
    res = await db.scans.delete_one({"_id": ObjectId(scan_id), "user_id": uid})
    if res.deleted_count == 0:
        raise HTTPException(404, "Scan not found")
    return {"message": "Deleted"}


@router.post("/{scan_id}/favorite")
async def toggle_favorite(scan_id: str, uid: str = Depends(get_current_user)):
    db = get_db()
    s = await db.scans.find_one({"_id": ObjectId(scan_id), "user_id": uid})
    if not s:
        raise HTTPException(404, "Scan not found")
    new_val = not s.get("is_favorite", False)
    await db.scans.update_one({"_id": ObjectId(scan_id)}, {"$set": {"is_favorite": new_val}})
    return {"is_favorite": new_val}
