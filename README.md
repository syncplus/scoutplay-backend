# ScoutPlay API

API REST + WebSocket construída com **FastAPI**, seguindo a mesma arquitetura do projeto delas-network-api.

## Stack

- **FastAPI** + uvicorn/gunicorn
- **SQLAlchemy async** (asyncpg) + PostgreSQL (prod) / SQLite (dev)
- **Alembic** para migrations
- **Keycloak** para autenticação JWT
- **Azure Blob Storage** para upload de arquivos
- **Azure Notification Hub** para push notifications
- **Firebase FCM** para notificações mobile
- **OpenAI + LangChain** para funcionalidades de IA
- **aiocache** para cache em memória
- **WebSockets** para comunicação em tempo real
- **Docker** + **Kubernetes** para deploy

## Estrutura

```
scoutplay-api/
├── app/
│   ├── main.py               # Entry point FastAPI
│   ├── config.py             # Variáveis de ambiente
│   ├── database.py           # Engine SQLAlchemy + BaseModel
│   ├── utils.py              # Auth helpers (Keycloak)
│   ├── logger.py             # Logger JSON estruturado
│   ├── context.py            # ContextVar para correlationId
│   ├── controllers/          # Routers FastAPI (um por domínio)
│   ├── models/               # SQLAlchemy ORM + Pydantic schemas
│   ├── services/             # Regras de negócio
│   │   └── utils/            # Storage, push, etc.
│   └── sockets/              # WebSocket manager + handlers
├── alembic/                  # Migrations
├── static/                   # Arquivos estáticos
├── Dockerfile
├── docker-compose.yml
├── kubernetes.yml
├── requirements.txt
└── .env.example
```

## Rodando localmente

```bash
cp .env.example .env
# edite o .env com suas credenciais

pip install -r requirements.txt

# Com SQLite (sem configurar Postgres):
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Com Docker:
docker-compose up --build
```

## Docs

Após subir: http://localhost:8000/scoutplay/docs

## Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Docker Hub

```bash
docker build --platform linux/amd64 -t syncplus/scoutplay-backend:latest .
docker push syncplus/scoutplay-backend:latest 
```
