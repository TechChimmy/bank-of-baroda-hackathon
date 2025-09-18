from databases import Database

DATABASE_URL = "sqlite:///./backend.db"
database = Database(DATABASE_URL)

async def connect():
    await database.connect()

async def disconnect():
    await database.disconnect()
