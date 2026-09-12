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
from db import get_user, create_user, update_user, find_by_username
from utils.text import is_id
async def get_or_create(tg_user) -> dict:
    data = await get_user(tg_user.id)
    if not data:
        return await create_user(tg_user)
    return await update_user(tg_user)
async def resolve_user(message, text: str = "") -> tuple[dict | None, str]:
    #Возвращает (user_data | None, остаток_строки).
    #Приоритет: reply → @username → id.
    if message.reply_to_message:
        u = message.reply_to_message.from_user
        return await get_or_create(u), text.strip()
    if not text:
        return None, ""
    parts = text.strip().split(maxsplit=1)
    target = parts[0].replace("@", "")
    rest = parts[1].strip() if len(parts) > 1 else ""
    if is_id(target):
        u = await get_user(int(target))
        return u, rest
    u = await find_by_username(target)
    return u, rest