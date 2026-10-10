"""
Операции с сохранёнными цитатами.

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
from .connection import get_connection
async def add_quote(user_id: int, text: str, saved_by: int) -> int:
    connection = get_connection()
    cursor = await connection.execute(
        "INSERT INTO quotes (user_id, text, saved_by) VALUES (?, ?, ?)",
        (user_id, text, saved_by),
    )
    await connection.commit()
    if cursor.lastrowid is None:
        raise RuntimeError("не удалось получить ID сохранённой цитаты")
    return cursor.lastrowid
async def get_quote(quote_id: int) -> dict[str, Any] | None:
    connection = get_connection()
    async with connection.execute(
        "SELECT * FROM quotes WHERE id=?",
        (quote_id,),
    ) as cursor:
        row = await cursor.fetchone()
    return dict(row) if row else None
async def delete_quote(quote_id: int) -> bool:
    connection = get_connection()
    cursor = await connection.execute("DELETE FROM quotes WHERE id=?", (quote_id,))
    await connection.commit()
    return cursor.rowcount > 0
async def random_quote() -> dict[str, Any] | None:
    connection = get_connection()
    async with connection.execute(
        "SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1"
    ) as cursor:
        row = await cursor.fetchone()
    return dict(row) if row else None
async def quotes_by_user(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    connection = get_connection()
    async with connection.execute(
        "SELECT * FROM quotes WHERE user_id=? ORDER BY ts DESC, id DESC "
        "LIMIT ? OFFSET ?",
        (user_id, limit, offset),
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
async def count_quotes_by_user(user_id: int) -> int:
    connection = get_connection()
    async with connection.execute(
        "SELECT COUNT(*) FROM quotes WHERE user_id=?",
        (user_id,),
    ) as cursor:
        row = await cursor.fetchone()
    return int(row[0]) if row else 0
