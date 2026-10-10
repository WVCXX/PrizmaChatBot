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
import os
from dotenv import load_dotenv
load_dotenv()
def parse_admin_ids(raw_value: str | None) -> list[int]:
    if raw_value is None:
        return []
    result: list[int] = []
    for item in str(raw_value).split(","):
        value = item.strip()
        if not value:
            continue
        try:
            result.append(int(value))
        except ValueError:
            continue
    return result
def parse_log_channel_id(raw_value: str | None) -> int | None:
    value = (raw_value or "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env")
ADMIN_IDS = parse_admin_ids(os.getenv("ADMIN_IDS"))
if not ADMIN_IDS:
    raise RuntimeError("ADMIN_IDS пуст — добавь хотя бы одного админа в .env")
LOG_CHANNEL_ID = parse_log_channel_id(os.getenv("LOG_CHANNEL_ID"))
PROXY_URL = (os.getenv("PROXY_URL") or "").strip() or None
SETTINGS_FILE = "settings.json"
DB_PATH = "data/iris.db"
CHATS_DIR = "chats"
os.makedirs("data", exist_ok=True)
os.makedirs("data/backups", exist_ok=True)
os.makedirs(CHATS_DIR, exist_ok=True)