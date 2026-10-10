"""
Одноразовые подтверждения опасных действий с ограниченным сроком жизни.

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
from dataclasses import dataclass
from typing import Any
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
CONFIRMATION_TTL = 60
class ConfirmationError(ValueError):
    pass
@dataclass
class PendingConfirmation:
    action: str
    arg: str
    target_id: int
    requester_id: int
    expires_at: float
    payload: dict[str, Any]
_pending: dict[tuple[int, int], PendingConfirmation] = {}
def _callback_data(prefix: str, action: str, arg: str, target_id: int) -> str:
    safe_arg = arg or "-"
    return f"{prefix}:{action}:{safe_arg}:{target_id}"
async def request_confirmation(
    message: Message,
    *,
    action: str,
    target_id: int,
    prompt: str,
    arg: str = "",
    payload: dict[str, Any] | None = None,
    ttl: int = CONFIRMATION_TTL,
) -> Message:
    now = time.monotonic()
    for key, pending in list(_pending.items()):
        if pending.expires_at <= now:
            _pending.pop(key, None)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data=_callback_data("confirm", action, arg, target_id),
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=_callback_data("confirm_cancel", action, arg, target_id),
            ),
        ]
    ])
    confirmation_message = await message.answer(prompt, reply_markup=keyboard)
    _pending[(confirmation_message.chat.id, confirmation_message.message_id)] = (
        PendingConfirmation(
            action=action,
            arg=arg or "-",
            target_id=target_id,
            requester_id=message.from_user.id,
            expires_at=now + ttl,
            payload=payload or {},
        )
    )
    return confirmation_message
def _get_confirmation(
    callback: CallbackQuery,
    prefix: str,
) -> tuple[tuple[int, int], PendingConfirmation]:
    if callback.message is None:
        raise ConfirmationError("Не удалось найти запрос подтверждения")
    try:
        _, action, arg, target_id_text = callback.data.split(":", maxsplit=3)
        target_id = int(target_id_text)
    except (AttributeError, ValueError) as exc:
        raise ConfirmationError("Некорректная кнопка подтверждения") from exc
    key = (callback.message.chat.id, callback.message.message_id)
    pending = _pending.get(key)
    if pending is None:
        raise ConfirmationError("Подтверждение истекло или уже использовано")
    if pending.expires_at <= time.monotonic():
        _pending.pop(key, None)
        raise ConfirmationError("Время подтверждения истекло")
    if callback.from_user.id != pending.requester_id:
        raise ConfirmationError("Подтвердить может только инициатор действия")
    if (
        action != pending.action
        or (arg or "-") != pending.arg
        or target_id != pending.target_id
        or not callback.data.startswith(f"{prefix}:")
    ):
        raise ConfirmationError("Кнопка не соответствует запросу")
    return key, pending
def consume_confirmation(callback: CallbackQuery, action: str) -> dict[str, Any]:
    key, pending = _get_confirmation(callback, "confirm")
    if pending.action != action:
        raise ConfirmationError("Подтверждение для другого действия")
    _pending.pop(key, None)
    return {
        "action": pending.action,
        "arg": pending.arg,
        "target_id": pending.target_id,
        **pending.payload,
    }
def cancel_confirmation(callback: CallbackQuery) -> None:
    key, _ = _get_confirmation(callback, "confirm_cancel")
    _pending.pop(key, None)