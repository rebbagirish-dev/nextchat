"""
NexChat - Flask Web App (Token-based auth — works on Railway/Render/etc.)
Run locally: python app.py
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import hashlib
import datetime
import os
import secrets

app = Flask(__name__)

# DB path: /tmp on Railway (writable), local folder otherwise
if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RENDER"):
    DB_PATH = "/tmp/nexchat.db"
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nexchat.db")

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
            token     TEXT,
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
    for uname, pwd in [("alice", "Shutterflies1!"), ("bob", "Shutterflies1!")]:
        pw_hash = hashlib.sha256(pwd.encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?,?)",
                  (uname, pw_hash))
    conn.commit()
    conn.close()

init_db()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def now_ts():
    return datetime.datetime.now().strftime("%H:%M")

def get_user_by_token(token):
    if not token:
        return None
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE token=?", (token,)).fetchone()
    conn.close()
    return dict(row) if row else None

def require_auth():
    token = request.headers.get("X-Auth-Token", "").strip()
    user  = get_user_by_token(token)
    if not user:
        return None, (jsonify({"ok": False, "error": "Not authenticated"}), 401)
    return user, None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/logged-out")
def logged_out():
    # Neutral landing page after logout — just serves the app shell
    # which will show the login screen since no token exists
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    try:
        data     = request.get_json(force=True, silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        if not username or not password:
            return jsonify({"ok": False, "error": "Username and password required."})
        conn = get_conn()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hash_pw(password))
        ).fetchone()
        if not user:
            conn.close()
            return jsonify({"ok": False, "error": "Invalid username or password."})
        token = secrets.token_hex(32)
        conn.execute("UPDATE users SET token=?, online=1 WHERE id=?", (token, user["id"]))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "token": token, "user_id": user["id"], "username": user["username"]})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Server error: {str(e)}"}), 500

@app.route("/logout", methods=["POST"])
def logout():
    user, _ = require_auth()
    if user:
        conn = get_conn()
        conn.execute("UPDATE users SET token=NULL, online=0, last_seen=? WHERE id=?", (now_ts(), user["id"]))
        conn.commit()
        conn.close()
    return jsonify({"ok": True})

@app.route("/api/me")
def api_me():
    user, _ = require_auth()
    if not user:
        return jsonify({"logged_in": False})
    return jsonify({"logged_in": True, "user_id": user["id"], "username": user["username"]})

@app.route("/api/other")
def api_other():
    user, err = require_auth()
    if err: return err
    conn  = get_conn()
    other = conn.execute("SELECT id, username, online, last_seen FROM users WHERE id != ?", (user["id"],)).fetchone()
    conn.close()
    return jsonify(dict(other) if other else {})

@app.route("/api/messages")
def api_messages():
    user, err = require_auth()
    if err: return err
    my_id = user["id"]
    conn  = get_conn()
    other = conn.execute("SELECT id FROM users WHERE id != ?", (my_id,)).fetchone()
    if not other:
        conn.close()
        return jsonify([])
    other_id = other["id"]
    conn.execute("UPDATE messages SET status='delivered' WHERE sender_id=? AND receiver_id=? AND status='sent'", (other_id, my_id))
    conn.execute("UPDATE messages SET status='read' WHERE sender_id=? AND receiver_id=? AND status='delivered'", (other_id, my_id))
    conn.commit()
    rows = conn.execute("""
        SELECT id, sender_id, body, timestamp, status FROM messages
        WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)
        ORDER BY id ASC
    """, (my_id, other_id, other_id, my_id)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/send", methods=["POST"])
def api_send():
    user, err = require_auth()
    if err: return err
    data = request.get_json(force=True, silent=True) or {}
    body = data.get("body", "").strip()
    if not body:
        return jsonify({"ok": False, "error": "Empty message"})
    my_id = user["id"]
    conn  = get_conn()
    other = conn.execute("SELECT id FROM users WHERE id != ?", (my_id,)).fetchone()
    if not other:
        conn.close()
        return jsonify({"ok": False})
    conn.execute("INSERT INTO messages (sender_id,receiver_id,body,timestamp,status) VALUES (?,?,?,?,'sent')",
                 (my_id, other["id"], body, now_ts()))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/clear", methods=["POST"])
def api_clear():
    user, err = require_auth()
    if err: return err
    conn = get_conn()
    conn.execute("DELETE FROM messages")
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/poll")
def api_poll():
    user, err = require_auth()
    if err: return jsonify({"logged_in": False}), 401
    my_id = user["id"]
    conn  = get_conn()
    total = conn.execute("SELECT COUNT(*) as c FROM messages").fetchone()["c"]
    other = conn.execute("SELECT online, last_seen FROM users WHERE id != ?", (my_id,)).fetchone()
    conn.close()
    return jsonify({
        "logged_in": True,
        "msg_count": total,
        "other_online": other["online"] if other else 0,
        "other_last_seen": other["last_seen"] if other else ""
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
