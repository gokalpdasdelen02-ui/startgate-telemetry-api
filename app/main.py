from fastapi import FastAPI, status
from app.database import engine
from app.logging_config import setup_logging
from app import models
from app.routers import events, stats

setup_logging()

app = FastAPI(title="Game Telemetry API")

models.Base.metadata.create_all(
    bind=engine
)  # modellerden veri tabanı oluşturmamızı sağlayn kod.

app.include_router(
    events.router
)  # events.py dosyasındaki router'ı ana uygulamaya ekliyoruz.

app.include_router(stats.router)
# stats.py dosyasındaki router'ı ana uygulamaya ekliyoruz.


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok", "message": "Service is healthy."}
