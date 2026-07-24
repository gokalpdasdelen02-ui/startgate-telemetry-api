from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

#tüm rotaların başına /events ekleyen kod
router = APIRouter(
    prefix="/events",
    tags=["Events"]
)

#prefix kullandığımız için /events yazmak yerine / yazabiliyoruz.
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_event(event: schemas.GameEvent, db: Session = Depends(get_db)):
    db_event = models.GameEvent(**event.model_dump()) #kullandığın veri doğrulama kütüphanesi olan Pydantic'in yeni versiyonunda dict() metodunun kullanımdan kaldırılmış olmasıdır.
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {
        "status": "success",
        "message": "Event successfully saved to database.",
        "data": db_event
    }

@router.get("/", status_code=status.HTTP_200_OK)
def get_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    events = db.query(models.GameEvent).offset(skip).limit(limit).all()
    return {
        "status": "success",
        "count": len(events),
        "skip": skip,
        "limit": limit,
        "data": events
    }

@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
def get_events_by_user(user_id: str, db: Session = Depends(get_db)):
    events = db.query(models.GameEvent).filter(models.GameEvent.user_id == user_id).all()
    return{
        "status": "success",
        "user_id": user_id,
        "total_events": len(events),
        "data": events
    }
