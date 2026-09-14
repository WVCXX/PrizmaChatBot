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
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.types import CallbackQuery, Message, TelegramObject
log = logging.getLogger("iris")
class ErrorMiddleware(BaseMiddleware):
    """
    outer middleware. Ловит все исключения из хендлеров и внутренних
    middleware, логирует и по возможности отвечает юзеру.
    подключается через outer_middleware — то есть оборачивает ВСЁ,
    включая UserMiddleware и RateLimitMiddleware.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except TelegramRetryAfter as e:
            log.warning(f"Flood control: retry after {e.retry_after}s")
            return
        except TelegramBadRequest as e:
            log.warning(f"Bad request: {e}")
            return
        except TelegramForbiddenError as e:
            # юзер заблокировал бота / удалил аккаунт / не начинал диалог.
            log.info(f"Forbidden: {e}")
            return
        except TelegramAPIError as e:
            log.exception(f"Telegram API error: {e}")
            await _reply_safe(event, "⚠️ Telegram API вернул ошибку. Попробуй позже.")
            return
        except Exception as e:
            log.exception(f"Unhandled exception in handler: {e}")
            await _reply_safe(event, "⚠️ Что-то пошло не так. Попробуй позже.")
            return
async def _reply_safe(event: TelegramObject, text: str) -> None:
    try:
        if isinstance(event, Message):
            await event.answer(text)
        elif isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)
    except Exception:
        pass