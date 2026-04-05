from sqlalchemy import Column, Integer, String, Float, Text
from db.database import Base

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    address = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False) # 카페, 음식점, 문화공간 등
    theme_keywords = Column(String(200))          # "조용한,로맨틱,사진찍기좋은" 형태 혹은 JSON
