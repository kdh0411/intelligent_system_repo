import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, url_for
from face.face_save import FaceSaver
from face.face_detect import FaceDetect  
import json

# HTML 파일들이 UI 폴더 안에 있으므로 경로 지정
app = Flask(__name__, template_folder="UI")

app.secret_key = 'your_secret_key'  # 세션 사용을 위해 필요

# DB 경로
DB_PATH = os.path.join(os.path.dirname(__file__), "DB", "users.db")

# 맨 처음 화면면
@app.route("/")
def welcome():
    return render_template("welcome.html")

# ----------------- 회원가입 --------------------#
#json -> DB 읽어오기
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        student_id = request.form["student_id"]
        name = request.form["name"]
        password = request.form["password"]

        embedding = None
        temp_path = "face/temp_embedding.json"
        if os.path.exists(temp_path):
            with open(temp_path, "r", encoding="utf-8") as f:
                embedding = json.load(f)
            os.remove(temp_path)  # 등록 후 삭제

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (student_id, name, password, face_embedding)
                VALUES (?, ?, ?, ?)
            """, (
                student_id,
                name,
                password,
                json.dumps(embedding) if embedding else None
            ))
            conn.commit()
            message = f"{name}님 회원가입 완료!"
        except sqlite3.IntegrityError:
            message = "⚠️ 이미 존재하는 학번입니다."
        finally:
            conn.close()

        return render_template("register.html", message=message)

    return render_template("register.html")

# 얼굴 등록
@app.route("/register/face")
def register_face():
    saver = FaceSaver()
    embedding = saver.register_face()
    if embedding is not None:
        with open("face/temp_embedding.json", "w", encoding="utf-8") as f:
            json.dump(embedding.tolist(), f)
    return redirect(url_for("register", face="success"))


# --------------- 로그인 -------------------# 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        student_id = request.form["student_id"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE student_id = ? AND password = ?", (student_id, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect(url_for("main", student_id=student_id))
        else:
            return render_template("login.html", message="⚠️ 로그인 정보가 올바르지 않습니다.")

    return render_template("login.html")

# 얼굴인식 로그인
@app.route("/login/face")
def login_face():
    detector = FaceDetect()
    student_id = detector.recognize_face()

    if student_id == "No Match":
        return "😥 얼굴 인식 실패! 등록된 얼굴이 없습니다."
    else:
        return redirect(url_for("main", student_id=student_id))
    


# --------------- 로그인 후 메인(기능 선택)-------------------# 
@app.route("/main")
def main():
    student_id = request.args.get("student_id")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()

    name = result[0] if result else "사용자"

    return render_template("main.html", student_id=student_id, name=name)

# --------------- 기능-------------------# 

# ---------------챗봇--------------------#
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    response = ""
    if request.method == "POST":
        user_input = request.form["user_input"]

        # ✅ 간단한 rule 기반 응답
        if "대출" in user_input:
            response = "📚 도서는 최대 14일 동안 대출할 수 있어요."
        elif "연장" in user_input:
            response = "⏱️ 도서 연장은 1회 가능하며, 연장 시 추가 7일이 제공됩니다."
        elif "반납" in user_input:
            response = "📮 반납은 무인 반납함 또는 안내 데스크를 이용해주세요."
        elif "연체" in user_input:
            response = "⚠️ 연체 시 하루 100원의 연체료가 부과됩니다."
        elif "도서관" in user_input or "운영 시간" in user_input:
            response = "🕐 도서관은 평일 09:00~22:00, 주말 10:00~18:00 운영됩니다."
        else:
            response = "죄송해요, 이해하지 못했어요. '대출', '반납', '연장' 등으로 다시 물어보세요!"

    return render_template("chatbot.html", response=response)





# 서버 실행
if __name__ == "__main__":
    app.run(debug=True)
