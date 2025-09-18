from sqlalchemy import create_engine
from models import metadata

engine = create_engine("sqlite:///backend.db")  # Use the same DB as your FastAPI project
metadata.create_all(engine)
print("Tables created successfully!")
