from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings

# motoru oluşturuyoruz.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

# veritabanı işlemleri için oturum oluşturuyoruz.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# model sınıflarımızın temelini oluşturuyoruz.
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
