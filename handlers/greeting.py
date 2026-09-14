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
import logging
from aiogram import Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER
from aiogram.types import ChatMemberUpdated
from aiogram.exceptions import TelegramAPIError
from functions_settings import load_settings
from utils.users import get_or_create
router = Router()
log = logging.getLogger("iris")
@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> MEMBER))
async def on_join(event: ChatMemberUpdated, bot: Bot):
    try:
        botData = load_settings()
    except Exception as e:
        log.exception(f"greeting: load_settings failed: {e}")
        return
    user = event.new_chat_member.user
    try:
        await get_or_create(user)
    except Exception as e:
        log.exception(f"greeting: get_or_create failed: {e}")
    text = botData.get("greeting", "").replace("{nick}", user.full_name)
    if not text:
        return
    try:
        await bot.send_message(event.chat.id, text, parse_mode="HTML")
    except TelegramAPIError as e:
        log.warning(f"greeting: send failed: {e}")
@router.chat_member(ChatMemberUpdatedFilter(MEMBER >> IS_NOT_MEMBER))
async def on_leave(event: ChatMemberUpdated, bot: Bot):
    user = event.old_chat_member.user
    if event.new_chat_member.status == "kicked":
        log.info(f"leave: {user.id} kicked, skip farewell")
        return
    if user.is_bot:
        return
    try:
        await bot.send_message(
            event.chat.id,
            f"👋 {user.full_name} покинул нас.",
        )
    except TelegramAPIError as e:
        log.warning(f"leave: send failed: {e}")