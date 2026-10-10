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
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import sys
from db import db_healthcheck
from functions_settings import load_settings
from version import __version__, __build_date__, __author__
router = Router()
@router.message(Command("version", "версия", "v"))
async def cmd_version(message: Message):
    await message.answer(
        f"🤖 <b>Iris</b> — Telegram bot for Prizma\n"
        f"\n"
        f"Версия: <code>{__version__}</code>\n"
        f"Сборка: <code>{__build_date__}</code>\n"
        f"Автор: {__author__}\n"
        f"Python: <code>{sys.version.split()[0]}</code>",
        parse_mode="HTML",
    )
@router.message(Command("health", "здоровье", "status"))
async def cmd_health(message: Message):
    db_state = await db_healthcheck()
    settings_ok = False
    settings_error = ""
    try:
        load_settings()
        settings_ok = True
    except Exception as exc:  
        settings_error = str(exc)

    status = "OK" if db_state["connected"] and settings_ok else "WARNING"
    text = [
        "<b>BOT STATUS</b>",
        f"Статус: <code>{status}</code>",
        f"БД: <code>{'OK' if db_state['connected'] else 'ERROR'}</code>",
        f"Схема: <code>{db_state.get('schema_version', 0)}</code>",
        f"Пользователи: <code>{db_state.get('users', 0)}</code>",
        f"Настройки: <code>{'OK' if settings_ok else 'ERROR'}</code>",
    ]
    if settings_error:
        text.append(f"Ошибка настроек: <code>{settings_error}</code>")
    if db_state.get("errors"):
        text.append(f"Ошибка БД: <code>{db_state['errors'][0]}</code>")

    await message.answer("\n".join(text), parse_mode="HTML")