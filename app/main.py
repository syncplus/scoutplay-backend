import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from database import init_db
from config import init_cache
from controllers.database_controller import router as database_router

description = """

Bem-vindo ao backend da ScoutPlay.

"""

app = FastAPI(
    title='ScoutPlay API',
    description=description,
    version='1.0.0',
    debug=True,
    root_path=os.getenv("ROOT_PATH", ""),
    openapi_url='/api/openapi.json',
    docs_url='/api/docs',
    redoc_url='/api/redoc',
)

# ── Middlewares ───────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup ───────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    init_cache()


# ── Static files ──────────────────────────────────────────────────
app.mount("/api/static", StaticFiles(directory="static"), name="static")

# ── DB init ───────────────────────────────────────────────────────
init_db()

# ── HTTP Routers ──────────────────────────────────────────────────
app.include_router(database_router, prefix="/api/v1/database", tags=["Database"])

@app.get("/swagger", include_in_schema=False)
async def swagger_redirect():
    return RedirectResponse(url="/api/docs")


# ── WebSocket ─────────────────────────────────────────────────────
