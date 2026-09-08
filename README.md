# CRIMSON — AI-Powered Intelligence & Investigation Platform

**CRIMSON** is a full-stack, local-first intelligence analysis and investigation platform designed for cyber defense analysts, financial intelligence units, and threat investigators.

---

## 🌟 Features

- **Case Management Registry**: Complete CRUD workflows for cases, milestone timelines, priorities (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and statuses (`OPEN`, `INVESTIGATING`, `PENDING`, `RESOLVED`, `ARCHIVED`).
- **Subject & Entity Tracking**: Track Person, Organization, Location, Event, Object, and Digital Entity profiles with risk levels and cryptographic identifiers.
- **Cryptographic Evidence Vault**: Secure evidence cataloging supporting Documents, Text, Images, URLs, and Records with automated SHA-256 reference hash verification.
- **Local AI & NLP Intelligence Engine**: Deterministic pattern matching, Named Entity Recognition (NER), relationship extraction, sentiment/risk flag detection, confidence scoring, recommendations, and next step suggestions running 100% locally in **DEMO AI MODE**.
- **Explainable Risk Engine**: Transparent 0–100 risk scoring model calculating threat scores based on entity network linkage density, priority rating, and critical threat flags with detailed factor explanations.
- **Interactive Network Relationship Canvas**: Visual node-edge graph with zoom, pan, entity type filtering, node selection inspection, and dynamic relationship creation.
- **Global Intelligence Search**: Fast multi-registry search across Cases, Subjects, Evidence, AI Analyses, and Reports.
- **Structured Report Generator**: Instant compilation and printable export of Case Summaries, Investigation Reports, Intelligence Analyses, Evidence Logs, and Risk Assessments.
- **Audit Logs & Live Notifications**: Real-time audit stream tracking user actions, logins, case updates, and in-app system alerts.
- **System Health Monitor**: Live telemetry for API, Database, AI Engine, and NLP Processor statuses.

---

## 🏗 Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS (Custom Dark Charcoal & Crimson design system)
- **Icons**: Lucide React Icons
- **HTTP Client**: Axios with automatic JWT interceptors & error handlers

### Backend
- **Framework**: Python 3.14 + FastAPI
- **ORM / DB**: SQLAlchemy 2.0 + SQLite (`crimson.db`)
- **Authentication**: JWT tokens + PBKDF2 HMAC password hashing
- **Testing**: pytest suite

---

## 📁 Project Structure

```
d:/SIH/Crimson/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI Routers (auth, cases, subjects, evidence, analysis, network, search, reports, activity, notifications, settings, health)
│   │   ├── services/     # AI NLP Engine, Risk Engine, Report Service
│   │   ├── config.py     # Environment settings
│   │   ├── database.py   # SQLAlchemy session manager
│   │   ├── models.py     # Database ORM schemas
│   │   ├── schemas.py    # Pydantic v2 data models
│   │   ├── seed.py       # Seed script for realistic demo data
│   │   └── main.py       # FastAPI application entry point
│   ├── tests/            # Pytest automated test suite
│   └── requirements.txt  # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # Layout (Sidebar, Header, NotificationPanel) & Common (StatusBadge, RiskGauge, LoadingState, BackendStatusBanner)
│   │   ├── context/      # AuthContext provider
│   │   ├── pages/        # Dashboard, Cases, CaseDetail, Subjects, Evidence, Analysis, Search, Network, Reports, Activity, Settings, Login
│   │   ├── services/     # Central API client (api.ts)
│   │   ├── types/        # TypeScript interfaces
│   │   ├── App.tsx       # Router configuration
│   │   ├── index.css     # Crimson design system CSS
│   │   └── main.tsx      # React entry point
│   ├── package.json
│   └── vite.config.ts
├── .env.example
├── start_crimson.bat     # Windows 1-click startup batch script
└── README.md
```

---

## 🔑 Demo Credentials

CRIMSON includes pre-seeded accounts for role-based access testing:

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Administrator** | `admin@crimson.intel` | `crimson2026` | Full platform control & report generation |
| **Senior Analyst** | `analyst@crimson.intel` | `crimson2026` | Case management & AI workspace access |
| **Viewer** | `viewer@crimson.intel` | `crimson2026` | Read-only audit & reporting view |

---

## 🚀 Quick Start (Windows)

### Option 1: One-Click Batch Script
Double-click `start_crimson.bat` in the project root directory.

### Option 2: Manual Terminal Setup

#### 1. Start FastAPI Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Backend REST API: `http://127.0.0.1:8000`
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`

#### 2. Start React Frontend
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
- Web Application UI: `http://127.0.0.1:5173`

---

## 🧪 Testing & Verification

Run backend unit & integration tests with pytest:
```bash
pytest backend/tests
```

Build production frontend bundle:
```bash
cd frontend
npm run build
```

---

## 🤖 Local AI / NLP Engine Explanation

CRIMSON operates locally without external API keys or cloud dependencies:
1. **Entity Extraction**: Recognizes email addresses, IP addresses, Ethereum crypto wallets, phone numbers, passport IDs, and monetary values via regex + dictionary matching.
2. **Threat Flag Identification**: Scans context against risk keyword matrices (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
3. **Relationship Mapping**: Connects pairs of identified entities (e.g. `Person → works_for → Organization`, `Person → owns → Digital Entity`).
4. **Explainable Risk Engine**: Calculates a transparent score (0–100) based on priority ratings, entity linkage density, and threat indicators.
