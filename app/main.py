from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.endpoints import recommendation

app = FastAPI(title="수원 데이트 큐레이터 MVP API Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 연결 영역
app.include_router(recommendation.router, prefix="/api/v1/recommendations", tags=["Recommendations"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Suwon Date Curator FastAPI is happily running!"}
