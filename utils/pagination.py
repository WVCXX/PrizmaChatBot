"""
Общие функции разбиения списков на страницы и создания клавиатуры.

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
from collections.abc import Sequence
from typing import TypeVar
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
Item = TypeVar("Item")
def page_window(
    total_items: int,
    page: int,
    page_size: int = 10,
) -> tuple[int, int, int]:
    if page_size <= 0:
        raise ValueError("Размер страницы должен быть больше нуля")
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    current_page = max(1, min(page, total_pages))
    offset = (current_page - 1) * page_size
    return current_page, total_pages, offset
def paginate(
    items: Sequence[Item],
    page: int,
    page_size: int = 10,
) -> tuple[list[Item], int, int]:
    current_page, total_pages, start = page_window(len(items), page, page_size)
    return list(items[start:start + page_size]), current_page, total_pages
def pagination_keyboard(
    kind: str,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup | None:
    if total_pages <= 1:
        return None
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(
            text="◀️",
            callback_data=f"page:{kind}:{page - 1}",
        ))
    buttons.append(InlineKeyboardButton(
        text=f"{page}/{total_pages}",
        callback_data=f"page:{kind}:{page}",
    ))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(
            text="▶️",
            callback_data=f"page:{kind}:{page + 1}",
        ))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])