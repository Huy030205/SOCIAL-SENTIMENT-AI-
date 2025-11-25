# app.py
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import pipeline
from social_collector import fetch_facebook_posts, fetch_instagram_posts
import os

app = Flask(__name__)
app.secret_key = "EAATH6l0HjMoBPyhhXjODLZBZCE7xFZARfBvt7wSPkbuZAy8woQDSPJTS1xoZCXRDtZCXBmSO5ZBlnUgBKjAXtgkspUNBF0KrMKlZBOfwoaiMakWB0hIt8yGhq1dXqSs3EhZCvVNou7h3DZCJyyALc2ZCZAcOsbZC9nD82mKcD4x5Xvbjg93lbSZAhqQr0kczdcOBIw5QCEDDHrVLjoZAzatz9374wbzePP5pmSbnk6edMwdZBgZDZD"  # đổi cho bí mật hơn

DB_PATH = "users.db"

# --- Tạo DB nếu chưa có ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Khởi tạo pipeline sentiment (tải model khi lần đầu chạy) ---
# Lưu ý: lần đầu chạy sẽ tải model từ internet rồi lưu cache (chậm một chút)
sentiment = pipeline("sentiment-analysis")

# --- Helper: lấy user theo username ---
def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row  # None hoặc (id, username, password_hash)

# --- Route: Trang chính chuyển hướng theo login ---
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# --- Route: Đăng ký ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not password:
            flash("Vui lòng nhập username và password.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Mật khẩu và xác nhận không khớp.", "error")
            return render_template("register.html")

        if get_user(username):
            flash("Username đã tồn tại. Chọn tên khác.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()
        flash("Đăng ký thành công. Vui lòng đăng nhập.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# --- Route: Đăng nhập ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user(username)
        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            flash("Đăng nhập thành công.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng.", "error")
            return render_template("login.html")

    return render_template("login.html")

# --- Route: Dashboard / Phân tích cảm xúc ---
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("Vui lòng đăng nhập để truy cập.", "error")
        return redirect(url_for("login"))

    result = None
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if text:
            analysis = sentiment(text)[0]
            result = {
                "text": text,
                "label": analysis["label"],
                "score": round(analysis["score"] * 100, 2)
            }
        else:
            flash("Vui lòng nhập văn bản để phân tích.", "error")

    return render_template("dashboard.html", result=result, username=session.get("username"))

# --- Route: Đăng xuất ---
@app.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("login"))
@app.route("/collect", methods=["GET", "POST"])
def collect():
    if "user_id" not in session:
        flash("Vui lòng đăng nhập để truy cập.", "error")
        return redirect(url_for("login"))

    results = []

    if request.method == "POST":
        platform = request.form.get("platform")
        keyword = request.form.get("keyword", "").strip()

        posts = []

        # tạm thời demo: không dùng keyword, chỉ lấy vài bài gần nhất
        if platform == "facebook":
            posts = fetch_facebook_posts(limit=5)
        elif platform == "instagram":
            posts = fetch_instagram_posts(limit=5)
        # nếu chưa dùng twitter thì bỏ qua

        # chạy sentiment cho từng bài
        for p in posts:
            analysis = sentiment(p["text"])[0]
            results.append({
                "source": p["source"],
                "text": p["text"],
                "time": p["time"],
                "label": analysis["label"],
                "score": round(analysis["score"] * 100, 2),
            })

    return render_template(
        "collect.html",
        results=results,
        username=session.get("username")
    )
if __name__ == "__main__":
    # Nếu chạy trong môi trường dev, debug=True ok. Khi nộp bài/triển khai, tắt debug.
    app.run(debug=True)
