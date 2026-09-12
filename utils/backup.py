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
import shutil
import datetime
from config import DB_PATH, CHATS_DIR
def backup():
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    dst = f"data/backups/{ts}"
    os.makedirs(dst, exist_ok=True)
    if os.path.exists(DB_PATH):
        shutil.copy(DB_PATH, f"{dst}/iris.db")
    if os.path.exists(CHATS_DIR):
        shutil.make_archive(f"{dst}/chats", "zip", CHATS_DIR)
    backups = sorted(os.listdir("data/backups"))
    for old in backups[:-7]:
        shutil.rmtree(f"data/backups/{old}", ignore_errors=True)