import aiosqlite

DB_PATH = "calories.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            meal TEXT,
            calories INTEGER,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            user_id TEXT PRIMARY KEY,
            daily_calories INTEGER NOT NULL,
            mode TEXT DEFAULT 'daily'
        )
        """)
        await db.commit()