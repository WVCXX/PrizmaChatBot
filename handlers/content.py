"""
Prizma — Telegram bot for Prizma chat
Copyright (C) 2026 WVCXX
... (GPL header)
"""
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from db import get_user
from config import ADMIN_IDS
from functions_settings import load_settings, save_settings
from emojis import Emoji
router = Router()

#какой ранг нужен для правки контента
NEED_RANK = 4
async def _check(message: Message) -> bool:
    moder = await get_user(message.from_user.id)
    if not moder:
        await message.answer(f"{Emoji.note.value} Тебя нет в БД")
        return False
    if moder["rank"] < NEED_RANK and message.from_user.id not in ADMIN_IDS:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return False
    return True
@router.message(Command("greeting", "приветствие"))
async def cmd_greeting(message: Message):
    parts = message.text.split(maxsplit=1)
    botData = load_settings()
    if len(parts) < 2:
        current = botData.get("greeting", "")
        if not current:
            await message.answer(f"{Emoji.note.value} Приветствие не задано")
            return
        await message.answer(
            f"👋 <b>Текущее приветствие:</b>\n<code>{current}</code>\n\n"
            f"Изменить: <code>приветствие Новый Текст Приветствия!</code>",
            parse_mode="HTML",
        )
        return
    if not await _check(message):
        return
    new_text = parts[1].strip()
    if len(new_text) > 500:
        await message.answer(f"{Emoji.note.value} Максимум 500 символов")
        return
    botData["greeting"] = new_text
    save_settings(botData)
    preview = new_text.replace("{nick}", message.from_user.full_name)
    await message.answer(
        f"{Emoji.check.value} Приветствие обновлено\n\n"
        f"<b>Превью:</b>\n{preview}",
        parse_mode="HTML",
    )
@router.message(Command("rule_add", "правило"))
async def cmd_rule_add(message: Message):
    if not await _check(message):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        await message.answer(
            f"{Emoji.note.value} Формат: <code>правило добавить &lt;N&gt; текст</code>",
            parse_mode="HTML",
        )
        return
    pos = int(parts[1])
    text = parts[2].strip()
    if len(text) > 300:
        await message.answer(f"{Emoji.note.value} Максимум 300 символов")
        return
    botData = load_settings()
    rules = botData.get("rules", [])
    if pos < 1 or pos > len(rules) + 1:
        await message.answer(
            f"{Emoji.note.value} Позиция: 1..{len(rules) + 1}"
        )
        return
    rules.insert(pos - 1, text)
    botData["rules"] = rules
    save_settings(botData)
    await message.answer(
        f"{Emoji.check.value} Правило добавлено на позицию {pos}"
    )
@router.message(Command("rule_del", "правило_удалить"))
async def cmd_rule_del(message: Message):
    if not await _check(message):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        await message.answer(
            f"{Emoji.note.value} Формат: <code>правило удалить &lt;N&gt;</code>",
            parse_mode="HTML",
        )
        return
    pos = int(parts[1])
    botData = load_settings()
    rules = botData.get("rules", [])
    if pos < 1 or pos > len(rules):
        await message.answer(f"{Emoji.note.value} Нет такого правила")
        return
    removed = rules.pop(pos - 1)
    botData["rules"] = rules
    save_settings(botData)
    await message.answer(
        f"{Emoji.check.value} Удалено: <i>{removed}</i>",
        parse_mode="HTML",
    )
@router.message(Command("rules_reset", "правила_сбросить"))
async def cmd_rules_reset(message: Message):
    if not await _check(message):
        return
    botData = load_settings()
    botData["rules"] = []
    save_settings(botData)
    await message.answer(f"{Emoji.check.value} Все правила удалены")
@router.message(Command("link_add", "ссылка"))
async def cmd_link_add(message: Message):
    if not await _check(message):
        return
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer(
            f"{Emoji.note.value} Формат: <code>ссылка добавить Название https://...</code>",
            parse_mode="HTML",
        )
        return
    name = parts[2].strip()
    url = parts[3].strip()
    if not url.startswith(("http://", "https://", "tg://")):
        await message.answer(f"{Emoji.note.value} URL должен начинаться с http(s):// или tg://")
        return
    if len(name) > 50:
        await message.answer(f"{Emoji.note.value} Название: макс. 50 символов")
        return
    botData = load_settings()
    links = botData.get("links", {})
    links[name] = url
    botData["links"] = links
    save_settings(botData)
    await message.answer(f"{Emoji.check.value} Ссылка «{name}» добавлена")
@router.message(Command("link_del", "ссылка_удалить"))
async def cmd_link_del(message: Message):
    if not await _check(message):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            f"{Emoji.note.value} Формат: <code>ссылка удалить Название</code>",
            parse_mode="HTML",
        )
        return
    name = parts[2].strip()
    botData = load_settings()
    links = botData.get("links", {})
    if name not in links:
        await message.answer(f"{Emoji.note.value} Нет ссылки «{name}»")
        return
    del links[name]
    botData["links"] = links
    save_settings(botData)
    await message.answer(f"{Emoji.check.value} Ссылка «{name}» удалена")