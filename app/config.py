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