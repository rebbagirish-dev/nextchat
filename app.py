"""
NexChat - Flask Web App
Uses PostgreSQL when DATABASE_URL env var is set, SQLite otherwise.
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import hashlib, datetime, os, secrets

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB max per request

# ── DB backend selection ───────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL:
    try:
        import psycopg2
        import psycopg2.extras

        def get_conn():
            conn = psycopg2.connect(DATABASE_URL, sslmode="require")
            return conn

        def get_cursor(conn):
            return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        PG = True
    except ImportError:
        DATABASE_URL = ""  # fallback to SQLite
        PG = False

if not DATABASE_URL:
    # SQLite (Railway / local)
    import sqlite3
    DB_PATH = "/tmp/nexchat.db" if os.environ.get("RAILWAY_ENVIRONMENT") \
              else os.path.join(os.path.dirname(os.path.abspath(__file__)), "nexchat.db")

    def get_conn():
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def get_cursor(conn):
        return conn.cursor()

    PG = False

# ── DB init ────────────────────────────────────────────────────────────────────

def init_db():
    conn = get_conn()
    cur  = get_cursor(conn)

    if PG:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          SERIAL PRIMARY KEY,
                username    TEXT UNIQUE NOT NULL,
                password    TEXT NOT NULL,
                token       TEXT,
                online      INTEGER DEFAULT 0,
                last_seen   TEXT,
                typing      INTEGER DEFAULT 0,
                last_active TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id          SERIAL PRIMARY KEY,
                sender_id   INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                body        TEXT NOT NULL,
                timestamp   TEXT NOT NULL,
                status      TEXT DEFAULT 'sent'
            )
        """)
        # Seed users
        for uname, pwd in [("alice", "Shutterflies1!"), ("bob", "Shutterflies1!")]:
            pw_hash = hashlib.sha256(pwd.encode()).hexdigest()
            cur.execute("""
                INSERT INTO users (username, password)
                VALUES (%s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (uname, pw_hash))
    else:
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY,
                username    TEXT UNIQUE NOT NULL,
                password    TEXT NOT NULL,
                token       TEXT,
                online      INTEGER DEFAULT 0,
                last_seen   TEXT,
                typing      INTEGER DEFAULT 0,
                last_active TEXT
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
            cur.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?,?)",
                        (uname, pw_hash))
        # Migrations
        for sql in [
            "ALTER TABLE users ADD COLUMN typing INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN last_active TEXT",
        ]:
            try: cur.execute(sql)
            except: pass

    conn.commit()
    cur.close()
    conn.close()

init_db()

# ── Query helpers ──────────────────────────────────────────────────────────────

def ph(n=1):
    """Return placeholder: %s for PG, ? for SQLite."""
    return "%s" if PG else "?"

def phs(n):
    """Return n placeholders comma-separated."""
    p = "%s" if PG else "?"
    return ",".join([p]*n)

def qfetch(sql, params=()):
    conn = get_conn()
    cur  = get_cursor(conn)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in rows]

def qfetchone(sql, params=()):
    conn = get_conn()
    cur  = get_cursor(conn)
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close(); conn.close()
    return dict(row) if row else None

def qexec(sql, params=()):
    conn = get_conn()
    cur  = get_cursor(conn)
    cur.execute(sql, params)
    conn.commit()
    cur.close(); conn.close()

def qexec_many(sqls_params):
    conn = get_conn()
    cur  = get_cursor(conn)
    for sql, params in sqls_params:
        cur.execute(sql, params)
    conn.commit()
    cur.close(); conn.close()

# ── Helpers ────────────────────────────────────────────────────────────────────

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def now_ts():
    ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    return datetime.datetime.now(ist).strftime("%I:%M %p")

def now_dt():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def is_active(last_active_str, threshold=10):
    if not last_active_str:
        return False
    try:
        last = datetime.datetime.strptime(str(last_active_str)[:19], "%Y-%m-%d %H:%M:%S")
        return (datetime.datetime.utcnow() - last).total_seconds() < threshold
    except:
        return False

def get_user_by_token(token):
    if not token:
        return None
    p = ph()
    return qfetchone(f"SELECT * FROM users WHERE token={p}", (token,))

def require_auth():
    token = request.headers.get("X-Auth-Token", "").strip()
    user  = get_user_by_token(token)
    if not user:
        return None, (jsonify({"ok": False, "error": "Not authenticated"}), 401)
    return user, None

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json", mimetype="application/manifest+json")

@app.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/keep-alive")
def keep_alive():
    return jsonify({"status": "alive"}), 200

@app.route("/logged-out")
def logged_out():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    try:
        data     = request.get_json(force=True, silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        if not username or not password:
            return jsonify({"ok": False, "error": "Username and password required."})
        p    = ph()
        user = qfetchone(
            f"SELECT * FROM users WHERE username={p} AND password={p}",
            (username, hash_pw(password))
        )
        if not user:
            return jsonify({"ok": False, "error": "Invalid username or password."})
        token = secrets.token_hex(32)
        qexec(f"UPDATE users SET token={p}, online=1, last_active={p} WHERE id={p}",
              (token, now_dt(), user["id"]))
        return jsonify({"ok": True, "token": token, "user_id": user["id"], "username": user["username"]})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Server error: {str(e)}"}), 500

@app.route("/logout", methods=["POST"])
def logout():
    user, _ = require_auth()
    if user:
        p = ph()
        qexec(f"UPDATE users SET token=NULL, online=0, typing=0, last_active=NULL, last_seen={p} WHERE id={p}",
              (now_ts(), user["id"]))
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
    p     = ph()
    other = qfetchone(
        f"SELECT id, username, last_seen, last_active FROM users WHERE id != {p}",
        (user["id"],)
    )
    if not other:
        return jsonify({})
    return jsonify({
        "id":        other["id"],
        "username":  other["username"],
        "online":    1 if is_active(other["last_active"]) else 0,
        "last_seen": other["last_seen"] or "",
    })

@app.route("/api/messages")
def api_messages():
    user, err = require_auth()
    if err: return err
    my_id = user["id"]
    p     = ph()
    other = qfetchone(f"SELECT id FROM users WHERE id != {p}", (my_id,))
    if not other:
        return jsonify([])
    other_id = other["id"]
    # Mark incoming messages as delivered (not read — read only on explicit view)
    qexec(f"UPDATE messages SET status='delivered' WHERE sender_id={p} AND receiver_id={p} AND status='sent'",
          (other_id, my_id))
    rows = qfetch(f"""
        SELECT id, sender_id, body, timestamp, status FROM messages
        WHERE (sender_id={p} AND receiver_id={p}) OR (sender_id={p} AND receiver_id={p})
        ORDER BY id ASC
    """, (my_id, other_id, other_id, my_id))
    return jsonify(rows)

@app.route("/api/send", methods=["POST"])
def api_send():
    user, err = require_auth()
    if err: return err
    data = request.get_json(force=True, silent=True) or {}
    body = data.get("body", "")
    # Don't strip image data; strip only text messages
    if not body.startswith("[IMG]"):
        body = body.strip()
    if not body:
        return jsonify({"ok": False, "error": "Empty message"})
    my_id = user["id"]
    p     = ph()
    other = qfetchone(f"SELECT id FROM users WHERE id != {p}", (my_id,))
    if not other:
        return jsonify({"ok": False})
    qexec(
        f"INSERT INTO messages (sender_id,receiver_id,body,timestamp,status) VALUES ({phs(5)})",
        (my_id, other["id"], body, now_ts(), "sent")
    )
    return jsonify({"ok": True})

@app.route("/api/typing", methods=["POST"])
def api_typing():
    user, err = require_auth()
    if err: return err
    data   = request.get_json(force=True, silent=True) or {}
    typing = 1 if data.get("typing") else 0
    p      = ph()
    qexec(f"UPDATE users SET typing={p} WHERE id={p}", (typing, user["id"]))
    return jsonify({"ok": True})

@app.route("/api/poll")
def api_poll():
    user, err = require_auth()
    if err: return jsonify({"logged_in": False}), 401
    my_id = user["id"]
    p     = ph()
    qexec(f"UPDATE users SET last_active={p}, online=1 WHERE id={p}", (now_dt(), my_id))
    total = qfetchone("SELECT COUNT(*) as c FROM messages")["c"]
    other = qfetchone(f"SELECT last_seen, typing, last_active FROM users WHERE id != {p}", (my_id,))
    return jsonify({
        "logged_in":       True,
        "msg_count":       total,
        "other_online":    1 if (other and is_active(other["last_active"])) else 0,
        "other_last_seen": other["last_seen"] if other else "",
        "other_typing":    other["typing"]    if other else 0,
    })

@app.route("/api/clear", methods=["POST"])
def api_clear():
    user, err = require_auth()
    if err: return err
    qexec("DELETE FROM messages")
    return jsonify({"ok": True})

@app.route("/api/logout-beacon", methods=["POST"])
def api_logout_beacon():
    token = request.args.get("token", "").strip()
    user  = get_user_by_token(token)
    if user:
        p = ph()
        qexec(f"UPDATE users SET token=NULL, online=0, typing=0, last_active=NULL, last_seen={p} WHERE id={p}",
              (now_ts(), user["id"]))
    return "", 204

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
