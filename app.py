import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, url_for, jsonify,Response
from face.face_save import FaceSaver
from face.face_detect import FaceDetect  
import json
from chatbot.chatbot_guide import LibraryGuideBot
from book.crawling import BookCrawler
import cv2
from threading import Event
from functools import wraps  
from datetime import timedelta
from book.summary import BookDetailExtractor
from robot.robot_controller import (
    send_goal_to_bookshelf,
    send_goal_to_table_or_home
)# 로봇 임시
import subprocess

# HTML 파일들이 UI 폴더 안에 있으므로 경로 지정
app = Flask(__name__, template_folder="UI", static_folder="UI/static")

app.permanent_session_lifetime = timedelta(minutes=5) #로그인 5분 타이머머

app.secret_key = 'your_secret_key'  # 세션 사용을 위해 필요

# DB 경로
DB_PATH = os.path.join(os.path.dirname(__file__), "DB", "users.db")

# 세션 기반 로그인 체크용 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# 맨 처음 화면면
@app.route("/")
def home():
    return redirect("/login")  # 바로 로그인 페이지로 이동


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
            os.remove(temp_path)

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

        return redirect("/login")

    return render_template("register.html")


#얼굴등록 라우트 - 비동기
@app.route("/register/face/save/ajax", methods=["POST"])
def register_face_save_ajax():
    global latest_frame

    if latest_frame is None:
        return jsonify({"success": False, "error": "캠 프레임 없음"})

    saver = FaceSaver()
    embedding = saver.extract_embedding(latest_frame)

    if embedding is None:
        return jsonify({"success": False, "error": "얼굴을 인식하지 못했습니다."})

    with open("face/temp_embedding.json", "w", encoding="utf-8") as f:
        json.dump(embedding.tolist(), f)

    return jsonify({"success": True})


#---------수동 로그아웃------------#
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --------------- 로그인 -------------------# 
# --------------- 학번 로그인 -------------------# 
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
            session.permanent = True
            session["student_id"] = student_id
            return redirect(url_for("main"))
        else:
            return render_template("login.html", message="⚠️ 로그인 정보가 올바르지 않습니다.")

    return render_template("login.html")

# --------------- 얼굴인식 로그인 -------------------# 


# 얼굴 인식기 전역 인스턴스
face_detector = FaceDetect()
latest_frame = None  
stop_event = Event()
# 캠스트림
@app.route("/face_stream")
def face_stream():
    def generate_frames():
        global latest_frame
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while True:
            success, frame = camera.read()
            if not success:
                break
            latest_frame = frame.copy()  # 💡 여기서 최신 프레임 저장
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        camera.release()
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

#캠 종료
@app.route("/stop_stream", methods=["POST"])
def stop_stream():
    stop_event.set()
    return jsonify({"stopped": True})

#얼굴 인식 라우팅
@app.route("/detect_face", methods=["POST"])
def detect_face():
    global latest_frame
    if latest_frame is None:
        return jsonify({"success": False, "error": "프레임 없음"})

    result = face_detector.recognize_face_from_frame(latest_frame)

    if result.get("match"):
        session.permanent = True
        session["student_id"] = result["student_id"]
        return jsonify({"success": True, "student_id": result["student_id"]})
    else:
        return jsonify({"success": False, "progress": result.get("progress", 0)})


# --------------- 로그인 후 메인(기능 선택)-------------------# 
@app.route("/main")
@login_required
def main():
    student_id = session["student_id"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()

    name = result[0] if result else "사용자"

    return render_template("main.html", student_id=student_id, name=name)

# --------------- 기능-------------------# 

# ---------------챗봇--------------------#
bot = LibraryGuideBot()

@app.route("/chat_guide", methods=["GET"])
@login_required
def chat_guide():
    return render_template("chat_guide.html")

@app.route("/chat_guide_api", methods=["POST"])
@login_required
def chat_guide_api():
    data = request.get_json()
    query = data.get("query", "").strip()
    
    if not query:
        return jsonify({"response": "⚠️ 질문이 비어 있습니다."})

    bot_response = bot.ask(query)
    return jsonify({"response": bot_response})

# ---------------도서 검색-----------------#
@app.route("/book", methods=["GET", "POST"])
@login_required
def book_search():
    book_info = None
    summary = None  # 요약은 무조건 초기화

    if request.method == "POST":
        regno = request.form.get("regno", "").strip()
        title = request.form.get("title", "").strip()
        crawler = BookCrawler()

        if regno:
            book_info = crawler.get_book_info_by_regno(regno)
        elif title:
            book_info = crawler.get_book_info_by_title(title)

        # ⚠️ 검색 결과 없으면 오류 표시
        if not book_info or book_info.get("오류"):
            book_info = {"오류": "❗ 검색 결과가 없습니다."}
            session["book_info"] = None
        else:
            session["book_info"] = book_info

    return render_template("book_search.html", book_info=book_info, summary=summary)



# ----------------도서 요약 -----------------#
@app.route("/book/summary", methods=["POST"])
@login_required
def book_summary():
    rno = request.form.get("rno")
    extractor = BookDetailExtractor()

    if rno:
        summary_data = extractor.get_details_by_rno(rno)

        # 📛 요약 결과가 진짜 하나도 없으면 사용자에게 안내
        if not summary_data or all(not v.strip() for v in summary_data.values()):
            summary_data = {"오류": "❗ 이 도서는 상세 서지 정보가 제공되지 않습니다."}
    else:
        summary_data = {"오류": "❗ 상세 정보를 찾을 수 없습니다 (rno 없음)."}

    return render_template("book_search.html", book_info=session.get("book_info"), summary=summary_data)

#---------로봇 제어 ------------#

# --------------- 로봇 호출 제어 페이지 -------------------#
@app.route("/robot_call", methods=["GET"])
@login_required
def robot_call():
    return render_template("robot_call.html")

#---------로봇 주행 ------------#
@app.route("/call_robot", methods=["POST"])
@login_required
def call_robot():
    data = request.get_json()
    print("[DEBUG] 받은 데이터:", data)

    if not data or "zone" not in data:
        return jsonify({"success": False, "message": "❗ zone 값이 없습니다."}), 400

    zone = data["zone"]

    if zone in {"1번", "2번", "3번", "4번"}:
        success, message = send_goal_to_bookshelf(zone)
    elif zone in {"shelf1", "shelf2", "shelf3", "shelf4", "home"}:
        success, message = send_goal_to_table_or_home(zone)
    else:
        success, message = False, "❌ 알 수 없는 zone입니다."

    return jsonify({"success": success, "message": message}), (200 if success else 400)

# 서버 실행
if __name__ == "__main__":
    app.run(debug=True)
