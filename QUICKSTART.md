# SafeScan — 5-Minute Setup

## Prerequisites
- Python 3.10+
- MongoDB running on `localhost:27017`
- Tesseract OCR installed
- Gemini API key

## Install Tesseract

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```
**Mac:**
```bash
brew install tesseract
```
**Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki

---

## Backend Setup

```bash
cd backend
python -m venv venv

# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env — add your GEMINI_API_KEY

uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

---

## Frontend Setup

Just open `frontend/` with any static server:

```bash
# Option 1 — Python (simplest)
cd frontend
python -m http.server 3000

# Option 2 — Node live-server
npx live-server frontend --port=3000
```

Open http://localhost:3000

---

## Folder Structure

```
safescan/
├── backend/
│   ├── main.py           ← FastAPI entry point
│   ├── config.py         ← Environment settings
│   ├── database.py       ← MongoDB connection
│   ├── .env.example      ← Copy to .env and fill in
│   ├── requirements.txt
│   ├── models/schemas.py ← Pydantic models
│   ├── routes/           ← auth, users, scan, reviews, dashboard
│   ├── services/         ← gemini_service.py, ocr_service.py
│   └── utils/auth.py     ← JWT + bcrypt
└── frontend/
    ├── login.html
    ├── register.html
    ├── onboarding.html   ← Set allergies on first login
    ├── dashboard.html
    ├── scan.html         ← Camera + file upload
    ├── results.html      ← AI analysis results
    ├── history.html
    ├── profile.html
    ├── css/styles.css
    └── js/api.js         ← All API calls
```

---

## User Flow

1. Register → Onboarding (set allergies/diet) → Dashboard
2. Tap "Scan" → Camera or upload label photo
3. Gemini AI analyses → Results page (verdict + per-ingredient breakdown)
4. If unsafe → see healthier alternatives with nutrition info
5. All scans saved to History; mark favourites

---

## Environment Variables

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB URI (default: `mongodb://localhost:27017/`) |
| `MONGO_DB` | Database name (default: `safescan`) |
| `JWT_SECRET` | Long random string for token signing |
| `GEMINI_API_KEY` | Your Google AI Studio key |
| `UPLOAD_DIR` | Where to save uploaded images (default: `uploads`) |