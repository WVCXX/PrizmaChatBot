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
from html import escape
def startInList(text: str, getList: list):
    if not text:
        return False, "0"
    upper = text.upper()
    for item in getList:
        if upper.startswith(item.upper()):
            return True, item
    return False, "0"
def toSymbol(text: str, symbol: str) -> str:
    return text.split(symbol, 1)[0]
def is_id(s: str) -> bool:
    if not s:
        return False
    return s.lstrip("-").isdigit()
def hlink(nick: str, user_id: int) -> str:
    safe = escape(nick or f"id{user_id}")
    return f'<a href="tg://openmessage?user_id={user_id}">{safe}</a>'