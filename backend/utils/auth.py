from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
from database import get_db
from bson import ObjectId

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
bearer = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": user_id, "exp": expire},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        payload = jwt.decode(creds.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def is_admin_email(email: str) -> bool:
    allowed = {
        item.strip().lower()
        for item in settings.ADMIN_EMAILS.split(",")
        if item.strip()
    }
    return bool(allowed) and email.strip().lower() in allowed


async def get_current_admin(uid: str = Depends(get_current_user)):
    """Require a valid JWT and a current server-side admin allowlist match."""
    db = get_db()
    try:
        user = await db.users.find_one({"_id": ObjectId(uid)})
    except Exception:
        user = None
    if not user or not is_admin_email(user.get("email", "")):
        raise HTTPException(status_code=403, detail="Administrator access is required")
    return user
