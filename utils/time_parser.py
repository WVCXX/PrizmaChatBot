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
import datetime
def toDate(text: str) -> datetime.datetime:
    text = text.strip().replace(":", " ").replace(".", " ")
    try:
        parts = [int(p) for p in text.split() if p]
    except ValueError:
        raise ValueError("Не удалось разобрать дату")
    while len(parts) < 6:
        parts.append(0)
    try:
        return datetime.datetime(*parts[:6])
    except ValueError as e:
        raise ValueError(f"Некорректная дата: {e}")
_UNITS = {
    "минута": 60, "минуту": 60, "минут": 60, "минуты": 60, "мн": 60, "м": 60,
    "час": 3600, "часа": 3600, "часов": 3600, "ч": 3600,
    "день": 86400, "дня": 86400, "дней": 86400, "дн": 86400, "д": 86400,
    "неделя": 604800, "недели": 604800, "недель": 604800, "нд": 604800,
    "месяц": 2629800, "месяца": 2629800, "месяцев": 2629800, "мес": 2629800,
}
def t2s(time_str: str) -> datetime.datetime:
    time_str = time_str.lower().strip()
    if time_str in ("навсегда", "forever", "перм"):
        return datetime.datetime(2038, 1, 1)
    try:
        value, unit = time_str.split(maxsplit=1)
        value = int(value)
    except ValueError:
        raise ValueError("Не удалось разобрать время. Пример: '1 час'")
    unit = unit.strip()
    if unit not in _UNITS:
        raise ValueError(f"Неизвестная единица: {unit}")
    return datetime.datetime.now() + datetime.timedelta(seconds=value * _UNITS[unit])