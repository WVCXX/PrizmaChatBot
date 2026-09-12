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
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from db import inc_field
from utils.users import get_or_create
class UserMiddleware(BaseMiddleware):
    #загружает юзера, обновляет username/ник, батчит счётчик
    def __init__(self, flush_every: int = 10):
        self.flush_every = flush_every
        self.counter: dict[int, int] = {}
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            data["user"] = await get_or_create(event.from_user)
            uid = event.from_user.id
            self.counter[uid] = self.counter.get(uid, 0) + 1
            if self.counter[uid] >= self.flush_every:
                await inc_field(uid, "messages", self.counter[uid])
                self.counter[uid] = 0

            if event.reply_to_message and event.reply_to_message.from_user:
                await get_or_create(event.reply_to_message.from_user)
        return await handler(event, data)
class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 15, window: float = 1.0):
        self.limit = limit
        self.window = window
        self.cache: dict[int, list[float]] = {}
        self.last_cleanup = time.time()
    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and event.from_user:
            uid = event.from_user.id
            now = time.time()
            if now - self.last_cleanup > 60:
                for k in list(self.cache):
                    self.cache[k] = [t for t in self.cache[k] if now - t < self.window]
                    if not self.cache[k]:
                        del self.cache[k]
                self.last_cleanup = now
            times = self.cache.setdefault(uid, [])
            times[:] = [t for t in times if now - t < self.window]
            if len(times) >= self.limit:
                return  
            times.append(now)
        return await handler(event, data)