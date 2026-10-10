"""
Операции с пользователями и их репутацией.

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
from typing import Any
from aiogram.types import User
from .connection import get_connection
ALLOWED_FIELDS = {
    "rank", "reputation", "varn", "balance", "bank",
    "nick", "custom_nick", "username", "last_daily",
    "last_rob", "daily_streak",
    "last_rep_given_to", "last_rep_time", "messages",
}
async def get_user(user_id: int) -> dict[str, Any] | None:
    connection = get_connection()
    async with connection.execute("SELECT * FROM users WHERE id=?", (user_id,)) as cursor:
        row = await cursor.fetchone()
    return dict(row) if row else None
async def ensure_admin(user_id: int, rank: int = 5) -> None:
    connection = get_connection()
    await connection.execute(
        "INSERT OR IGNORE INTO users (id, nick) VALUES (?, ?)",
        (user_id, f"id{user_id}"),
    )
    await connection.execute(
        "UPDATE users SET rank=? WHERE id=? AND rank<?",
        (rank, user_id, rank),
    )
    await connection.commit()
async def create_user(user: User) -> dict[str, Any]:
    connection = get_connection()
    await connection.execute(
        "INSERT OR IGNORE INTO users (id, username, nick) VALUES (?, ?, ?)",
        (user.id, user.username, user.full_name),
    )
    await connection.commit()
    result = await get_user(user.id)
    if result is None:
        raise RuntimeError("не удалось создать пользователя в базе данных")
    return result
async def update_user(user: User) -> dict[str, Any]:
    data = await get_user(user.id)
    if not data:
        return await create_user(user)
    new_nick = user.full_name if not data["custom_nick"] else data["nick"]
    connection = get_connection()
    await connection.execute(
        "UPDATE users SET username=?, nick=? WHERE id=?",
        (user.username, new_nick, user.id),
    )
    await connection.commit()
    result = await get_user(user.id)
    if result is None:
        raise RuntimeError("не удалось обновить пользователя в базе данных")
    return result
async def set_field(user_id: int, field: str, value: Any) -> None:
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    connection = get_connection()
    await connection.execute(
        f"UPDATE users SET {field}=? WHERE id=?", (value, user_id)
    )
    await connection.commit()
async def inc_field(user_id: int, field: str, delta: int = 1) -> None:
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    connection = get_connection()
    await connection.execute(
        f"UPDATE users SET {field}={field}+? WHERE id=?", (delta, user_id)
    )
    await connection.commit()
async def all_users() -> list[dict[str, Any]]:
    connection = get_connection()
    async with connection.execute("SELECT * FROM users") as cursor:
        return [dict(row) for row in await cursor.fetchall()]
async def find_by_username(username: str) -> dict[str, Any] | None:
    username = username.replace("@", "").strip()
    connection = get_connection()
    async with connection.execute(
        "SELECT * FROM users WHERE LOWER(username)=LOWER(?)", (username,)
    ) as cursor:
        row = await cursor.fetchone()
    return dict(row) if row else None
async def find_by_nick(nick: str) -> dict[str, Any] | None:
    connection = get_connection()
    async with connection.execute("SELECT * FROM users WHERE nick=?", (nick,)) as cursor:
        row = await cursor.fetchone()
    return dict(row) if row else None
async def top_by(
    field: str,
    limit: int = 10,
    min_value: int = 1,
    offset: int = 0,
) -> list[dict[str, Any]]:
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    connection = get_connection()
    async with connection.execute(
        f"SELECT * FROM users WHERE {field} >= ? ORDER BY {field} DESC, id ASC "
        "LIMIT ? OFFSET ?",
        (min_value, limit, offset),
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
async def count_by(field: str, min_value: int = 1) -> int:
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")
    connection = get_connection()
    async with connection.execute(
        f"SELECT COUNT(*) FROM users WHERE {field} >= ?",
        (min_value,),
    ) as cursor:
        row = await cursor.fetchone()
    return int(row[0]) if row else 0
async def log_rep(from_id: int, to_id: int, delta: int) -> None:
    connection = get_connection()
    await connection.execute(
        "INSERT INTO reputation_log (from_id, to_id, delta) VALUES (?, ?, ?)",
        (from_id, to_id, delta),
    )
    await connection.commit()
async def rep_history(to_id: int, limit: int = 10) -> list[dict[str, Any]]:
    connection = get_connection()
    async with connection.execute(
        "SELECT * FROM reputation_log WHERE to_id=? ORDER BY ts DESC LIMIT ?",
        (to_id, limit),
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
