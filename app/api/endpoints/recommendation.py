from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import sys

# 상위 폴더 절대 경로를 sys에 추가해 모듈 탐색
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.database import SessionLocal
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation import get_hybrid_recommendation

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/recommend", response_model=RecommendationResponse)
def generate_recommendations(req: RecommendationRequest, db: Session = Depends(get_db)):
    """
    고객의 취향 설문(tags)과 특이사항을 받아
    추천 결과(Gemini LLM 랭킹 결과 및 기본 리스트)를 반환하는 엔드포인트
    """
    try:
        result = get_hybrid_recommendation(
            db=db,
            region=req.region,
            user_tags=req.user_tags,
            special_request=req.special_request
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 에러 발생: {str(e)}")
