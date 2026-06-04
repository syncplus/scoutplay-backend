import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from database import init_db
from config import init_cache
from controllers.database import router as database_router
from app.controllers.auth import router as auth_router
from app.controllers.user import router as user_router
from app.controllers.partida import router as partida_router
from app.controllers.partida_set import router as partida_set_router
from app.controllers.partida_lancamento import router as partida_lancamento_router

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
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user_router, prefix="/api/v1/user", tags=["User"])
app.include_router(partida_router, prefix="/api/v1/partidas", tags=["Partidas"])
app.include_router(partida_set_router, prefix="/api/v1/partidas", tags=["Partidas - Sets"])
app.include_router(partida_lancamento_router, prefix="/api/v1/partidas", tags=["Partidas - Lançamentos"])

@app.get("/swagger", include_in_schema=False)
async def swagger_redirect():
    return RedirectResponse(url="/api/docs")


# ── WebSocket ─────────────────────────────────────────────────────
