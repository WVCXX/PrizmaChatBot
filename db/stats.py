"""
Операции с накопленной статистикой чатов.

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
async def track_message_stat(chat_id: int, date: str, hour: int) -> None:
    connection = get_connection()
    await connection.execute(
        "INSERT INTO message_stats (chat_id, date, hour, count) VALUES (?, ?, ?, 1) "
        "ON CONFLICT(chat_id, date, hour) DO UPDATE SET count = count + 1",
        (chat_id, date, hour),
    )
    await connection.commit()
async def stats_hour(chat_id: int, date: str) -> list[dict[str, Any]]:
    connection = get_connection()
    async with connection.execute(
        "SELECT hour, count FROM message_stats "
        "WHERE chat_id=? AND date=? ORDER BY hour",
        (chat_id, date),
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
async def stats_day(
    chat_id: int,
    days: int = 14,
) -> list[dict[str, Any]]:
    since = (datetime.date.today() - datetime.timedelta(days=days - 1)).isoformat()
    connection = get_connection()
    async with connection.execute(
        "SELECT date, SUM(count) AS total FROM message_stats "
        "WHERE chat_id=? AND date>=? GROUP BY date ORDER BY date",
        (chat_id, since),
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
async def stats_week(
    chat_id: int,
    weeks: int = 8,
) -> list[dict[str, Any]]:
    since = (datetime.date.today() - datetime.timedelta(weeks=weeks)).isoformat()
    connection = get_connection()
    async with connection.execute(
        "SELECT strftime('%Y-W%W', date) AS wk, SUM(count) AS total "
        "FROM message_stats WHERE chat_id=? AND date>=? "
        "GROUP BY wk ORDER BY wk",
        (chat_id, since),
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
async def stats_month(
    chat_id: int,
    months: int = 6,
) -> list[dict[str, Any]]:
    since = (datetime.date.today() - datetime.timedelta(days=months * 31)).isoformat()
    connection = get_connection()
    async with connection.execute(
        "SELECT strftime('%Y-%m', date) AS mo, SUM(count) AS total "
        "FROM message_stats WHERE chat_id=? AND date>=? "
        "GROUP BY mo ORDER BY mo",
        (chat_id, since),
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
async def stats_all(chat_id: int) -> dict[str, Any]:
    connection = get_connection()
    async with connection.execute(
        "SELECT COUNT(*) AS days, SUM(count) AS total, "
        "MIN(date) AS first, MAX(date) AS last "
        "FROM message_stats WHERE chat_id=?",
        (chat_id,),
    ) as cursor:
        row = await cursor.fetchone()
    return dict(row) if row else {}
