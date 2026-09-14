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
import time
from collections import defaultdict, deque
from aiogram import Router, Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatPermissions, Message
from db import get_user, add_mute, log_action
from emojis import Emoji
from functions_settings import load_settings
from utils.text import hlink
router = Router()
MUTE_PERMS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_send_polls=False,
    can_invite_users=False,
)
_buckets: dict[int, deque] = defaultdict(deque)
@router.message()
async def antiflood(message: Message, bot: Bot):
    if not message.from_user or message.from_user.is_bot:
        return
    text = message.text or message.caption or ""
    if text.startswith("/") or text.startswith("!"):
        return
    botData = load_settings()
    cfg = botData.get("antiflood", {})
    if not cfg.get("enabled"):
        return
    user = await get_user(message.from_user.id)
    if user and user["rank"] >= botData["DKmute"]:
        return
    limit = int(cfg.get("messages", 5))
    window = int(cfg.get("seconds", 10))
    mute_min = int(cfg.get("mute_minutes", 10))
    now = time.time()
    bucket = _buckets[message.from_user.id]
    while bucket and now - bucket[0] > window:
        bucket.popleft()
    bucket.append(now)
    if len(bucket) < limit:
        return
    bucket.clear()
    until = datetime.datetime.now() + datetime.timedelta(minutes=mute_min)
    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            permissions=MUTE_PERMS,
            until_date=until,
        )
    except TelegramAPIError:
        return
    await add_mute(
        message.from_user.id, message.chat.id,
        until.isoformat(), "антифлуд",
    )
    await log_action(
        message.chat.id, bot.id, message.from_user.id,
        "mute", f"{mute_min}м", "антифлуд",
    )
    await message.answer(
        f"{Emoji.mute.value} "
        f"{hlink(message.from_user.full_name, message.from_user.id)} "
        f"замучен на {mute_min} мин (антифлуд)",
        parse_mode="HTML",
    )