"""
Общие callback-обработчики отмены подтверждений опасных действий.

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
from aiogram import F, Router
from aiogram.types import CallbackQuery
from utils.confirm import ConfirmationError, cancel_confirmation
router = Router()
@router.callback_query(F.data.startswith("confirm_cancel:"))
async def cb_cancel_confirmation(callback: CallbackQuery) -> None:
    try:
        cancel_confirmation(callback)
    except ConfirmationError as exc:
        await callback.answer(str(exc), show_alert=True)
        return
    if callback.message:
        await callback.message.edit_text("❌ Действие отменено")
    await callback.answer("Отменено")