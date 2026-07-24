from fastapi import APIRouter, Depends, Path, Query, status
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
def get_events(
    skip: int = Query(
        default=0,
        ge=0,
        description="Atlanacak kayıt sayısı",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Döndürülecek en fazla kayıt sayısı",
    ),
    db: Session = Depends(get_db),
):
    total = db.query(models.GameEvent).count()

    events = (
        db.query(models.GameEvent)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return{
        "status": "success",
        "total": total,
        "count": len(events),
        "skip": skip,
        "limit": limit,
        "data": events
    }


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
def get_events_by_user(
    user_id: str = Path(
        ...,
        min_length=1,
        description="Olayları getirilecek kullanıcı ID'si",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Atlanacak kayıt sayısı",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Döndürülecek en fazla kayıt sayısı",
    ),
    db: Session = Depends(get_db),
):
    user_events_query = db.query(models.GameEvent).filter(models.GameEvent.user_id == user_id)

    total = user_events_query.count()

    events = (
        user_events_query
        .order_by(models.GameEvent.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "status": "success",
        "user_id": user_id,
        "total": total,
        "count": len(events),
        "skip": skip,
        "limit": limit,
        "data": events
    }