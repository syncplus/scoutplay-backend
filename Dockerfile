FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ENV MAX_WORKERS=1
ENV APP_MODULE=app.main:app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app
COPY ./static /app/static
COPY ./static /static
