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
from aiogram import Router, F
from aiogram.types import Message
from db import set_field, all_users
from emojis import Emoji
from functions_settings import load_settings
router = Router()
@router.message(F.text.func(lambda t: t and t.upper() == "-НИК"))
async def remove_nick(message: Message):
    await set_field(message.from_user.id, "custom_nick", 0)
    await set_field(message.from_user.id, "nick", message.from_user.full_name)
    await message.answer(f"{Emoji.cross.value} Ник сброшен")
@router.message(F.text.func(lambda t: t and t.upper().startswith("+НИК")))
async def set_nick(message: Message):
    botData = load_settings()
    nick = message.text[len("+НИК"):].strip()
    if not nick:
        await message.answer(f"{Emoji.note.value} Напиши ник")
        return
    if len(nick) > botData["symbolLimit"]:
        await message.answer(
            f"{Emoji.note.value} Максимум {botData['symbolLimit']} символов")
        return
    for u in await all_users():
        if u["nick"] == nick and u["id"] != message.from_user.id:
            await message.answer(f"{Emoji.cross.value} Ник занят")
            return
    await set_field(message.from_user.id, "nick", nick)
    await set_field(message.from_user.id, "custom_nick", 1)
    await message.answer(f"{Emoji.check.value} Ник изменён на «{nick}»")