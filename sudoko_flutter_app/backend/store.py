import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from datetime import datetime, timezone

DATA_DIR = os.environ.get(
    "DATA_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
)
DB_PATH = os.path.join(DATA_DIR, "sudoku.db")

_SECRET = None


def init():
    """Create the data dir, tables, and load (or generate) the token secret."""
    global _SECRET
    os.makedirs(DATA_DIR, exist_ok=True)
    con = _conn()
    con.execute(
        """CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL)"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS solves(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            puzzle TEXT NOT NULL,
            solution TEXT NOT NULL)"""
    )
    con.commit()
    con.close()

    env_secret = os.environ.get("JWT_SECRET", "").strip()
    if env_secret:
        _SECRET = env_secret.encode()
    else:
        path = os.path.join(DATA_DIR, "token.secret")
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(secrets.token_hex(32))
        with open(path) as f:
            _SECRET = f.read().strip().encode()


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---- passwords ----

def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return f"{salt}${digest}"


def _verify_password(password, stored):
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return hmac.compare_digest(check, digest)


# ---- tokens (HMAC-signed, stdlib only) ----

def _b64(data):
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def issue_token(uid, username, days=180):
    payload = _b64(json.dumps(
        {"uid": uid, "username": username, "exp": int(time.time()) + days * 86400}
    ).encode())
    sig = _b64(hmac.new(_SECRET, payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def verify_token(token):
    """Return the payload dict for a valid, unexpired token; else None."""
    try:
        payload, sig = token.split(".")
        expect = _b64(hmac.new(_SECRET, payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expect):
            return None
        data = json.loads(_unb64(payload))
        if data.get("exp", 0) < time.time():
            return None
        return data
    except Exception:
        return None


# ---- users ----

def create_user(username, password):
    """Create a user; returns the new user id, or None if the name is taken."""
    con = _conn()
    try:
        cur = con.execute(
            "INSERT INTO users(username, password_hash, created_at) VALUES(?,?,?)",
            (username, _hash_password(password), _now()),
        )
        con.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        con.close()


def authenticate(username, password):
    """Return (uid, username) on success, else None."""
    con = _conn()
    row = con.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    con.close()
    if row and _verify_password(password, row["password_hash"]):
        return row["id"], row["username"]
    return None


# ---- solve history ----

def save_solve(uid, puzzle, solution):
    con = _conn()
    cur = con.execute(
        "INSERT INTO solves(user_id, created_at, puzzle, solution) VALUES(?,?,?,?)",
        (uid, _now(), json.dumps(puzzle), json.dumps(solution)),
    )
    con.commit()
    con.close()
    return cur.lastrowid


def list_solves(uid, limit=100):
    con = _conn()
    rows = con.execute(
        "SELECT id, created_at, puzzle, solution FROM solves "
        "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (uid, limit),
    ).fetchall()
    con.close()
    return [
        {
            "id": r["id"],
            "created_at": r["created_at"],
            "puzzle": json.loads(r["puzzle"]),
            "solution": json.loads(r["solution"]),
        }
        for r in rows
    ]


def delete_solve(uid, solve_id):
    con = _conn()
    cur = con.execute("DELETE FROM solves WHERE id = ? AND user_id = ?", (solve_id, uid))
    con.commit()
    con.close()
    return cur.rowcount > 0
