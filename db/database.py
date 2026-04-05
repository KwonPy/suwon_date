from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 초기 MVP용 SQLite / 이후 추후 PostgreSQL 전환 가능하도록 설정
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./suwon_date.db")

# SQLite 사용 시 스레드 설정 추가
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
