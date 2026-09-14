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
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from emojis import Emoji
router = Router()

@router.message(F.text.func(lambda t: t and t.upper().startswith("ПИУ")))
async def piu(message: Message):
    await message.answer("ПАУ")

@router.message(F.text.func(lambda t: t and t.upper().startswith("КИНГ")))
async def king(message: Message):
    await message.answer("КОНГ")

@router.message(F.text.func(lambda t: t and t.upper().startswith("БОТ")))
async def bot_alive(message: Message):
    await message.answer(f"{Emoji.check.value} На месте")

@router.message(F.text.func(lambda t: t and t.upper() == "ЧТО С БОТОМ"))
async def what(message: Message):
    await message.answer("Бот жив.")

@router.message(Command("random", "рандом"))
async def random_cmd(message: Message):
    parts = message.text.split()[1:]
    if len(parts) < 2:
        await message.answer(f"{Emoji.note.value} Формат: /random 1 100")
        return
    try:
        low, high = int(parts[0]), int(parts[1])
    except ValueError:
        await message.answer(f"{Emoji.note.value} Числа должны быть целыми")
        return
    if low > high:
        await message.answer(f"{Emoji.note.value} Первое число должно быть меньше")
        return
    if low == high:
        await message.answer(
            f"{Emoji.cube.value} Из [{low}..{high}] выпало... {low}!")
        return
    result = random.randint(low, high)
    await message.answer(
        f"{Emoji.cube.value} Случайное число из [{low}..{high}] — {result}")