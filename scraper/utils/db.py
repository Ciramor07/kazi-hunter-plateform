from sqlalchemy import create_engine, Column, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()
DB_PATH = os.getenv("DB_PATH", "/app/data/kazi.db")

class Offer(Base):
    __tablename__ = "offers"

    id          = Column(String, primary_key=True)
    title       = Column(String)
    company     = Column(String)
    location    = Column(String)
    salary      = Column(String)
    contract    = Column(String)
    description = Column(Text)
    url         = Column(String)
    platform    = Column(String)
    score       = Column(Float, default=0.0)
    status      = Column(String, default="new")
    created_at  = Column(DateTime, default=datetime.utcnow)
    applied_at  = Column(DateTime, nullable=True)
    notes       = Column(Text, nullable=True)
    cv_path     = Column(String, nullable=True)
    lm_path     = Column(String, nullable=True)

def get_session():
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
