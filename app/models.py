from sqlalchemy import Column, Integer, String, DateTime
import datetime
from .database import Base
from sqlalchemy import Column, Integer, String, JSON

class GameEvent(Base):
    # veritabanındaki tablo adı
    __tablename__ = "events"

    # oluşturduğumuz tablonun kolonları
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    category = Column(String, index=True)
    event_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    session_id = Column(String, index=True, nullable=True)
    platform = Column(String, index=True, nullable=True)
    session_num = Column(Integer, nullable=True)
    os_version = Column(String, nullable=True)
    sdk_version = Column(String, nullable=True)
    device = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    client_ts = Column(Integer, nullable=True)
    v = Column(String, nullable=True)