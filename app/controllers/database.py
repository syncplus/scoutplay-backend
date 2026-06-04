from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_pg_configs, get_db_type
from app.database import engine

router = APIRouter()

@router.get("/status")
async def database_status():
    config = get_pg_configs()

    connected = False
    error = None
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        connected = True
    except Exception as e:
        error = str(e)

    return {
        "connected": connected,
        "error": error,
        "config": {
            "host": config["host"],
            "port": config["port"],
            "dbname": config["dbname"],
            "user": config["user"],
            "sslmode": config["sslmode"],
            "db_type": get_db_type(),
        },
    }
