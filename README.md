 # Bank Hackathon MVP: Phishing-Resistant Auth + Detection

 A full-stack MVP that demonstrates phishing-resistant MFA (WebAuthn-ready), a simple risk engine, phishing detection/reporting, and a basic analytics/logging pipeline.

 - Backend: `FastAPI` (Python) with `SQLAlchemy` schema, `databases` async driver (SQLite), placeholder MFA/risk modules, and phishing detection APIs.
 - Frontend: `Next.js` (React, TypeScript) scaffold with mock login and phishing alert/report button.
 - AI/ML: Placeholder risk scoring and phishing heuristics, with room to plug in a lightweight model.
 - Optional Modules: Mock blockchain link verification, behavioral biometrics logging, demo deepfake/biometric verification.

 ## Repository Structure

 ```
 .
 ├─ backend/
 │  ├─ app.py
 │  ├─ auth/
 │  │  ├─ mfa.py
 │  │  └─ risk_engine.py
 │  ├─ phishing/
 │  │  ├─ detector.py
 │  │  └─ sandbox.py
 │  ├─ db/
 │  │  ├─ __init__.py         # DATABASE_URL + async connect/disconnect
 │  │  ├─ models.py           # SQLAlchemy tables
 │  │  └─ create_tables.py    # Create tables in backend.db
 │  ├─ logs/
 │  │  ├─ logger.py           # File logger to logs/backend.log
 │  │  └─ backend.log
 │  └─ requirements.txt
 ├─ frontend/
 │  ├─ package.json
 │  ├─ src/ (Next.js app)
 │  └─ ...
 └─ docs/
    └─ architecture.md
 ```

 ## Quickstart

 ### Backend (Windows, PowerShell)

 1) Create/Activate venv (if not already):

 ```
 python -m venv venv
 ./venv/Scripts/Activate.ps1
 ```

 2) Install dependencies:

 ```
 pip install -r backend/requirements.txt
 ```

 3) Initialize the SQLite DB and tables:

 ```
 python -m backend.db.create_tables
 ```

 4) Run the API:

 ```
 uvicorn backend.app:app --reload --port 8000
 ```

 - API base: http://localhost:8000
 - Docs (Swagger): http://localhost:8000/docs

 ### Frontend (Next.js)

 In a new terminal:

 ```
 cd frontend
 pnpm install   # or npm install / yarn
 pnpm dev       # or npm run dev / yarn dev
 ```

 - App base: http://localhost:3000

 ## Core Endpoints (MVP)

 - POST `/api/register` — Create user with placeholder MFA secret.
 - POST `/api/login` — Password check + generate MFA challenge.
 - POST `/api/mfa/verify` — Verify MFA token + return risk score.
 - POST `/api/report-phish` — User reports URL; backend runs heuristic detection and logs result.

 See `backend/app.py` for request/response models.

 ## Database

 - Engine: SQLite, file at `backend/backend.db`.
 - DDL: `backend/db/models.py`.
 - Creation: `python -m backend.db.create_tables`.

 ## Architecture Overview

 - FastAPI backend exposes auth, MFA, phishing detection, and logging endpoints.
 - `auth/mfa.py` uses a simple 6-digit challenge for MVP. Can be replaced with WebAuthn flows (FIDO2).
 - `auth/risk_engine.py` returns a placeholder score; later integrate IP/device/time features and a light ML model.
 - `phishing/detector.py` contains keyword heuristics; later extend to URL embeddings, content analysis, PDF/image scanning.
 - Frontend provides mock login + phishing alert/report button.

 See `docs/architecture.md` for a diagram and module interactions.

 ## Roadmap (4 Weeks)

 Week 1 — Setup & Initial Architecture
 - Scope + MVP, repo and folders, core libs.
 - Technical architecture diagram.
 - Backend scaffold + endpoints.
 - Frontend scaffold (mock login + alert button).
 - Database for users, devices, login logs, phishing reports.
 - Research FIDO2/WebAuthn libraries.
 - Registration API skeleton for MFA secret storage.

 Week 2 — Core Authentication Module
 - MFA device registration endpoint (WebAuthn).
 - MFA login validation endpoint (token binding).
 - Integrate frontend MFA flows.
 - Basic risk engine (IP/device/location/time).
 - Rule-based risk scoring for step-up.
 - Integrate risk + MFA for step-up challenges.
 - E2E test with multiple devices.

 Week 3 — Phishing Detection Module
 - Collect datasets / heuristics for URLs and PDFs/images.
 - Train lightweight model (URL/email content).
 - Backend APIs for scanning.
 - Sandboxed PDF/image viewing (demo-only sandbox).
 - Frontend button to report phishing attempts.
 - E2E test: login → detection → step-up → reporting.

 Week 4 — Advanced + Polish
 - Hybrid identity (biometrics + liveness) skeleton.
 - Deepfake detection concept demo.
 - Mock blockchain link verification.
 - Behavioral biometrics logging (demo app).
 - Central logging and analytics dashboard.
 - Full integration testing.
 - Gamified phishing awareness prototype.
 - Polishing + demo readiness.

 ## Security Notes

 - Do not store plaintext passwords. This MVP uses `passlib[bcrypt]` hashing.
 - Never log secrets or full tokens.
 - For WebAuthn, do not store raw credentials; store public key, credential ID, counters.
 - Add proper CORS domains and HTTPS in production.

 ## License

 MIT (for hackathon demo purposes).
