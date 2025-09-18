from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, MetaData

metadata = MetaData()

# Users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password_hash", String, nullable=False)
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
