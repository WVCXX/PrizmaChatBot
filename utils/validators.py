"""
Валидаторы длительности, причины и текстовых сумм.

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
import re
from utils.time_parser import t2s
_SMALL_NUMBERS = {
    "ноль": 0,
    "нуль": 0,
    "один": 1,
    "одна": 1,
    "одно": 1,
    "одну": 1,
    "два": 2,
    "две": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
}
_TEENS = {
    "десять": 10,
    "одиннадцать": 11,
    "двенадцать": 12,
    "тринадцать": 13,
    "четырнадцать": 14,
    "пятнадцать": 15,
    "шестнадцать": 16,
    "семнадцать": 17,
    "восемнадцать": 18,
    "девятнадцать": 19,
}
_TENS = {
    "двадцать": 20,
    "тридцать": 30,
    "сорок": 40,
    "пятьдесят": 50,
    "шестьдесят": 60,
    "семьдесят": 70,
    "восемьдесят": 80,
    "девяносто": 90,
}
_HUNDREDS = {
    "сто": 100,
    "двести": 200,
    "триста": 300,
    "четыреста": 400,
    "пятьсот": 500,
    "шестьсот": 600,
    "семьсот": 700,
    "восемьсот": 800,
    "девятьсот": 900,
}
_SCALES = {
    "тысяча": 1_000,
    "тысячи": 1_000,
    "тысяч": 1_000,
    "миллион": 1_000_000,
    "миллиона": 1_000_000,
    "миллионов": 1_000_000,
    "миллиард": 1_000_000_000,
    "миллиарда": 1_000_000_000,
    "миллиардов": 1_000_000_000,
}
_CURRENCY_WORDS = {
    "рубль", "рубля", "рублей", "руб", "руб.",
    "монета", "монеты", "монет",
}
_NUMBER_WORDS = {**_SMALL_NUMBERS, **_TEENS, **_TENS, **_HUNDREDS}
def parse_duration(text: str) -> datetime.datetime:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Укажите длительность, например «1 час» или «30 минут».")

    value = text.strip()
    try:
        result = t2s(value)
    except (ValueError, OverflowError) as exc:
        raise ValueError(
            f"Не удалось разобрать длительность «{value}». "
            "Пример: «1 час» или «30 минут»."
        ) from exc

    if result <= datetime.datetime.now():
        raise ValueError("Длительность должна быть больше нуля.")
    return result
def parse_reason(
    text: str,
    keywords: tuple[str, ...] = ("за", "причина"),
) -> tuple[str, str]:
    value = text.strip()
    if not value:
        return "", ""
    ordered_keywords = sorted(
        (word for word in keywords if word),
        key=len,
        reverse=True,
    )
    alternatives = "|".join(re.escape(keyword) for keyword in ordered_keywords)
    if alternatives:
        marker = re.search(
            rf"(?<!\w)(?:{alternatives})(?!\w)",
            value,
            flags=re.IGNORECASE,
        )
        if marker:
            duration_text = value[:marker.start()].strip(" \t\r\n,:;")
            reason = value[marker.end():].strip(" \t\r\n,:;")
            return duration_text, reason
    words = value.split()
    for split_at in range(len(words), 0, -1):
        duration_text = " ".join(words[:split_at])
        try:
            parse_duration(duration_text)
        except ValueError:
            continue
        reason = " ".join(words[split_at:])
        return duration_text, reason
    return value, ""
def parse_amount(text: str) -> int | None:
    if not isinstance(text, str) or not text.strip():
        return None
    normalized = text.lower().replace("ё", "е")
    tokens = [word.strip(".,;:!?") for word in normalized.split()]
    if not tokens or any(
        not token or any(char.isdigit() for char in token)
        for token in tokens
    ):
        return None
    total = 0
    group = 0
    group_has_number = False
    saw_number = False
    for index, token in enumerate(tokens):
        if token in _CURRENCY_WORDS and index == len(tokens) - 1:
            continue
        if token in _NUMBER_WORDS:
            group += _NUMBER_WORDS[token]
            group_has_number = True
            saw_number = True
        elif token in _SCALES:
            if group_has_number and group == 0:
                return None
            scale = _SCALES[token]
            total += (group if group_has_number else 1) * scale
            group = 0
            group_has_number = False
            saw_number = True
        else:
            return None
    amount = total + group
    if not saw_number or amount <= 0:
        return None
    return amount