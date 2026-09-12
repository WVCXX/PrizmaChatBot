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
import datetime
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from db import get_user, inc_field, set_field, log_rep, top_by
from utils.text import hlink
from emojis import Emoji
router = Router()
@router.message(Command("top"))
async def cmd_top(message: Message):
    users = await top_by("reputation", 10, min_value=1)
    if not users:
        await message.answer("Топ пуст")
        return
    lines = ["🏆 <b>Топ по репутации</b>"]
    medals = ["🥇", "🥈", "🥉"]
    for i, u in enumerate(users):
        prefix = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{prefix} {hlink(u['nick'], u['id'])} — {u['reputation']}")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("rep", "реп"))
async def cmd_rep(message: Message):
    if not message.reply_to_message:
        await message.answer("Ответь на сообщение, кому дать репутацию.")
        return
    target_tg = message.reply_to_message.from_user
    if target_tg.id == message.from_user.id:
        await message.answer(f"{Emoji.note.value} Себе нельзя.")
        return
    if target_tg.is_bot:
        await message.answer(f"{Emoji.note.value} Ботам нельзя.")
        return
    me = await get_user(message.from_user.id)
    last_to = me.get("last_rep_given_to")
    last_time = me.get("last_rep_time")
    if last_to == target_tg.id and last_time:
        try:
            last_dt = datetime.datetime.fromisoformat(last_time)
            if (datetime.datetime.now() - last_dt).total_seconds() < 86400:
                await message.answer(f"{Emoji.note.value} Этому юзеру — раз в сутки.")
                return
        except Exception:
            pass
    await inc_field(target_tg.id, "reputation", 1)
    await set_field(message.from_user.id, "last_rep_given_to", target_tg.id)
    await set_field(message.from_user.id, "last_rep_time",
                    datetime.datetime.now().isoformat())
    await log_rep(message.from_user.id, target_tg.id, 1)
    target = await get_user(target_tg.id)
    await message.answer(
        f"{Emoji.plus.value} {hlink(target['nick'], target['id'])} получает +1 репутации "
        f"(всего: {target['reputation']})", parse_mode="HTML")