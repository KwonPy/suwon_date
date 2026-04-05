import json
import os
import sys

# 상위 폴더(app, db, models 등)를 인식할 수 있도록 sys.path 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal, engine, Base
from models.place import Place

def init_db():
    # 데이터베이스 테이블 생성 (없는 경우)
    print("데이터베이스 테이블을 생성합니다...")
    Base.metadata.create_all(bind=engine)

def seed_data():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'mock_places.json')
    
    if not os.path.exists(json_path):
        print(f"데이터 파일이 없습니다: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        places_data = json.load(f)

    db = SessionLocal()
    
    try:
        # 기존 데이터 날리기 (멱등성을 위해 초기화 후 삽입)
        print("기존 장소 데이터를 초기화합니다...")
        db.query(Place).delete()
        
        # 데이터 삽입
        print("가상 데이터 시딩(Seeding)을 시작합니다...")
        inserted_count = 0
        for p in places_data:
            new_place = Place(
                name=p.get('name'),
                address=p.get('address'),
                category=p.get('category'),
                theme_keywords=p.get('tags')
            )
            db.add(new_place)
            inserted_count += 1
            
        db.commit()
        print(f"성공! 총 {inserted_count}개의 장소 데이터가 DB에 삽입되었습니다.")
        
    except Exception as e:
        db.rollback()
        print(f"에러가 발생했습니다: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    seed_data()
