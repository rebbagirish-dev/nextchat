"""
NexChat - Flask Web App
Run locally: python app.py
Deploy: Railway / Render / PythonAnywhere
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import hashlib
import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nexchat-secret-key-change-in-prod")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nexchat.db")

# ── DB helpers ─────────────────────────────────────────────────────────────────

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY,
            username  TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            online    INTEGER DEFAULT 0,
            last_seen TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id   INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            body        TEXT NOT NULL,
            timestamp   TEXT NOT NULL,
            status      TEXT DEFAULT 'sent'
        );
    """)
    for uname, pwd in [("Alice", "alice123"), ("Bob", "bob123")]:
        pw_hash = hashlib.sha256(pwd.encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?,?)",
                  (uname, pw_hash))
    conn.commit()
    conn.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def now_ts():
    return datetime.datetime.now().strftime("%H:%M")

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        conn = get_conn()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hash_pw(password))
        ).fetchone()
        conn.close()
        if user:
            session["user_id"]   = user["id"]
            session["username"]  = user["username"]
            # mark online
            conn = get_conn()
            conn.execute("UPDATE users SET online=1 WHERE id=?", (user["id"],))
            conn.commit()
            conn.close()
            return jsonify({"ok": True, "username": user["username"]})
        return jsonify({"ok": False, "error": "Invalid username or password."})
    return render_template("index.html")

@app.route("/logout", methods=["POST"])
def logout():
    if "user_id" in session:
        conn = get_conn()
        conn.execute(
            "UPDATE users SET online=0, last_seen=? WHERE id=?",
            (now_ts(), session["user_id"])
        )
        conn.commit()
        conn.close()
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/me")
def api_me():
    if "user_id" not in session:
        return jsonify({"logged_in": False})
    return jsonify({"logged_in": True, "user_id": session["user_id"],
                    "username": session["username"]})

@app.route("/api/other")
def api_other():
    if "user_id" not in session:
        return jsonify({}), 401
    conn = get_conn()
    other = conn.execute(
        "SELECT id, username, online, last_seen FROM users WHERE id != ?",
        (session["user_id"],)
    ).fetchone()
    conn.close()
    if not other:
        return jsonify({})
    return jsonify(dict(other))

@app.route("/api/messages")
def api_messages():
    if "user_id" not in session:
        return jsonify([]), 401
    my_id = session["user_id"]
    conn = get_conn()
    # find other user id
    other = conn.execute("SELECT id FROM users WHERE id != ?", (my_id,)).fetchone()
    if not other:
        conn.close()
        return jsonify([])
    other_id = other["id"]

    # mark their messages as delivered (I'm online & fetching)
    conn.execute(
        "UPDATE messages SET status='delivered' WHERE sender_id=? AND receiver_id=? AND status='sent'",
        (other_id, my_id)
    )
    # mark their messages as read (I'm viewing the chat)
    conn.execute(
        "UPDATE messages SET status='read' WHERE sender_id=? AND receiver_id=? AND status='delivered'",
        (other_id, my_id)
    )
    conn.commit()

    rows = conn.execute("""
        SELECT id, sender_id, body, timestamp, status FROM messages
        WHERE (sender_id=? AND receiver_id=?)
           OR (sender_id=? AND receiver_id=?)
        ORDER BY id ASC
    """, (my_id, other_id, other_id, my_id)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/send", methods=["POST"])
def api_send():
    if "user_id" not in session:
        return jsonify({"ok": False}), 401
    data = request.get_json()
    body = data.get("body", "").strip()
    if not body:
        return jsonify({"ok": False, "error": "Empty message"})
    my_id = session["user_id"]
    conn = get_conn()
    other = conn.execute("SELECT id FROM users WHERE id != ?", (my_id,)).fetchone()
    if not other:
        conn.close()
        return jsonify({"ok": False})
    conn.execute(
        "INSERT INTO messages (sender_id,receiver_id,body,timestamp,status) VALUES (?,?,?,?,'sent')",
        (my_id, other["id"], body, now_ts())
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/clear", methods=["POST"])
def api_clear():
    if "user_id" not in session:
        return jsonify({"ok": False}), 401
    conn = get_conn()
    conn.execute("DELETE FROM messages")
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/poll")
def api_poll():
    """Lightweight endpoint: returns message count + other user status."""
    if "user_id" not in session:
        return jsonify({}), 401
    my_id = session["user_id"]
    conn = get_conn()
    count = conn.execute(
        "SELECT COUNT(*) as c FROM messages WHERE sender_id != ? OR receiver_id != ?",
        (my_id, my_id)   # just total count is fine
    ).fetchone()["c"]
    other = conn.execute(
        "SELECT online, last_seen FROM users WHERE id != ?", (my_id,)
    ).fetchone()
    conn.close()
    return jsonify({
        "msg_count": count,
        "other_online": other["online"] if other else 0,
        "other_last_seen": other["last_seen"] if other else ""
    })

# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
