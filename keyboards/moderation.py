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
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
def mod_actions_keyboard(target_id: int) -> InlineKeyboardMarkup:
    #кнопки модератора
    kb = InlineKeyboardBuilder()
    kb.button(text="🔇 Мут 1ч",  callback_data=f"mod:mute:1h:{target_id}")
    kb.button(text="🔇 Мут 1д",  callback_data=f"mod:mute:1d:{target_id}")
    kb.button(text="🔇 Мут 7д",  callback_data=f"mod:mute:7d:{target_id}")
    kb.button(text="⚠️ Варн",    callback_data=f"mod:warn:1:{target_id}")
    kb.button(text="👢 Кик",     callback_data=f"mod:kick:0:{target_id}")
    kb.button(text="⛔ Бан",     callback_data=f"mod:ban:0:{target_id}")
    kb.button(text="❌ Отмена",  callback_data=f"mod:cancel:0:{target_id}")
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup()