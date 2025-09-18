from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from auth import mfa, risk_engine
from phishing import detector
from logs.logger import logger
from db import database, models
import datetime

app = FastAPI(title="Bank Hackathon Backend")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class PhishReportRequest(BaseModel):
    url: str
    description: str = ""

# Startup / Shutdown Events
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Endpoints
@app.post("/api/login")
async def login(req: LoginRequest):
    logger.info(f"Login attempt: {req.username}")

    # For now, using mock credentials (replace with DB lookup later)
    if req.username != "user" or req.password != "password":
        logger.warning(f"Invalid login attempt: {req.username}")
        return await log_login(user_id=None, success=False, risk_score=0, username=req.username)
    
    # Generate MFA challenge
    challenge = mfa.generate_challenge(req.username)
    logger.info(f"MFA challenge generated for {req.username}")

    # Log successful login attempt with risk score 0 (step-up happens in MFA verify)
    await log_login(user_id=None, success=True, risk_score=0, username=req.username)

    return {"message": "Login successful", "mfa_challenge": challenge}

@app.post("/api/mfa/verify")
async def verify_mfa(token: str, username: str):
    if mfa.verify_token(username, token):
        risk_score = risk_engine.calculate_risk(username)
        logger.info(f"MFA verified for {username} | Risk score: {risk_score}")

        # Log MFA verification
        await log_login(user_id=None, success=True, risk_score=risk_score, username=username)

        return {"status": "verified", "risk_score": risk_score}
    
    logger.warning(f"Invalid MFA token for {username}")
    await log_login(user_id=None, success=False, risk_score=0, username=username)
    raise HTTPException(status_code=401, detail="Invalid MFA token")

@app.post("/api/report-phish")
async def report_phish(req: PhishReportRequest):
    detected = detector.scan_url(req.url)
    logger.info(f"Phish reported: {req.url} | Detected: {detected}")

    # Log phishing report
    await log_phish_report(user_id=None, url=req.url, description=req.description, detected_as_phish=detected)

    return {"reported": True, "detected_as_phish": detected}


# Helper functions to insert into DB
async def log_login(user_id: int = None, success: bool = True, risk_score: int = 0, username: str = None):
    timestamp = datetime.datetime.utcnow()
    # Optional: You can map username -> user_id from users table if needed
    query = models.login_logs.insert().values(
        user_id=user_id,
        success=success,
        risk_score=risk_score,
        timestamp=timestamp
    )
    await database.execute(query)
    return {"logged": True, "success": success, "risk_score": risk_score}

async def log_phish_report(user_id: int = None, url: str = "", description: str = "", detected_as_phish: bool = False):
    timestamp = datetime.datetime.utcnow()
    query = models.phishing_reports.insert().values(
        user_id=user_id,
        url=url,
        description=description,
        detected_as_phish=detected_as_phish,
        timestamp=timestamp
    )
    await database.execute(query)
    return {"logged": True, "detected_as_phish": detected_as_phish}
