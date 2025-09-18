from sqlalchemy import create_engine
from db.models import metadata

engine = create_engine("sqlite:///./backend/backend.db")  # Match DATABASE_URL in db/__init__.py
metadata.create_all(engine)
print("Tables created successfully!")
