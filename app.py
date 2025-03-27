from flask import Flask, render_template, request

# HTML 파일들이 UI 폴더 안에 있으므로 경로 지정
app = Flask(__name__, template_folder="UI")

# 맨 처음 화면면
@app.route("/")
def welcome():
    return render_template("welcome.html")

# ----------------- 회원가입 --------------------#
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        student_id = request.form["student_id"]
        password = request.form["password"]
        print(f"[회원가입] 이름: {name}, 학번: {student_id}")
        return "회원가입 완료!"  # 임시 메시지 (나중에 리디렉션/DB 저장 예정)
    return render_template("register.html")

# 📸 얼굴 등록 페이지 (캠 연동 예정)
@app.route("/register/face")
def register_face():
    return "얼굴 등록 페이지 (추후 캠 연동)"

# --------------- 로그인 -------------------# 
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login/face")
def login_face():
    return "얼굴 인식 로그인 (캠 연동 예정)"

@app.route("/login/id", methods=["GET", "POST"])
def login_id():
    return "학번/비밀번호 로그인 (폼 입력 예정)"




# 서버 실행
if __name__ == "__main__":
    app.run(debug=True)
