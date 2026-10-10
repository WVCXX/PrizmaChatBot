"""
Операции с инвентарём экономики.

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
async def inv_add(user_id: int, code: str, qty: int = 1) -> None:
    connection = get_connection()
    await connection.execute(
        "INSERT INTO inventory (user_id, item_code, qty) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, item_code) DO UPDATE SET qty = qty + ?",
        (user_id, code, qty, qty),
    )
    await connection.commit()
async def inv_remove(user_id: int, code: str, qty: int = 1) -> bool:
    connection = get_connection()
    async with connection.execute(
        "SELECT qty FROM inventory WHERE user_id=? AND item_code=?",
        (user_id, code),
    ) as cursor:
        row = await cursor.fetchone()
    if not row or row["qty"] < qty:
        return False
    await connection.execute(
        "UPDATE inventory SET qty = qty - ? WHERE user_id=? AND item_code=?",
        (qty, user_id, code),
    )
    await connection.commit()
    return True
async def inv_all(user_id: int) -> list[dict[str, Any]]:
    connection = get_connection()
    async with connection.execute(
        "SELECT * FROM inventory WHERE user_id=? AND qty>0 ORDER BY item_code",
        (user_id,),
    ) as cursor:
        return [dict(row) for row in await cursor.fetchall()]
