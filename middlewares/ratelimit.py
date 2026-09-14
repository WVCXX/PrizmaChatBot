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
import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 15, window: float = 1.0):
        super().__init__()
        self.limit = limit
        self.window = window
        self.cache: dict[int, list[float]] = {}
        self.last_cleanup = time.time()
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
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