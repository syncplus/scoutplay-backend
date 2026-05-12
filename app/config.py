import os
from dotenv import load_dotenv
from aiocache import caches

load_dotenv()



def init_cache():
    caches.set_config({
        "default": {
            "cache": "aiocache.backends.memory.SimpleMemoryCache",
            "ttl": 600,  # 10 minutos
        }
    })


def get_db_type():
    return os.environ.get('DB_TYPE', None)


def get_app_url():
    return os.environ.get('APP_URL', None)

def get_pg_configs():
    return {
        'dbname': os.environ.get('PG_DATABASE', None),
        'host': os.environ.get('PG_HOST', None),
        'port': os.environ.get('PG_PORT', None),
        'user': os.environ.get('PG_USERNAME', None),
        'pwd': os.environ.get('PG_PASSWORD', None),
        'sslmode': os.environ.get('PG_SSLMODE', 'prefer'),
    }

# ─── Auth / JWT ──────────────────────────────────────────────────────
def get_secret_key() -> str:
    value = os.environ.get('SECRET_KEY')
    if not value:
        raise RuntimeError("SECRET_KEY não definida no .env")
    return value


def get_algorithm() -> str:
    return os.environ.get('JWT_ALGORITHM', 'HS256')


def get_access_token_expire_minutes() -> int:
    return int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))


def get_refresh_token_expire_days() -> int:
    return int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS', '7'))


# config.py
def get_allowed_origins() -> list[str]:
    raw = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000')
    if raw.strip() == '*':
        return ['*']
    return [origin.strip() for origin in raw.split(',')]