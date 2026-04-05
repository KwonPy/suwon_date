import pytest
from fastapi.testclient import TestClient
import sys
import os

# app 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_health_check():
    """
    서버 초기화 및 기본 라우팅 검증 
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Suwon Date Curator FastAPI is happily running!"}

def test_recommendation_missing_body():
    """
    POST Request Body 누락 시 Pydantic 검증 에러(422) 발생 확인
    """
    response = client.post("/api/v1/recommendations/recommend")
    assert response.status_code == 422
