import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models.place import Place

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_hybrid_recommendation(db: Session, region: str, user_tags: list, special_request: str):
    """
    Step 1: 지역 기반 하드 필터링
    Step 2: TF-IDF & 코사인 유사도 태그 벡터 매칭
    Step 3: Gemini 1.5 Flash LLM을 활용한 파이널 재랭킹 및 커스텀 코스 생성
    """
    # 1. DB 필터링 (Hard Filtering)
    query = db.query(Place)
    if region:
        query = query.filter(Place.address.like(f"%{region}%") | Place.name.like(f"%{region}%"))
    places = query.all()

    if not places:
        return {"error": "해당 권역에 일치하는 장소가 없습니다.", "results": []}

    # 2. Vector Similarity (태그 기반 추출)
    if not user_tags:
        user_tags = ["상관없음"]
        
    user_tag_str = " ".join(user_tags)
    # 콤마로 구분된 태그를 띄어쓰기 기준으로 처리하기 위해 치환
    docs = [p.theme_keywords.replace(",", " ") if p.theme_keywords else "" for p in places]
    docs.append(user_tag_str)
    
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform(docs)
        # 마지막 입력(사용자 태그)과 앞의 전체 장소들을 코사인 유사도로 평가
        cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
    except ValueError:
        # 단어가 전혀 매칭되지 않거나 어휘사전이 비어있는 경우
        cosine_sim = [0.0] * len(places)
        
    place_scores = [(place, cosine_sim[idx]) for idx, place in enumerate(places)]
    # 점수가 높은 순으로 정렬
    place_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 상위 10개 예비 후보군 추출
    top_10 = place_scores[:10]
    
    # 3. LLM Reranking (Gemini 1.5 Flash)
    if not GEMINI_API_KEY or not special_request:
        return {
            "status": "success",
            "message": "Gemini API 키가 설정되지 않았거나 특이사항이 없어 베이스 유사도 결과를 반환합니다.",
            "candidates": [{"name": p.name, "category": p.category, "tags": p.theme_keywords, "score": round(score, 2)} for p, score in top_10[:3]]
        }
        
    # 상위 10개 정보를 프롬프트로 쓸 수 있게 포맷팅
    candidates_info = "\n".join([f"- {p.name} [{p.category}] (특징: {p.theme_keywords})" for p, score in top_10])
    
    prompt = f"""
    너는 수원 지역 데이트 코스를 전문적으로 계획하는 최고의 데이트 큐레이터 AI야.
    아래에 사용자의 객관식 설문조사 취향을 수치적으로 계산하여 가장 어울리는 상위 10개의 핫플레이스 예비 후보를 뽑아뒀어:
    {candidates_info}

    이 사용자는 "특이사항/추가 요구사항"으로 아래와 같이 남겼어:
    "{special_request}"

    너의 임무:
    1. 사용자의 특이사항을 완벽하게 반영할 수 있도록, 위 10개의 후보 중에서 가장 잘 어울리는 장소를 딱 3곳만 선별해줘.
    2. 가능하면 식당, 카페, 문화/산책로 등 카테고리 밸런스를 맞춰서 하루 데이트가 되게 짜주면 좋아.
    3. 로맨틱하고 친절한 말투로, 왜 이 장소들을 골랐는지 사용자의 특이사항과 엮어서 설명해줘.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        llm_text = response.text
    except Exception as e:
        llm_text = f"API 호출 중 문제가 발생했습니다: {str(e)}"
        
    return {
        "status": "success",
        "llm_recommendation": llm_text,
        "base_candidates": [{"name": p.name, "category": p.category, "score": round(score, 2)} for p, score in top_10]
    }
