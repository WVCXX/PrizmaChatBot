"""
Prizma — Telegram bot for Prizma chat
Copyright (C) 2026 WVCXX

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from config import ADMIN_IDS
from db import ensure_admin, get_user, inc_field
from utils.users import get_or_create
log = logging.getLogger("iris")
class UserMiddleware(BaseMiddleware):
    def __init__(self, flush_every: int = 10):
        super().__init__()
        self.flush_every = flush_every
        self.counter: dict[int, int] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            uid = event.from_user.id
            data["user"] = await get_or_create(event.from_user)
            if uid in ADMIN_IDS and data["user"]["rank"] < 5:
                await ensure_admin(uid, rank=5)
                data["user"] = await get_user(uid)
            self.counter[uid] = self.counter.get(uid, 0) + 1
            if self.counter[uid] >= self.flush_every:
                try:
                    await inc_field(uid, "messages", self.counter[uid])
                except Exception as e:
                    log.exception(f"inc_field(messages) failed for {uid}: {e}")
                self.counter[uid] = 0
            if event.reply_to_message and event.reply_to_message.from_user:
                await get_or_create(event.reply_to_message.from_user)
        return await handler(event, data)
    async def flush(self) -> None:
        for uid, count in list(self.counter.items()):
            if count > 0:
                try:
                    await inc_field(uid, "messages", count)
                except Exception as e:
                    log.exception(f"flush failed for {uid}: {e}")
        self.counter.clear()