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
from functions_settings import load_settings
from emojis import Emoji
router = Router()
@router.message(Command("rules", "правила"))
async def cmd_rules(message: Message):
    botData = load_settings()
    rules = botData.get("rules", [])
    if not rules:
        await message.answer(f"{Emoji.note.value} Правила не заданы")
        return
    lines = ["📜 <b>Правила чата</b>\n"]
    for i, r in enumerate(rules, 1):
        lines.append(f"{i}. {r}")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("links", "ссылки"))
async def cmd_links(message: Message):
    botData = load_settings()
    links = botData.get("links", {})
    if not links:
        await message.answer(f"{Emoji.note.value} Ссылки не заданы")
        return
    lines = ["🔗 <b>Ссылки</b>\n"]
    for name, url in links.items():
        lines.append(f'• <a href="{url}">{name}</a>')
    await message.answer("\n".join(lines), parse_mode="HTML")