from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import require_api_key

from loguru import logger

router = APIRouter(
    prefix="/stats",
    tags=["Statistics"],
    dependencies=[Depends(require_api_key)],
)


@router.get(
    "/daily-events",
    status_code=status.HTTP_200_OK,
    response_model=schemas.DailyEventStatsResponse,
)
def get_daily_event_counts(db: Session = Depends(get_db)):
    event_date = func.date(models.GameEvent.timestamp)

    try:
        daily_counts = (
            db.query(
                event_date.label("date"),
                func.count(models.GameEvent.id).label("event_count"),
            )
            .group_by(event_date)
            .order_by(event_date.asc())
            .all()
        )

        logger.bind(
            daily_count=len(daily_counts),
            total_events=sum(row.event_count for row in daily_counts),
        ).info("daily_event_stats_queried")

    except SQLAlchemyError as exc:
        db.rollback()

        logger.bind(
            operation="get_daily_event_counts",
        ).exception("database_error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Daily event statistics could not be retrieved from the database.",
        ) from exc

    return {
        "status": "success",
        "data": [
            {
                "date": row.date,
                "event_count": row.event_count,
            }
            for row in daily_counts
        ],
    }


@router.get(
    "/active-users",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ActiveUserStatsResponse,
)
def get_active_user_count(
    date_from: datetime | None = Query(
        default=None,
        description="Bu tarih ve sonrasında etkinlik gönderen kullanıcıları dahil eder.",
    ),
    date_to: datetime | None = Query(
        default=None,
        description="Bu tarih ve öncesinde etkinlik gönderen kullanıcıları dahil eder.",
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
            detail="date_from, date_to değerinden sonra olamaz.",
        )

    try:
        active_users_query = db.query(
            func.count(func.distinct(models.GameEvent.user_id))
        )

        if date_from is not None:
            active_users_query = active_users_query.filter(
                models.GameEvent.timestamp >= date_from
            )

        if date_to is not None:
            active_users_query = active_users_query.filter(
                models.GameEvent.timestamp <= date_to
            )

        active_users = active_users_query.scalar() or 0

        logger.bind(
            date_from=date_from.isoformat() if date_from is not None else None,
            date_to=date_to.isoformat() if date_to is not None else None,
            active_users=active_users,
        ).info("active_user_stats_queried")

    except SQLAlchemyError as exc:
        db.rollback()

        logger.bind(
            operation="get_active_user_count",
            date_from=date_from.isoformat() if date_from is not None else None,
            date_to=date_to.isoformat() if date_to is not None else None,
        ).exception("database_error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Active user statistics could not be retrieved from the database.",
        ) from exc

    return {
        "status": "success",
        "active_users": active_users,
    }
