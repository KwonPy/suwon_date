from pydantic import BaseModel
from typing import List, Optional

class CandidateItem(BaseModel):
    name: str
    category: str
    score: float

class RecommendationRequest(BaseModel):
    region: Optional[str] = None
    user_tags: List[str] = []
    special_request: Optional[str] = None

class RecommendationResponse(BaseModel):
    status: Optional[str] = None
    llm_recommendation: Optional[str] = None
    message: Optional[str] = None
    candidates: Optional[List[CandidateItem]] = None
    base_candidates: Optional[List[CandidateItem]] = None
    error: Optional[str] = None
