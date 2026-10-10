"""
Декораторы для проверки прав и аудита команд Iris.

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
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar, cast
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Message
from config import ADMIN_IDS
from db import get_user, log_action
from emojis import Emoji
from functions_settings import load_settings
from ranks import get_rank_name
Handler = TypeVar("Handler", bound=Callable[..., Awaitable[Any]])
log = logging.getLogger("iris")
async def _answer(event: Message | CallbackQuery, text: str) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer(text, show_alert=True)
    else:
        await event.answer(text)
def require_rank(key: str) -> Callable[[Handler], Handler]:
    def decorator(handler: Handler) -> Handler:
        @wraps(handler)
        async def wrapped(
            event: Message | CallbackQuery,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            user = event.from_user
            if user is None:
                await _answer(
                    event,
                    f"{Emoji.cross.value} Не удалось определить пользователя",
                )
                return None
            if user.id not in ADMIN_IDS:
                settings = load_settings()
                required_rank = settings.get(key)
                if not isinstance(required_rank, int):
                    log.error("Для проверки ранга отсутствует числовая настройка %s", key)
                    await _answer(event, f"{Emoji.cross.value} Ошибка настройки прав")
                    return None
                user_data = await get_user(user.id)
                rank = user_data.get("rank", 0) if user_data else 0
                if rank < required_rank:
                    rank_name = get_rank_name(settings, required_rank, 1)
                    await _answer(
                        event,
                        f"{Emoji.note.value} Команда доступна с ранга "
                        f"{rank_name} ({required_rank})",
                    )
                    return None
            return await handler(event, *args, **kwargs)
        return cast(Handler, wrapped)
    return decorator
def require_owner() -> Callable[[Handler], Handler]:
    def decorator(handler: Handler) -> Handler:
        @wraps(handler)
        async def wrapped(
            event: Message | CallbackQuery,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            user = event.from_user
            message = event.message if isinstance(event, CallbackQuery) else event
            bot = kwargs.get("bot") or getattr(event, "bot", None)
            if user is None or message is None or bot is None:
                await _answer(
                    event,
                    f"{Emoji.cross.value} Не удалось проверить создателя чата",
                )
                return None
            try:
                member = await bot.get_chat_member(message.chat.id, user.id)
            except TelegramAPIError:
                log.exception("Не удалось проверить статус создателя чата")
                await _answer(event, f"{Emoji.cross.value} Не удалось проверить права")
                return None
            if member.status != "creator":
                await _answer(
                    event,
                    f"{Emoji.cross.value} Только создатель чата может это сделать",
                )
                return None
            return await handler(event, *args, **kwargs)
        return cast(Handler, wrapped)
    return decorator
def log_command() -> Callable[[Handler], Handler]:
    def decorator(handler: Handler) -> Handler:
        @wraps(handler)
        async def wrapped(
            event: Message | CallbackQuery,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            user = event.from_user
            message = event.message if isinstance(event, CallbackQuery) else event
            if user is not None and message is not None:
                text = message.text or message.caption or ""
                command = text.split(maxsplit=1)[0] if text else handler.__name__
                await log_action(
                    message.chat.id,
                    user.id,
                    user.id,
                    "command",
                    reason=command[:64],
                )
            return await handler(event, *args, **kwargs)
        return cast(Handler, wrapped)
    return decorator