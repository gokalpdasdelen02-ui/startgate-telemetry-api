from datetime import datetime, timezone
from sqlalchemy import JSON, Column, DateTime, Integer, String
from .database import Base


class GameEvent(Base):
    __tablename__ = "game_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        String,
        index=True,
        nullable=False,
    )

    category = Column(
        String,
        index=True,
        nullable=False,
    )

    event_data = Column(
        JSON,
        nullable=False,
    )

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    session_id = Column(
        String,
        index=True,
        nullable=False,
    )

    platform = Column(
        String,
        index=True,
        nullable=False,
    )

    session_num = Column(
        Integer,
        nullable=False,
    )

    os_version = Column(
        String,
        nullable=False,
    )

    sdk_version = Column(
        String,
        nullable=False,
    )

    device = Column(
        String,
        nullable=False,
    )

    manufacturer = Column(
        String,
        nullable=False,
    )

    client_ts = Column(
        Integer,
        nullable=False,
    )

    v = Column(
        String,
        nullable=False,
    )


