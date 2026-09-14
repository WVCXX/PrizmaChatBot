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
from db import all_users, active_mutes, moder_stats, get_user, find_by_username, top_by
from utils.text import hlink
from emojis import Emoji
router = Router()
@router.message(Command("stats", "стата"))
async def cmd_stats(message: Message):
    users = await all_users()
    mutes = await active_mutes()
    moders = [u for u in users if u["rank"] >= 1]
    admins = [u for u in users if u["rank"] >= 3]
    total_messages = sum(u.get("messages", 0) for u in users)
    total_varn = sum(u.get("varn", 0) for u in users)
    total_rep = sum(u.get("reputation", 0) for u in users)
    text = (
        f"📊 <b>Статистика чата</b>\n"
        f"\n"
        f"👥 Всего юзеров: <b>{len(users)}</b>\n"
        f"⭐ Модераторов: <b>{len(moders)}</b>\n"
        f"👑 Админов: <b>{len(admins)}</b>\n"
        f"🔇 В муте: <b>{len(mutes)}</b>\n"
        f"\n"
        f"💬 Сообщений: <b>{total_messages}</b>\n"
        f"👍 Репутации: <b>{total_rep}</b>\n"
        f"⚠️ Варнов: <b>{total_varn}</b>\n"
    )
    await message.answer(text, parse_mode="HTML")
@router.message(Command("moder_stats", "стата_модер", "модерстата"))
async def cmd_moder_stats(message: Message):
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            u = await find_by_username(parts[1].strip())
            if not u:
                await message.answer(f"{Emoji.note.value} Нет информации")
                return
            target_id = u["id"]
        else:
            target_id = message.from_user.id
    u = await get_user(target_id)
    if not u:
        await message.answer(f"{Emoji.note.value} Нет информации")
        return
    stats = await moder_stats(target_id)
    text = (
        f"🛡 <b>{u['nick']}</b>\n"
        f"\n"
        f"🔇 Мутов: <b>{stats['mute']}</b>\n"
        f"⚠️ Варнов: <b>{stats['warn']}</b>\n"
        f"⛔ Банов: <b>{stats['ban']}</b>\n"
        f"👢 Киков: <b>{stats['kick']}</b>\n"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(Command("top_active", "топ_активных"))
async def cmd_top_active(message: Message):
    users = await top_by("messages", 10, min_value=1)
    if not users:
        await message.answer("Топ пуст")
        return
    lines = ["🏆 <b>Топ по сообщениям</b>"]
    medals = ["🥇", "🥈", "🥉"]
    for i, u in enumerate(users):
        prefix = medals[i] if i < 3 else f"{i+1}."
        lines.append(
            f"{prefix} {hlink(u['nick'], u['id'])} — {u['messages']}"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("top_varn", "топ_варнов"))
async def cmd_top_varn(message: Message):
    users = await top_by("varn", 10, min_value=1)
    if not users:
        await message.answer("Предупреждённых нет 🎉")
        return
    lines = ["⚠️ <b>Антитоп по варнам</b>"]
    for i, u in enumerate(users):
        lines.append(
            f"{i+1}. {hlink(u['nick'], u['id'])} — {u['varn']}"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")