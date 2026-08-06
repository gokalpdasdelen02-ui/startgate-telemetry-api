from typing import Literal
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.security import require_api_key

EventCategory = Literal[
    "business",
    "progression",
    "design",
    "resource",
    "error",
    "user",
    "session_end",
    "ad",
    "impression",
    "info",
]

# tüm rotaların başına /events ekleyen kod
router = APIRouter(
    prefix="/events", tags=["Events"], dependencies=[Depends(require_api_key)]
)


# prefix kullandığımız için /events yazmak yerine / yazabiliyoruz.
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.EventCreateResponse,
)
def create_event(event: schemas.GameEvent, db: Session = Depends(get_db)):
    db_event = models.GameEvent(**event.model_dump())

    try:
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        logger.bind(
            event_id=db_event.id,
            category=db_event.category,
        ).info("event_created")

    except SQLAlchemyError as exc:
        db.rollback()

        logger.bind(
            operation="create_event",
            category=event.category,
        ).exception("database_error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Event could not be saved to database.",
        ) from exc

    return {
        "status": "success",
        "message": "Event successfully saved to database.",
        "data": db_event,
    }


@router.post(
    "/batch",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.BatchEventCreateResponse,
)
def create_events_batch(
    batch: schemas.BatchEventCreateRequest,
    db: Session = Depends(get_db),
):
    db_events = [models.GameEvent(**event.model_dump()) for event in batch.events]

    try:
        db.add_all(db_events)
        db.commit()

        for db_event in db_events:
            db.refresh(db_event)

        logger.bind(
            event_count=len(db_events),
            event_ids=[db_event.id for db_event in db_events],
        ).info("batch_events_created")

    except SQLAlchemyError as exc:
        db.rollback()

        logger.bind(
            operation="create_events_batch",
            event_count=len(batch.events),
        ).exception("database_error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Events could not be saved to database",
        ) from exc

    return {
        "status": "success",
        "message": "Events successfully saved to database.",
        "created_count": len(db_events),
        "data": db_events,
    }


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.EventListResponse,
)
def get_events(
    category: EventCategory | None = Query(
        default=None,
        description="Filtrelenecek etkinlik kategorisi",
    ),
    date_from: datetime | None = Query(
        default=None,
        description="Bu tarih ve sonrasındaki etkinlikleri getirir.",
    ),
    date_to: datetime | None = Query(
        default=None,
        description="Bu tarih ve öncesindeki etkinlikleri getirir.",
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

    if date_from is not None:
        if date_from.tzinfo is None:
            date_from = date_from.replace(tzinfo=timezone.utc)
        else:
            date_from = date_from.astimezone(timezone.utc)

    if date_to is not None:
        if date_to.tzinfo is None:
            date_to = date_to.replace(tzinfo=timezone.utc)
        else:
            date_to = date_to.astimezone(timezone.utc)
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="date_from date_to değerinden sonra olamaz.",
        )
    try:
        events_query = db.query(models.GameEvent)

        if category is not None:
            events_query = events_query.filter(models.GameEvent.category == category)

        if date_from is not None:
            events_query = events_query.filter(models.GameEvent.timestamp >= date_from)

        if date_to is not None:
            events_query = events_query.filter(models.GameEvent.timestamp <= date_to)

        total = events_query.count()

        events = (
            events_query.order_by(models.GameEvent.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        logger.bind(
            category=category,
            date_from=date_from.isoformat() if date_from is not None else None,
            date_to=date_to.isoformat() if date_to is not None else None,
            skip=skip,
            limit=limit,
            total=total,
            result_count=len(events),
        ).info("events_queried")

    except SQLAlchemyError as exc:
        db.rollback()

        logger.bind(
            operation="get_events",
            category=category,
            date_from=date_from.isoformat() if date_from is not None else None,
            date_to=date_to.isoformat() if date_to is not None else None,
            skip=skip,
            limit=limit,
        ).exception("database_error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Events could not be retrieved from the database.",
        ) from exc

    return {
        "status": "success",
        "total": total,
        "count": len(events),
        "skip": skip,
        "limit": limit,
        "data": events,
    }


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserEventListResponse,
)
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
    try:
        user_events_query = db.query(models.GameEvent).filter(
            models.GameEvent.user_id == user_id
        )

        total = user_events_query.count()

        events = (
            user_events_query.order_by(models.GameEvent.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        logger.bind(
            user_id=user_id,
            skip=skip,
            limit=limit,
            total=total,
            result_count=len(events),
        ).info("user_events_queried")

    except SQLAlchemyError as exc:
        db.rollback()

        logger.bind(
            operation="get_events_by_user",
            user_id=user_id,
            skip=skip,
            limit=limit,
        ).exception("database_error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User events could not be retrieved from the database.",
        ) from exc

    return {
        "status": "success",
        "user_id": user_id,
        "total": total,
        "count": len(events),
        "skip": skip,
        "limit": limit,
        "data": events,
    }
