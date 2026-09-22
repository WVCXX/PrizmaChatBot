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
import time
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from db import get_user, find_by_username, active_mutes
from utils.text import hlink, is_id
from emojis import Emoji
router = Router()
START_TIME = time.time()
async def _profile_text(user_id: int) -> str:
    u = await get_user(user_id)
    if not u:
        return "Нет информации"
    mutes = {m["target_id"]: m for m in await active_mutes()}
    mute_info = f"до {mutes[user_id]['until']}" if user_id in mutes else "нет"
    return (
        f"<b>{u['nick']}</b> (id: <code>{u['id']}</code>)\n"
        f"Ранг: <b>{u['rank']}</b>\n"
        f"Репутация: <b>{u['reputation']}</b>\n"
        f"Варнов: <b>{u['varn']}</b>\n"
        f"Мут: <b>{mute_info}</b>\n"
        f"Баланс: <b>{u.get('balance', 0)}</b>\n"
        f"Банк: <b>{u.get('bank', 0)}</b>\n"
        f"Стрик: <b>{u.get('daily_streak', 0)}</b>\n"
        f"Сообщений: <b>{u.get('messages', 0)}</b>\n"
        f"В чате с: <b>{u.get('joined_at', '?')}</b>"
    )
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я — <b>Iris</b>, бот чата <b>Prizma</b>.\n\n"
        "Напиши /help, чтобы увидеть команды.",
        parse_mode="HTML")
@router.message(Command("help"))
async def cmd_help(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Юзеру", callback_data="help_user"),
         InlineKeyboardButton(text="Модератору", callback_data="help_moder")],
        [InlineKeyboardButton(text="Админу", callback_data="help_admin"),
         InlineKeyboardButton(text="Развлечения", callback_data="help_fun")],
    ])
    await message.answer("<b>Помощь</b>\nВыбери раздел:",
                         reply_markup=kb, parse_mode="HTML")
@router.callback_query(F.data.startswith("help_"))
async def help_cb(cb: CallbackQuery):
    section = cb.data[5:]
    texts = {
        "user": (
            "<b>Пользователю</b>\n"
            "/id — узнать id\n"
            "/profile — профиль\n"
            "/me — свой профиль\n"
            "/top — топ по репутации\n"
            "/rep — +1 репутации (ответом)\n"
            "+ник &lt;ник&gt; — сменить ник\n"
            "-ник — сбросить ник\n"
            "/rules — правила\n"
            "/report — жалоба (ответом)"
        ),
        "moder": (
            "<b>Модератору</b>\n"
            "/mute — мут (ответом)\n"
            "/unmute — размут\n"
            "/warn — предупреждение\n"
            "/warn_list — список\n"
            "/kick — кик\n"
            "/ban — бан\n"
            "/delete — удалить сообщение\n"
            "/note — заметка о юзере"
        ),
        "admin": (
            "<b>Админу</b>\n"
            "/promote — повысить\n"
            "/demote — понизить\n"
            "/snatvseh — снять всех\n"
            "/sozdatel — вернуть создателя\n"
            "/set — изменить настройку\n"
            "/get — посмотреть настройки\n"
            "/admins — список админов"
        ),
        "fun": (
            "<b>Развлечения</b>\n"
            "/dice — кубик\n"
            "/random — рандом число\n"
            "/ping — пинг"
        ),
    }
    try:
        await cb.message.edit_text(texts.get(section, "?"), parse_mode="HTML")
    except TelegramBadRequest:
        pass
    await cb.answer()
@router.message(Command("ping"))
async def cmd_ping(message: Message):
    uptime = int(time.time() - START_TIME)
    d, rem = divmod(uptime, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    await message.answer(f"Понг!")
@router.message(Command("id"))
async def cmd_id(message: Message):
    if message.reply_to_message:
        await message.answer(str(message.reply_to_message.from_user.id))
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        await message.answer(str(message.from_user.id))
        return
    target = parts[1].strip()
    if is_id(target):
        await message.answer(target)
        return
    u = await find_by_username(target)
    if not u:
        await message.answer("Нет информации")
        return
    await message.answer(str(u["id"]))
@router.message(Command("profile"))
async def cmd_profile(message: Message):
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            u = await find_by_username(parts[1].strip())
            if not u:
                await message.answer("Нет информации")
                return
            target_id = u["id"]
        else:
            target_id = message.from_user.id
    await message.answer(await _profile_text(target_id), parse_mode="HTML")
@router.message(Command("me"))
async def cmd_me(message: Message):
    await message.answer(await _profile_text(message.from_user.id), parse_mode="HTML")