"""
Форматирование длительности, дат, прогресса и русских форм слов.

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
from collections.abc import Sequence
def bar(value: int | float, max_value: int | float, width: int = 12) -> str:
    if width <= 0:
        return ""
    if max_value <= 0:
        return "░" * width
    ratio = max(0.0, min(1.0, value / max_value))
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)
def human_duration(seconds: int | float) -> str:
    remaining = max(0, int(seconds))
    units = (
        (86400, "д"),
        (3600, "ч"),
        (60, "м"),
        (1, "с"),
    )
    parts = []
    for unit_seconds, suffix in units:
        amount, remaining = divmod(remaining, unit_seconds)
        if amount:
            parts.append(f"{amount}{suffix}")
    return " ".join(parts) if parts else "0с"
def human_date(value: datetime.datetime | datetime.date) -> str:
    if isinstance(value, datetime.datetime):
        return value.strftime("%d.%m.%Y %H:%M")
    return value.strftime("%d.%m.%Y")
def pluralize(number: int, forms: Sequence[str]) -> str:
    if len(forms) != 3:
        raise ValueError("Нужно передать три формы: 1, 2-4 и 5-0")
    absolute_number = abs(number)
    last_two = absolute_number % 100
    if 11 <= last_two <= 14:
        form = forms[2]
    elif absolute_number % 10 == 1:
        form = forms[0]
    elif 2 <= absolute_number % 10 <= 4:
        form = forms[1]
    else:
        form = forms[2]
    return f"{number} {form}"