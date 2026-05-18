# 🔍 SafeScan — AI Ingredient Safety Scanner

<div align="center">

![SafeScan Banner](https://img.shields.io/badge/SafeScan-AI%20Powered-6366f1?style=for-the-badge&logo=google&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47a248?style=for-the-badge&logo=mongodb&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285f4?style=for-the-badge&logo=google&logoColor=white)

**Know exactly what's in your food — instantly.**

Photograph any ingredient label → Gemini AI analyses every ingredient → Get a personalised safety verdict in seconds.

[Features](#-features) · [Demo](#-demo) · [Setup](#-setup) · [API Docs](#-api-endpoints) · [Tech Stack](#-tech-stack)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 📷 **Smart Scanning** | Camera capture or photo upload of any ingredient label |
| 🤖 **Gemini AI Analysis** | Google Gemini 2.5 Flash reads and interprets every ingredient |
| 🛡️ **Allergy Protection** | Cross-checks ingredients against your personal allergy profile |
| 📊 **Health Score** | 0–100 rating for every product scanned |
| 💚 **Safer Alternatives** | AI suggests 3–5 healthier alternatives when a product is unsafe |
| 🧪 **Ingredient Breakdown** | Plain-English explanation of every single ingredient |
| 🕐 **Scan History** | All scans saved — search, filter, and track over time |
| 💛 **Favourites** | Save and revisit your most important scans |
| 👥 **Community Reviews** | Rate and review products, see what others think |
| 🌙 **Dark / Light Mode** | Beautiful theme toggle that persists across pages |

---

## 🎯 How It Works

```
📸 Photograph Label
        ↓
🔤 Tesseract OCR extracts text
        ↓
🤖 Gemini AI analyses ingredients
        ↓
🛡️ Cross-checks YOUR allergy profile
        ↓
📊 Returns Safety Verdict + Health Score
        ↓
💚 Suggests Healthier Alternatives (if unsafe)
```

---

## 🖥️ Demo

### Safety Verdicts
- ✅ **Safe** — No allergens detected, healthy ingredients
- ⚠️ **Use with Caution** — Some concerning ingredients found
- ❌ **Not Safe** — Allergens or harmful ingredients detected

### Supported Allergy Profiles
🥜 Peanuts · 🌰 Tree Nuts · 🥛 Dairy · 🥚 Eggs · 🌾 Gluten · 🫘 Soy · 🦐 Shellfish · 🐟 Fish · 🌻 Sesame

### Dietary Preferences
🌱 Vegan · 🥦 Vegetarian · ☪️ Halal · ✡️ Kosher · 🥑 Keto · 💉 Diabetic-Friendly · 🧂 Low Sodium · 🍬 Sugar-Free

---

## 🚀 Setup

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.10+ | [python.org](https://python.org) |
| MongoDB | 7.0+ | [mongodb.com](https://mongodb.com) |
| Tesseract OCR | Latest | See below |
| Gemini API Key | — | [aistudio.google.com](https://aistudio.google.com/app/apikey) |

### Install Tesseract OCR

**Windows:**
Download installer → https://github.com/UB-Mannheim/tesseract/wiki

**Mac:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

---

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/SafeScan.git
cd SafeScan
```

### 2. Set Up Python Environment

```bash
cd backend
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=safescan
JWT_SECRET=your-long-random-secret-string
JWT_EXPIRE_HOURS=24
GEMINI_API_KEY=your-gemini-api-key-here
UPLOAD_DIR=uploads
```

> 🔑 Get your Gemini API key free at https://aistudio.google.com/app/apikey

### 5. Start MongoDB

```bash
# Windows
net start MongoDB

# Mac
brew services start mongodb-community

# Ubuntu
sudo systemctl start mongod
```

### 6. Run the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

✅ You should see:
```
Connected to MongoDB: safescan
INFO: Uvicorn running on http://127.0.0.1:8000
```

### 7. Run the Frontend

Open a new terminal:

```bash
cd frontend
python -m http.server 3000
```

### 8. Open the App

```
http://localhost:3000/index.html
```

---

## 📁 Project Structure

```
SafeScan/
│
├── 📁 backend/
│   ├── main.py                  ← FastAPI entry point
│   ├── config.py                ← Environment settings
│   ├── database.py              ← MongoDB connection
│   ├── requirements.txt         ← Python dependencies
│   ├── .env.example             ← Environment template
│   │
│   ├── 📁 models/
│   │   └── schemas.py           ← Pydantic data models
│   │
│   ├── 📁 routes/
│   │   ├── auth.py              ← Register, login, JWT
│   │   ├── users.py             ← Profile & preferences
│   │   ├── scan.py              ← Main scan endpoint ⭐
│   │   ├── reviews.py           ← Community reviews
│   │   └── dashboard.py         ← Stats & recent scans
│   │
│   ├── 📁 services/
│   │   ├── gemini_service.py    ← Google Gemini AI ⭐
│   │   └── ocr_service.py       ← Tesseract OCR
│   │
│   └── 📁 utils/
│       └── auth.py              ← JWT + bcrypt helpers
│
├── 📁 frontend/
│   ├── index.html               ← Landing page
│   ├── login.html               ← Sign in
│   ├── register.html            ← Create account
│   ├── onboarding.html          ← Setup allergies
│   ├── dashboard.html           ← Home screen ⭐
│   ├── scan.html                ← Camera + upload ⭐
│   ├── results.html             ← AI analysis results ⭐
│   ├── history.html             ← Past scans
│   ├── profile.html             ← Edit preferences
│   ├── reviews.html             ← Community reviews
│   │
│   ├── 📁 css/
│   │   └── styles.css           ← Complete design system
│   │
│   └── 📁 js/
│       └── api.js               ← API client helpers
│
├── .gitignore
├── QUICKSTART.md
└── README.md
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Sign in, get JWT token |
| GET | `/api/auth/me` | Get current user info |

### Users
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/users/profile` | Get user profile |
| PUT | `/api/users/profile` | Update name |
| PUT | `/api/users/allergies` | Update allergy preferences |

### Scans
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/scan/image` | Upload image for AI analysis ⭐ |
| GET | `/api/scan/history` | Get all past scans |
| GET | `/api/scan/{id}` | Get single scan result |
| DELETE | `/api/scan/{id}` | Delete a scan |
| POST | `/api/scan/{id}/favorite` | Toggle favourite |

### Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/stats` | Stats + recent scans |

### Reviews
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/products/{name}/reviews` | Get product reviews |
| POST | `/api/products/{name}/reviews` | Submit a review |
| POST | `/api/products/{name}/reviews/{id}/helpful` | Mark helpful |

> 📖 Full interactive API docs at: `http://localhost:8000/docs`

---

## 🛠️ Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance async Python web framework
- **[MongoDB](https://mongodb.com)** + **[Motor](https://motor.readthedocs.io/)** — Async NoSQL database
- **[Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/)** — AI vision & ingredient analysis
- **[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)** — Fallback text extraction from images
- **[JWT](https://jwt.io/)** + **[bcrypt](https://pypi.org/project/bcrypt/)** — Secure authentication

### Frontend
- **HTML5** + **CSS3** + **Vanilla JavaScript** — No frameworks, fast & lightweight
- **getUserMedia API** — Camera access for live scanning
- **CSS Custom Properties** — Full dark/light theme system

---

## 🔒 Security

- ✅ Passwords hashed with bcrypt (12 rounds)
- ✅ JWT tokens for session management
- ✅ API keys stored in `.env` (never in code)
- ✅ File type and size validation on uploads
- ✅ CORS configured for local development
- ✅ Input sanitization on all endpoints

---

## 🚧 Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with venv activated |
| `MongoDB connection failed` | Run `net start MongoDB` (Windows) |
| `403 Forbidden` on Gemini | Check `GEMINI_API_KEY` in `.env` is correct |
| `401 Unauthorized` in browser | Log out and log back in — token expired |
| Blank pages in browser | Press `Ctrl+Shift+R` to hard refresh |
| `Failed to fetch` | Make sure backend is running on port 8000 |

---

## 📄 License

MIT License — free to use, modify and distribute.

---

## 👨‍💻 Author

Built with ❤️ using Google Gemini AI, FastAPI and MongoDB.

> ⚠️ **Disclaimer:** SafeScan is for informational purposes only. Always consult a doctor or nutritionist for medical dietary advice.