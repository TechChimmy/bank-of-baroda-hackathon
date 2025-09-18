# Technical Architecture

This document outlines the high-level architecture for the MVP across frontend, backend, AI modules, and optional blockchain/biometrics components.

## Diagram

```mermaid
flowchart LR
  subgraph Client[Frontend: Next.js]
    UI[Login & Report UI]
    MFA[WebAuthn/TOTP UI (future)]
    AlertBtn[Phishing Alert Button]
  end

  subgraph API[Backend: FastAPI]
    Auth[Auth Controller]
    MFAE[MFA Service]
    Risk[Risk Engine]
    Phish[Phishing Detector]
    Logs[Logger]
    DBLayer[(DB Access)]
  end

  subgraph DB[(SQLite / PostgreSQL)]
    Users[(users)]
    LoginLogs[(login_logs)]
    PhishReports[(phishing_reports)]
  end

  subgraph AI[AI/ML Modules]
    RiskModel[Rule-based Risk Scoring]
    PhishModel[URL/Content Heuristics\n(+ Light ML later)]
  end

  subgraph Optional[Optional Modules]
    Biometrics[Biometrics + Liveness (skeleton)]
    Deepfake[Deepfake Detection (concept)]
    Chain[Blockchain Link Verification (mock)]
    Behav[Behavioral Biometrics (demo logs)]
  end

  UI -->|/api/login, /api/register, /api/mfa/verify| Auth
  AlertBtn -->|/api/report-phish| Phish
  Auth --> MFAE
  Auth --> Risk
  MFAE --> Risk
  Risk --> RiskModel
  Phish --> PhishModel

  Auth --> DBLayer
  MFAE --> DBLayer
  Phish --> DBLayer
  DBLayer --> DB

  Logs -.->|backend.log| API
  Optional -.-> API
```

## Module Map

- Backend (`backend/`)
  - `app.py`: FastAPI app with endpoints for registration, login, MFA verify, and report-phish.
  - `auth/mfa.py`: Placeholder 6-digit challenge; to be replaced with WebAuthn (FIDO2) flows.
  - `auth/risk_engine.py`: Returns placeholder risk score; to integrate IP/device/time + model.
  - `phishing/detector.py`: Keyword heuristic; later extend to URL/content analysis, PDFs, images.
  - `db/models.py`: SQLAlchemy table definitions for `users`, `login_logs`, `phishing_reports`.
  - `db/__init__.py`: Async `Database` instance and helpers; `DATABASE_URL` uses SQLite.
  - `db/create_tables.py`: Script to create tables in `backend.db`.
  - `logs/logger.py`: File logger writing to `logs/backend.log`.

- Frontend (`frontend/`)
  - Next.js scaffold with pages and components for mock login and phishing report button.
  - Integrate WebAuthn in Week 2+ for MFA registration/login.

- AI/ML (`backend/models/`)
  - Placeholder artifacts; evolve with simple models in Week 3.

- Optional Modules
  - `blockchain/validator.py`: Mock hashing + verification demo.
  - Biometrics/Deepfake: Skeletons for demo; out of core path.

## Data Flows

- Registration: Frontend -> `/api/register` -> create user with hashed password and optional MFA secret.
- Login: Frontend -> `/api/login` -> password verify -> generate MFA challenge -> client presents token -> `/api/mfa/verify` -> verify + risk score -> session established (future: JWT/cookies).
- Phishing Report: Frontend -> `/api/report-phish` -> heuristic -> log to DB -> return detection flag.

## Decisions

- Start with SQLite for simplicity; abstract via `databases` for easy swap to PostgreSQL.
- Keep MFA simple in Week 1; add WebAuthn (FIDO2) in Week 2.
- Begin with rule-based risk scoring; consider lightweight model later.
- Heuristic phishing detection first; add ML once baseline works.

## Next Steps

- Week 2: Implement WebAuthn device registration & assertion endpoints.
- Integrate frontend WebAuthn flows.
- Expand risk signals (device, IP, location, time) and wire to step-up logic.
- Add basic dashboard for login and phishing report analytics.
