// 사용자의 추천 파라미터 상태 기록
let selection = {
    region: null,
    user_tags: [],
    special_request: ""
};

// 지역 카드 버튼 (단일 선택 로직)
document.querySelectorAll('#region-group .card-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('#region-group .card-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        selection.region = btn.dataset.value;
    });
});

// 태그 알약 버튼 (다중 선택 광역 로직 - 5단계 모두 관할)
document.querySelectorAll('.pill-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        btn.classList.toggle('selected');
        // 선택되면 배열에 추가, 취소되면 배열에서 제외
        if (btn.classList.contains('selected')) {
            selection.user_tags.push(btn.dataset.value);
        } else {
            selection.user_tags = selection.user_tags.filter(t => t !== btn.dataset.value);
        }
    });
});

// 화면(view) 전환 애니메이션 함수
function nextView(viewId) {
    // 1. 현재 떠있는 모든 뷰를 페이드아웃 처리
    document.querySelectorAll('.view').forEach(v => {
        v.classList.remove('active');
        setTimeout(() => v.style.display = 'none', 400); // CSS 트랜지션 타임 0.4s 대기
    });
    
    // 2. 다음 뷰 띄우기 (타이밍 맞춤)
    setTimeout(() => {
        const next = document.getElementById(viewId);
        next.style.display = 'flex';
        // HTML 렌더 트리 적용을 위해 살짝 늦게 active 추가 (페이드인 촉발)
        setTimeout(() => next.classList.add('active'), 50);
    }, 400);
}

// 백엔드 API에 POST 요청 후 파이널 결과 띄우기
async function submitCuration() {
    selection.special_request = document.getElementById('special-request').value;
    
    // 로딩 스크린 넘어가기
    nextView('view-loading');

    try {
        // FastAPI 서버로 POST 요청 (유동 호스팅을 위한 상대경로)
        const response = await fetch('/api/v1/recommendations/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(selection)
        });
        
        const data = await response.json();
        
        // 결과 출력 포맷팅 (모드 분기)
        let finalHTML = "";

        if (data.mode === "keyword_only" && data.candidates) {
            // Track B: 키워드 기반 카드 결과
            finalHTML = `<p style="margin-bottom:20px; opacity:0.85;">${data.message}</p>`;
            data.candidates.forEach((place, i) => {
                finalHTML += `
                <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.12); border-radius:14px; padding:18px 22px; margin-bottom:14px; backdrop-filter:blur(8px);">
                    <h3 style="margin:0 0 6px; font-size:1.15rem;">📍 ${i+1}. ${place.name}</h3>
                    <p style="margin:4px 0; opacity:0.7; font-size:0.9rem;">카테고리: ${place.category}</p>
                    <p style="margin:4px 0; opacity:0.7; font-size:0.9rem;">키워드: ${place.tags || "없음"}</p>
                    <p style="margin:4px 0; opacity:0.55; font-size:0.8rem;">매칭 점수: ${(place.score * 100).toFixed(0)}%</p>
                </div>`;
            });
        } else if (data.llm_recommendation) {
            // Track A: LLM 스토리텔링 결과
            finalHTML = data.llm_recommendation;
        } else if (data.detail) {
            finalHTML = "오류: " + data.detail;
        } else {
            finalHTML = data.message || "추천 결과를 불러오지 못했습니다.";
        }

        document.getElementById('llm-text').innerHTML = finalHTML;
        nextView('view-result');
        
    } catch (error) {
        console.error("API 연동 에러", error);
        document.getElementById('llm-text').innerText = "서버 통신에 실패했습니다.\n백엔드(FastAPI)가 포트 8000에서 켜져 있는지 확인해주세요!\n\n상세에러: " + error.message;
        nextView('view-result');
    }
}

