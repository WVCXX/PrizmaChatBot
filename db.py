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
CREATE INDEX IF NOT EXISTS idx_actions_moder ON actions(moder_id);
CREATE INDEX IF NOT EXISTS idx_actions_target ON actions(target_id);
CREATE INDEX IF NOT EXISTS idx_rep_to ON reputation_log(to_id);
"""
ALLOWED_FIELDS = {
    "rank", "reputation", "varn", "balance", "bank",
    "nick", "custom_nick", "username", "last_daily",
    "last_rep_given_to", "last_rep_time", "messages",
}
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.executescript(SCHEMA)
        await db.commit()
#юзеры
async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None
async def create_user(user) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (id, username, nick) VALUES (?, ?, ?)",
            (user.id, user.username, user.full_name),
        )
        await db.commit()
    return await get_user(user.id)
async def update_user(user) -> dict:
    data = await get_user(user.id)
    if not data:
        return await create_user(user)
    new_nick = user.full_name if not data["custom_nick"] else data["nick"]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET username=?, nick=? WHERE id=?",
            (user.username, new_nick, user.id),
        )
        await db.commit()
    return await get_user(user.id)
async def set_field(user_id: int, field: str, value):
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field}=? WHERE id=?", (value, user_id))
        await db.commit()
async def inc_field(user_id: int, field: str, delta: int = 1):
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE users SET {field}={field}+? WHERE id=?", (delta, user_id)
        )
        await db.commit()
async def all_users() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cur:
            return [dict(r) for r in await cur.fetchall()]
async def find_by_username(username: str) -> dict | None:
    username = username.replace("@", "").strip()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE LOWER(username)=LOWER(?)", (username,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None
async def top_by(field: str, limit: int = 10, min_value: int = 1) -> list[dict]:
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            f"SELECT * FROM users WHERE {field} >= ? ORDER BY {field} DESC LIMIT ?",
            (min_value, limit),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]
#действия
async def log_action(chat_id: int, moder_id: int, target_id: int,
                     action: str, duration: str = "", reason: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO actions (chat_id, moder_id, target_id, action, duration, reason) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (chat_id, moder_id, target_id, action, duration, reason),
        )
        await db.commit()
async def moder_stats(moder_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        stats = {}
        for action in ("mute", "unmute", "warn", "ban", "kick"):
            async with db.execute(
                "SELECT COUNT(*) as c FROM actions WHERE moder_id=? AND action=?",
                (moder_id, action),
            ) as cur:
                row = await cur.fetchone()
                stats[action] = row["c"]
        return stats
#муты
async def add_mute(target_id: int, chat_id: int, until: str, reason: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO mutes (target_id, chat_id, until, reason) "
            "VALUES (?, ?, ?, ?)",
            (target_id, chat_id, until, reason),
        )
        await db.commit()
async def remove_mute(target_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM mutes WHERE target_id=?", (target_id,))
        await db.commit()
async def active_mutes() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM mutes") as cur:
            return [dict(r) for r in await cur.fetchall()]
#
async def add_note(user_id: int, author_id: int, text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO notes (user_id, author_id, text) VALUES (?, ?, ?)",
            (user_id, author_id, text),
        )
        await db.commit()
async def get_notes(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM notes WHERE user_id=? ORDER BY ts DESC", (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]
#репутация
async def log_rep(from_id: int, to_id: int, delta: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO reputation_log (from_id, to_id, delta) VALUES (?, ?, ?)",
            (from_id, to_id, delta),
        )
        await db.commit()
async def rep_history(to_id: int, limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM reputation_log WHERE to_id=? ORDER BY ts DESC LIMIT ?",
            (to_id, limit),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]
#цитаты
async def add_quote(user_id: int, text: str, saved_by: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO quotes (user_id, text, saved_by) VALUES (?, ?, ?)",
            (user_id, text, saved_by),
        )
        await db.commit()
async def random_quote() -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1") as cur:
            row = await cur.fetchone()
            return dict(row) if row else None
async def quotes_by_user(user_id: int, limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM quotes WHERE user_id=? ORDER BY ts DESC LIMIT ?",
            (user_id, limit),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]