from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# 프론트엔드 UI를 백엔드와 연동하여 하나의 서버에서 서빙 (All-in-One)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")
