from fastapi import FastAPI
from app.schemas import GameEvent
from fastapi import Depends
from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal

app = FastAPI(title="Game Telemetry API")

# modellerden veritabanı tabloları oluşturuyoruz.
models.Base.metadata.create_all(bind=engine)


# veritabanı oturumunu yönetmek için bir bağımlılık fonksiyonu oluşturuyoruz.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is healthy"}

@app.post("/events")
def create_event(event: GameEvent, db: Session = Depends(get_db)):
    
    # GameEvent şemasından gelen verileri alıp, SQLAlchemy modeline dönüştürüyoruz.
    db_event = models.GameEvent(**event.dict()) 
    
    # 2. bu nesneyi veritabanına ekliyoruz.
    db.add(db_event)
    
    # 3. değişiklikleri veritabanına kaydediyoruz.
    db.commit()
    
    # 4. db_event nesnesini güncel verilerle gücelliyoruz.
    db.refresh(db_event)
    # 5. başarılı bir yanıt döndürüyoruz.
    return {
        "status": "success",
        "message": "Event successfully saved to database",
        "data": db_event
    }

    