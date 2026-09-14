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
import random
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from emojis import Emoji
router = Router()
@router.message(Command("dice", "кубик"))
async def cmd_dice(message: Message, bot):
    await message.answer_dice(emoji="🎲")
@router.message(Command("coin", "монетка"))
async def cmd_coin(message: Message):
    result = random.choice(["🪙 Орёл", "🪙 Решка"])
    await message.answer(f"{Emoji.cube.value} {result}")
@router.message(Command("8ball", "шар"))
async def cmd_8ball(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            f"{Emoji.note.value} Задай вопрос: <code>шар будет ли...?</code>",
            parse_mode="HTML",
        )
        return
    answers = [
        "🎱 Бесспорно.",
        "🎱 Определённо да.",
        "🎱 Скорее всего.",
        "🎱 Хорошие перспективы.",
        "🎱 Знаки говорят «да».",
        "🎱 Пока не ясно, попробуй ещё.",
        "🎱 Спроси позже.",
        "🎱 Лучше не рассказывать.",
        "🎱 Даже не думай.",
        "🎱 Мой ответ — нет.",
        "🎱 Очень сомнительно.",
        "🎱 Не рассчитывай на это.",
    ]
    await message.answer(
        f"❓ <i>{parts[1]}</i>\n{random.choice(answers)}",
        parse_mode="HTML",
    )
@router.message(Command("choose", "выбери"))
async def cmd_choose(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            f"{Emoji.note.value} Формат: <code>выбери пицца, суши, бургер</code>",
            parse_mode="HTML",
        )
        return
    options = [o.strip() for o in parts[1].split(",") if o.strip()]
    if len(options) < 2:
        await message.answer(f"{Emoji.note.value} Нужно минимум 2 варианта через запятую")
        return
    choice = random.choice(options)
    await message.answer(f"🎯 Выбираю: <b>{choice}</b>", parse_mode="HTML")
@router.message(Command("roll", "бросок"))
async def cmd_roll(message: Message):
    parts = message.text.split(maxsplit=1)
    dice_str = parts[1].strip() if len(parts) > 1 else "1d6"
    if "d" not in dice_str.lower():
        await message.answer(
            f"{Emoji.note.value} Формат: <code>2d6</code>",
            parse_mode="HTML",
        )
        return
    try:
        n_str, m_str = dice_str.lower().split("d", 1)
        n = int(n_str) if n_str else 1
        m = int(m_str)
    except ValueError:
        await message.answer(
            f"{Emoji.note.value} Формат: <code>2d6</code>",
            parse_mode="HTML",
        )
        return
    if not 1 <= n <= 20:
        await message.answer(f"{Emoji.note.value} Количество кубиков: 1-20")
        return
    if not 2 <= m <= 1000:
        await message.answer(f"{Emoji.note.value} Грани: 2-1000")
        return
    rolls = [random.randint(1, m) for _ in range(n)]
    total = sum(rolls)
    if n == 1:
        await message.answer(f"🎲 Выпало: <b>{total}</b> (d{m})", parse_mode="HTML")
    else:
        await message.answer(
            f"🎲 Бросок {n}d{m}: {rolls}\nСумма: <b>{total}</b>",
            parse_mode="HTML",
        )