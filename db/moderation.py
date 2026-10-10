"""
Операции с модерацией, действиями и заметками.

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
import datetime
from typing import Any
from .connection import get_connection
async def log_action(
    chat_id: int,
    moder_id: int,
    target_id: int,
    action: str,
    duration: str = "",
    reason: str = "",
) -> None:
    connection = get_connection()
    await connection.execute(
        "INSERT INTO actions (chat_id, moder_id, target_id, action, duration, reason) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (chat_id, moder_id, target_id, action, duration, reason),
    )
    await connection.commit()
async def moder_stats(moder_id: int) -> dict[str, int]:
    connection = get_connection()
    stats: dict[str, int] = {}
    for action in ("mute", "unmute", "warn", "ban", "kick"):
        async with connection.execute(
            "SELECT COUNT(*) AS c FROM actions WHERE moder_id=? AND action=?",
            (moder_id, action),
        ) as cursor:
            row = await cursor.fetchone()
            stats[action] = row["c"]
    return stats
async def add_mute(
    target_id: int,
    chat_id: int,
    until: str,
    reason: str = "",
) -> None:
    connection = get_connection()
    await connection.execute(
        "INSERT OR REPLACE INTO mutes (target_id, chat_id, until, reason) "
        "VALUES (?, ?, ?, ?)",
        (target_id, chat_id, until, reason),
    )
    await connection.commit()
async def remove_mute(target_id: int) -> None:
    connection = get_connection()
    await connection.execute("DELETE FROM mutes WHERE target_id=?", (target_id,))
    await connection.commit()
async def active_mutes() -> list[dict[str, Any]]:
    connection = get_connection()
    now = datetime.datetime.now().isoformat()
    async with connection.execute(
        "SELECT * FROM mutes WHERE until IS NOT NULL AND until > ?",
        (now,),
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
async def add_note(user_id: int, author_id: int, text: str) -> None:
    connection = get_connection()
    await connection.execute(
        "INSERT INTO notes (user_id, author_id, text) VALUES (?, ?, ?)",
        (user_id, author_id, text),
    )
    await connection.commit()
async def get_notes(user_id: int) -> list[dict[str, Any]]:
    connection = get_connection()
    async with connection.execute(
        "SELECT * FROM notes WHERE user_id=? ORDER BY ts DESC", (user_id,)
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
