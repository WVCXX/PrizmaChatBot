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
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from db import (
    add_quote,
    count_quotes_by_user,
    delete_quote,
    find_by_username,
    get_quote,
    get_user,
    quotes_by_user,
    random_quote,
)
from config import ADMIN_IDS
from functions_settings import load_settings
from utils.text import hlink, is_id
from utils.pagination import page_window, pagination_keyboard
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
    quote_id = await add_quote(target.id, text, message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"quote:del:{quote_id}",
        )
    ]])
    await message.answer(
        f"{Emoji.check.value} Цитата #{quote_id} сохранена",
        reply_markup=keyboard,
    )
@router.callback_query(F.data.startswith("quote:del:"))
async def cb_delete_quote(cb: CallbackQuery):
    try:
        quote_id = int(cb.data.split(":", maxsplit=2)[2])
    except (AttributeError, IndexError, ValueError):
        await cb.answer("Некорректный ID цитаты", show_alert=True)
        return
    quote = await get_quote(quote_id)
    if not quote:
        await cb.answer("Цитата уже удалена", show_alert=True)
        return
    actor_id = cb.from_user.id
    actor = await get_user(actor_id)
    settings = load_settings()
    is_owner = actor_id in (quote["saved_by"], quote["user_id"])
    is_moderator = (
        actor_id in ADMIN_IDS
        or (actor is not None and actor["rank"] >= settings["DKvarn"])
    )
    if not is_owner and not is_moderator:
        await cb.answer("Удалить цитату может только её автор или модератор", show_alert=True)
        return
    await delete_quote(quote_id)
    if cb.message:
        await cb.message.edit_text(f"{Emoji.check.value} Цитата #{quote_id} удалена")
    await cb.answer("Удалено")
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
    user = await get_user(target_id)
    if not user:
        await message.answer(f"{Emoji.note.value} Нет информации")
        return
    text, keyboard = await _quotes_page(target_id, 1, user)
    if text is None:
        await message.answer(f"{Emoji.note.value} Цитат нет")
        return
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
async def _quotes_page(
    target_id: int,
    page: int,
    user: dict | None = None,
) -> tuple[str | None, InlineKeyboardMarkup | None]:
    if user is None:
        user = await get_user(target_id)
    if not user:
        return None, None
    total = await count_quotes_by_user(target_id)
    if not total:
        return None, None
    current_page, total_pages, offset = page_window(total, page)
    quotes = await quotes_by_user(target_id, limit=10, offset=offset)
    if not quotes:
        return None, None
    lines = [
        f"💬 <b>Цитаты {hlink(user['nick'], user['id'])}</b> ({total}):\n"
    ]
    for quote in quotes:
        lines.append(f"• <i>{quote['text'][:100]}</i>")
    keyboard = pagination_keyboard(
        f"quotes:{target_id}",
        current_page,
        total_pages,
    )
    return "\n".join(lines), keyboard
@router.callback_query(F.data.startswith("page:quotes:"))
async def cb_quotes_page(cb: CallbackQuery):
    try:
        _, _, target_id_text, page_text = cb.data.split(":", maxsplit=3)
        if not target_id_text.isdigit() or not page_text.isdigit():
            raise ValueError("page callback должен содержать числовые ID")
        target_id = int(target_id_text)
        page = int(page_text)
    except (AttributeError, ValueError):
        await cb.answer("Некорректная страница", show_alert=True)
        return
    text, keyboard = await _quotes_page(target_id, page)
    if text is None:
        await cb.answer("Цитат нет", show_alert=True)
        return
    await cb.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await cb.answer()