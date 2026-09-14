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
from db import get_user, find_by_username, active_mutes, get_notes
from utils.text import hlink, is_id
from emojis import Emoji
from functions_settings import load_settings
from ranks import get_rank_name
router = Router()
@router.message(Command("whois", "кто"))
async def cmd_whois(message: Message):
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            arg = parts[1].strip().replace("@", "")
            if is_id(arg):
                target_id = int(arg)
            else:
                u = await find_by_username(arg)
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
    botData = load_settings()
    rank_name = get_rank_name(botData, u["rank"], 0) if u["rank"] > 0 else "—"
    mutes = {m["target_id"]: m for m in await active_mutes()}
    mute_info = f"до {mutes[target_id]['until']}" if target_id in mutes else "нет"
    notes = await get_notes(target_id)
    text = (
        f"👤 <b>{hlink(u['nick'], u['id'])}</b>\n"
        f"🆔 ID: <code>{u['id']}</code>\n"
        f"📛 Username: @{u['username'] or '—'}\n"
        f"\n"
        f"⭐ Ранг: <b>{rank_name}</b> ({u['rank']})\n"
        f"👍 Репутация: <b>{u['reputation']}</b>\n"
        f"⚠️ Варнов: <b>{u['varn']}</b>\n"
        f"🔇 Мут: <b>{mute_info}</b>\n"
        f"\n"
        f"💰 Баланс: <b>{u.get('balance', 0)}</b>\n"
        f"🏦 Банк: <b>{u.get('bank', 0)}</b>\n"
        f"💬 Сообщений: <b>{u.get('messages', 0)}</b>\n"
        f"📅 В чате с: <b>{u.get('joined_at', '?')}</b>\n"
        f"📝 Заметок: <b>{len(notes)}</b>"
    )
    await message.answer(text, parse_mode="HTML")