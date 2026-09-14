"""
Prizma — Telegram bot for Prizma chat
Copyright (C) 2026 WVCXX

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import aiosqlite
import datetime
from config import DB_PATH
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    username    TEXT,
    nick        TEXT,
    custom_nick INTEGER DEFAULT 0,
    rank        INTEGER DEFAULT 0,
    reputation  INTEGER DEFAULT 0,
    varn        INTEGER DEFAULT 0,
    balance     INTEGER DEFAULT 0,
    bank        INTEGER DEFAULT 0,
    last_daily  TEXT,
    last_rep_given_to INTEGER,
    last_rep_time     TEXT,
    joined_at   TEXT DEFAULT CURRENT_TIMESTAMP,
    messages    INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS actions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP,
    chat_id   INTEGER,
    moder_id  INTEGER,
    target_id INTEGER,
    action    TEXT,
    duration  TEXT,
    reason    TEXT
);
CREATE TABLE IF NOT EXISTS mutes (
    target_id INTEGER PRIMARY KEY,
    chat_id   INTEGER,
    until     TEXT,
    reason    TEXT
);
CREATE TABLE IF NOT EXISTS notes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER,
    author_id INTEGER,
    text      TEXT,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS quotes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER,
    text      TEXT,
    saved_by  INTEGER,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS reputation_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP,
    from_id   INTEGER,
    to_id     INTEGER,
    delta     INTEGER
);
CREATE TABLE IF NOT EXISTS warnings_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP,
    moder_id  INTEGER,
    target_id INTEGER,
    delta     INTEGER,
    reason    TEXT
);
CREATE TABLE IF NOT EXISTS achievements (
    user_id  INTEGER,
    code     TEXT,
    ts       TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, code)
);
CREATE INDEX IF NOT EXISTS idx_users_rank ON users(rank);
CREATE INDEX IF NOT EXISTS idx_users_rep ON users(reputation);
CREATE INDEX IF NOT EXISTS idx_users_nick ON users(nick);
CREATE INDEX IF NOT EXISTS idx_actions_moder ON actions(moder_id);
CREATE INDEX IF NOT EXISTS idx_actions_target ON actions(target_id);
CREATE INDEX IF NOT EXISTS idx_rep_to ON reputation_log(to_id);
"""
ALLOWED_FIELDS = {
    "rank", "reputation", "varn", "balance", "bank",
    "nick", "custom_nick", "username", "last_daily",
    "last_rep_given_to", "last_rep_time", "messages",
}
_conn: aiosqlite.Connection | None = None
async def init_db():
    global _conn
    _conn = await aiosqlite.connect(DB_PATH)
    _conn.row_factory = aiosqlite.Row
    await _conn.execute("PRAGMA journal_mode=WAL")
    await _conn.execute("PRAGMA synchronous=NORMAL")
    await _conn.execute("PRAGMA foreign_keys=ON")
    await _conn.executescript(SCHEMA)
    await _conn.commit()
async def close_db():
    global _conn
    if _conn is not None:
        await _conn.close()
        _conn = None
#юзеры
async def get_user(user_id: int) -> dict | None:
    async with _conn.execute("SELECT * FROM users WHERE id=?", (user_id,)) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None
async def ensure_admin(user_id: int, rank: int = 5):
    await _conn.execute(
        "INSERT OR IGNORE INTO users (id, nick) VALUES (?, ?)",
        (user_id, f"id{user_id}"),
    )
    await _conn.execute(
        "UPDATE users SET rank=? WHERE id=? AND rank<?",
        (rank, user_id, rank),
    )
    await _conn.commit()
async def create_user(user) -> dict:
    await _conn.execute(
        "INSERT OR IGNORE INTO users (id, username, nick) VALUES (?, ?, ?)",
        (user.id, user.username, user.full_name),
    )
    await _conn.commit()
    return await get_user(user.id)
async def update_user(user) -> dict:
    data = await get_user(user.id)
    if not data:
        return await create_user(user)
    new_nick = user.full_name if not data["custom_nick"] else data["nick"]
    await _conn.execute(
        "UPDATE users SET username=?, nick=? WHERE id=?",
        (user.username, new_nick, user.id),
    )
    await _conn.commit()
    return await get_user(user.id)
async def set_field(user_id: int, field: str, value):
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    await _conn.execute(f"UPDATE users SET {field}=? WHERE id=?", (value, user_id))
    await _conn.commit()
async def inc_field(user_id: int, field: str, delta: int = 1):
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    await _conn.execute(
        f"UPDATE users SET {field}={field}+? WHERE id=?", (delta, user_id)
    )
    await _conn.commit()
async def all_users() -> list[dict]:
    async with _conn.execute("SELECT * FROM users") as cur:
        return [dict(r) for r in await cur.fetchall()]
async def find_by_username(username: str) -> dict | None:
    username = username.replace("@", "").strip()
    async with _conn.execute(
        "SELECT * FROM users WHERE LOWER(username)=LOWER(?)", (username,)
    ) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None
async def find_by_nick(nick: str) -> dict | None:
    async with _conn.execute("SELECT * FROM users WHERE nick=?", (nick,)) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None
async def top_by(field: str, limit: int = 10, min_value: int = 1) -> list[dict]:
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    async with _conn.execute(
        f"SELECT * FROM users WHERE {field} >= ? ORDER BY {field} DESC LIMIT ?",
        (min_value, limit),
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]
#действия
async def log_action(chat_id: int, moder_id: int, target_id: int,
                     action: str, duration: str = "", reason: str = ""):
    await _conn.execute(
        "INSERT INTO actions (chat_id, moder_id, target_id, action, duration, reason) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (chat_id, moder_id, target_id, action, duration, reason),
    )
    await _conn.commit()
async def moder_stats(moder_id: int) -> dict:
    stats = {}
    for action in ("mute", "unmute", "warn", "ban", "kick"):
        async with _conn.execute(
            "SELECT COUNT(*) as c FROM actions WHERE moder_id=? AND action=?",
            (moder_id, action),
        ) as cur:
            row = await cur.fetchone()
            stats[action] = row["c"]
    return stats
#муты
async def add_mute(target_id: int, chat_id: int, until: str, reason: str = ""):
    await _conn.execute(
        "INSERT OR REPLACE INTO mutes (target_id, chat_id, until, reason) "
        "VALUES (?, ?, ?, ?)",
        (target_id, chat_id, until, reason),
    )
    await _conn.commit()
async def remove_mute(target_id: int):
    await _conn.execute("DELETE FROM mutes WHERE target_id=?", (target_id,))
    await _conn.commit()
async def active_mutes() -> list[dict]:
    async with _conn.execute("SELECT * FROM mutes") as cur:
        return [dict(r) for r in await cur.fetchall()]
#
async def add_note(user_id: int, author_id: int, text: str):
    await _conn.execute(
        "INSERT INTO notes (user_id, author_id, text) VALUES (?, ?, ?)",
        (user_id, author_id, text),
    )
    await _conn.commit()
async def get_notes(user_id: int) -> list[dict]:
    async with _conn.execute(
        "SELECT * FROM notes WHERE user_id=? ORDER BY ts DESC", (user_id,)
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]
#репутация
async def log_rep(from_id: int, to_id: int, delta: int):
    await _conn.execute(
        "INSERT INTO reputation_log (from_id, to_id, delta) VALUES (?, ?, ?)",
        (from_id, to_id, delta),
    )
    await _conn.commit()
async def rep_history(to_id: int, limit: int = 10) -> list[dict]:
    async with _conn.execute(
        "SELECT * FROM reputation_log WHERE to_id=? ORDER BY ts DESC LIMIT ?",
        (to_id, limit),
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]
#цитаты
async def add_quote(user_id: int, text: str, saved_by: int):
    await _conn.execute(
        "INSERT INTO quotes (user_id, text, saved_by) VALUES (?, ?, ?)",
        (user_id, text, saved_by),
    )
    await _conn.commit()
async def random_quote() -> dict | None:
    async with _conn.execute(
        "SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1"
    ) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None
async def quotes_by_user(user_id: int, limit: int = 20) -> list[dict]:
    async with _conn.execute(
        "SELECT * FROM quotes WHERE user_id=? ORDER BY ts DESC LIMIT ?",
        (user_id, limit),
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]