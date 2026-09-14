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
from db import add_quote, random_quote, quotes_by_user, get_user, find_by_username
from utils.text import hlink, is_id
from emojis import Emoji
router = Router()
@router.message(Command("quote", "цитата"))
async def cmd_quote(message: Message):
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
        quotes = await quotes_by_user(target_id, limit=1)
    else:
        q = await random_quote()
        quotes = [q] if q else []
    if not quotes:
        await message.answer(f"{Emoji.note.value} Цитат нет")
        return
    q = quotes[0]
    author = await get_user(q["user_id"])
    nick = hlink(author["nick"], author["id"]) if author else f"id{q['user_id']}"
    await message.answer(
        f"💬 <b>Цитата</b>\n{nick}:\n<i>{q['text']}</i>",
        parse_mode="HTML",
    )
@router.message(Command("q", "ц+"))
async def cmd_save_quote(message: Message):
    if not message.reply_to_message:
        await message.answer(f"{Emoji.note.value} Ответь на сообщение, которое хочешь сохранить")
        return
    target = message.reply_to_message.from_user
    text = message.reply_to_message.text or message.reply_to_message.caption
    if not text:
        await message.answer(f"{Emoji.note.value} В сообщении нет текста")
        return
    if len(text) > 500:
        await message.answer(f"{Emoji.note.value} Слишком длинно (макс. 500)")
        return
    await add_quote(target.id, text, message.from_user.id)
    await message.answer(f"{Emoji.check.value} Цитата сохранена")
@router.message(Command("quotes", "цитаты"))
async def cmd_quotes(message: Message):
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
    quotes = await quotes_by_user(target_id, limit=20)
    if not quotes:
        await message.answer(f"{Emoji.note.value} Цитат нет")
        return
    lines = [f"💬 <b>Цитаты {hlink(u['nick'], u['id'])}</b> ({len(quotes)}):\n"]
    for q in quotes[:10]:
        lines.append(f"• <i>{q['text'][:100]}</i>")
    await message.answer("\n".join(lines), parse_mode="HTML")