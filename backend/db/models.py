from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, MetaData
import datetime

metadata = MetaData()

# Users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("mfa_type", String, default="fido2"),   # fido2, totp, etc.
    Column("mfa_secret", String, nullable=True),   # for storage later
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)

# Login logs
login_logs = Table(
    "login_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, nullable=True),
    Column("success", Boolean, default=True),
    Column("risk_score", Integer, default=0),
    Column("timestamp", DateTime, nullable=False)
)

# Phishing reports
phishing_reports = Table(
    "phishing_reports",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, nullable=True),
    Column("url", String, nullable=False),
    Column("description", String, default=""),
    Column("detected_as_phish", Boolean, default=False),
    Column("timestamp", DateTime, nullable=False)
)

# WebAuthn credentials
webauthn_credentials = Table(
    "webauthn_credentials",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, nullable=False),
    Column("credential_id", String, unique=True, nullable=False),  # base64url
    Column("public_key", String, nullable=False),  # base64 of COSE key or PEM
    Column("sign_count", Integer, default=0),
    Column("aaguid", String, nullable=True),
    Column("fmt", String, nullable=True),
    Column("transports", String, nullable=True),  # comma-separated
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)
