from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- Auth ---
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str

# --- User Profile ---
class AllergyUpdate(BaseModel):
    allergies: List[str] = []
    dietary_preferences: List[str] = []
    medical_conditions: List[str] = []
    custom_avoid_list: List[str] = []

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    allergies: Optional[List[str]] = None
    dietary_preferences: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    custom_avoid_list: Optional[List[str]] = None

# --- Scan ---
class IngredientResult(BaseModel):
    name: str
    safety_level: str          # safe / caution / unsafe
    explanation: str
    triggers_user_allergy: bool
    triggered_allergy_name: Optional[str] = None
    is_natural: Optional[bool] = None
    side_effects: Optional[str] = None

class AlternativeProduct(BaseModel):
    name: str
    brand: str
    why_better: str
    calories: Optional[str] = None
    protein: Optional[str] = None
    fat: Optional[str] = None
    carbs: Optional[str] = None
    sugar: Optional[str] = None
    sodium: Optional[str] = None
    fiber: Optional[str] = None
    benefits: str
    price_range: Optional[str] = None
    where_to_buy: Optional[str] = None

class ScanResult(BaseModel):
    overall_verdict: str        # safe / caution / unsafe
    health_score: int
    ingredients: List[IngredientResult]
    triggered_allergies: List[str]
    main_concerns: List[str]
    alternatives: List[AlternativeProduct]
    ocr_text: str

# --- Review ---
class ReviewCreate(BaseModel):
    product_name: str
    rating: int = Field(..., ge=1, le=5)
    text: str

class ReviewResponse(BaseModel):
    id: str
    user_name: str
    product_name: str
    rating: int
    text: str
    helpful_count: int
    created_at: datetime