from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#veritabanındaki dosyaların yerini belirliyoruz.  
SQLALCHEMY_DATABASE_URL = "sqlite:///./telemetry.db"

#motoru oluşturuyoruz.  
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

#veritabanı işlemleri için oturum oluşturuyoruz.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#model sınıflarımızın temelini oluşturuyoruz.
Base = declarative_base()