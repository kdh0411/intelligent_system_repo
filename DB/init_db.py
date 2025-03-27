# IS/DB/init_db.py

import sqlite3
import os

# users.db 경로 지정
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

# DB 연결
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# users 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    face_embedding TEXT  -- 추후 얼굴 임베딩 추가 (JSON 문자열 등)
)
""")

conn.commit()
conn.close()

print("✅ users.db 초기화 완료!")
