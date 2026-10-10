"""
Управление соединением SQLite и проверка состояния базы.

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
from pathlib import Path
from typing import Any
import aiosqlite
from config import DB_PATH
from .migrations import apply_migrations
_conn: aiosqlite.Connection | None = None
def get_connection() -> aiosqlite.Connection:
    if _conn is None:
        raise RuntimeError("база данных не инициализирована.")
    return _conn
async def ensure_db_schema() -> int:
    return await apply_migrations(get_connection())
async def db_healthcheck() -> dict[str, Any]:
    health: dict[str, Any] = {
        "connected": False,
        "schema_version": 0,
        "users": 0,
        "errors": [],
    }
    try:
        connection = get_connection()
        async with connection.execute("SELECT COUNT(*) FROM users") as cursor:
            users_count = await cursor.fetchone()
        async with connection.execute("PRAGMA user_version") as cursor:
            version_row = await cursor.fetchone()
        health["connected"] = True
        health["users"] = (
            int(users_count[0])
            if users_count and users_count[0] is not None
            else 0
        )
        health["schema_version"] = (
            int(version_row[0])
            if version_row and version_row[0] is not None
            else 0
        )
    except Exception as exc:
        health["errors"] = [str(exc)]
    return health
async def init_db() -> None:
    global _conn
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    _conn = await aiosqlite.connect(DB_PATH)
    _conn.row_factory = aiosqlite.Row
    await _conn.execute("PRAGMA journal_mode=WAL")
    await _conn.execute("PRAGMA synchronous=NORMAL")
    await _conn.execute("PRAGMA foreign_keys=ON")
    await ensure_db_schema()
async def close_db() -> None:
    global _conn
    if _conn is not None:
        await _conn.close()
        _conn = None