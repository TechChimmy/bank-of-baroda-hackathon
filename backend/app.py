from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Request
from auth import mfa, risk_engine
from auth import webauthn
from phishing import detector
from logs.logger import logger
from db import database, models
import datetime
from passlib.hash import bcrypt

app = FastAPI(title="Bank Hackathon Backend")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # frontend dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    mfa_type: str = "totp"  # default totp, could be fido2 later
    mfa_secret: str | None = None

class PhishReportRequest(BaseModel):
    url: str
    description: str = ""

# WebAuthn models
class WebAuthnBeginRequest(BaseModel):
    username: str

class WebAuthnFinishRegisterRequest(BaseModel):
    username: str
    clientDataJSON: str
    attestationObject: str

class WebAuthnFinishAuthRequest(BaseModel):
    username: str
    id: str
    clientDataJSON: str
    authenticatorData: str
    signature: str

# Startup / Shutdown Events
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ------------------ Registration ------------------
@app.post("/api/register")
async def register(req: RegisterRequest):
    logger.info(f"Register attempt: {req.username}")
    try:
        # check if user exists
        existing_user = await database.fetch_one(
            models.users.select().where(models.users.c.username == req.username)
        )
        if existing_user:
            logger.warning(f"Username already exists: {req.username}")
            raise HTTPException(status_code=400, detail="Username already taken")

        # hash password
        hashed_pw = bcrypt.hash(req.password)

        # insert user
        query = models.users.insert().values(
            username=req.username,
            password_hash=hashed_pw,
            mfa_type=req.mfa_type,
            mfa_secret=req.mfa_secret,
            created_at=datetime.datetime.utcnow(),
        )
        user_id = await database.execute(query)

        logger.info(f"User registered: {req.username} (id: {user_id})")
        return {"status": "registered", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Register failed for {req.username}: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

# ------------------ Login ------------------
@app.post("/api/login")
async def login(req: LoginRequest):
    logger.info(f"Login attempt: {req.username}")

    # fetch from DB
    user = await database.fetch_one(
        models.users.select().where(models.users.c.username == req.username)
    )
    if not user or not bcrypt.verify(req.password, user.password_hash):
        logger.warning(f"Invalid login attempt: {req.username}")
        return await log_login(user_id=user.id if user else None, success=False, risk_score=0, username=req.username)

    # generate MFA challenge
    challenge = mfa.generate_challenge(req.username)
    logger.info(f"MFA challenge generated for {req.username}")

    # log login success
    await log_login(user_id=user.id, success=True, risk_score=0, username=req.username)

    return {"message": "Login successful", "mfa_challenge": challenge}

# ------------------ WebAuthn Registration ------------------
@app.post("/api/webauthn/register/begin")
async def webauthn_register_begin(req: WebAuthnBeginRequest):
    user = await database.fetch_one(
        models.users.select().where(models.users.c.username == req.username)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    options = await webauthn.begin_registration(user_id=user.id, username=req.username)
    logger.info(f"WebAuthn register begin for {req.username}")
    return options


@app.post("/api/webauthn/register/finish")
async def webauthn_register_finish(req: WebAuthnFinishRegisterRequest):
    user = await database.fetch_one(
        models.users.select().where(models.users.c.username == req.username)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await webauthn.finish_registration(
        username=req.username,
        client_data_json_b64=req.clientDataJSON,
        attestation_object_b64=req.attestationObject,
        user_id=user.id,
    )
    logger.info(f"WebAuthn registration finished for {req.username}")
    return result

# ------------------ WebAuthn Authentication ------------------
@app.post("/api/webauthn/authenticate/begin")
async def webauthn_authenticate_begin(req: WebAuthnBeginRequest):
    user = await database.fetch_one(
        models.users.select().where(models.users.c.username == req.username)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    options = await webauthn.begin_authentication(user_id=user.id, username=req.username)
    logger.info(f"WebAuthn authenticate begin for {req.username}")
    return options


@app.post("/api/webauthn/authenticate/finish")
async def webauthn_authenticate_finish(req: WebAuthnFinishAuthRequest, request: Request):
    user = await database.fetch_one(
        models.users.select().where(models.users.c.username == req.username)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await webauthn.finish_authentication(
        username=req.username,
        credential_id_b64=req.id,
        client_data_json_b64=req.clientDataJSON,
        authenticator_data_b64=req.authenticatorData,
        signature_b64=req.signature,
    )

    # Risk scoring with headers + IP
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    risk_score = risk_engine.calculate_risk_v2(
        username=req.username,
        ip=client_ip,
        user_agent=user_agent,
        login_time=datetime.datetime.utcnow(),
    )

    await log_login(user_id=user.id, success=True, risk_score=risk_score, username=req.username)
    logger.info(f"WebAuthn authenticated for {req.username} | Risk score: {risk_score}")
    return {"authenticated": True, "risk_score": risk_score}

# ------------------ MFA Verify ------------------
@app.post("/api/mfa/verify")
async def verify_mfa(token: str, username: str):
    user = await database.fetch_one(
        models.users.select().where(models.users.c.username == username)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if mfa.verify_token(username, token):
        risk_score = risk_engine.calculate_risk(username)
        logger.info(f"MFA verified for {username} | Risk score: {risk_score}")

        await log_login(user_id=user.id, success=True, risk_score=risk_score, username=username)

        return {"status": "verified", "risk_score": risk_score}
    
    logger.warning(f"Invalid MFA token for {username}")
    await log_login(user_id=user.id, success=False, risk_score=0, username=username)
    raise HTTPException(status_code=401, detail="Invalid MFA token")

# ------------------ Phishing Report ------------------
@app.post("/api/report-phish")
async def report_phish(req: PhishReportRequest):
    detected = detector.scan_url(req.url)
    logger.info(f"Phish reported: {req.url} | Detected: {detected}")

    await log_phish_report(user_id=None, url=req.url, description=req.description, detected_as_phish=detected)

    return {"reported": True, "detected_as_phish": detected}

# ------------------ Helper Functions ------------------
async def log_login(user_id: int = None, success: bool = True, risk_score: int = 0, username: str = None):
    timestamp = datetime.datetime.utcnow()
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

# ------------------ Health ------------------
@app.get("/api/health")
async def health():
    return {"status": "ok", "db": True}
