from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db.database import Base

class UserRecommendationLog(Base):
    __tablename__ = "user_recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_identifier = Column(String(100), index=True)  # 세션 ID 혹은 식별자
    keywords_requested = Column(String(200))           # 요청된 키워드
    budget = Column(Integer, nullable=True)            # 최대 예산
    created_at = Column(DateTime(timezone=True), server_default=func.now())
