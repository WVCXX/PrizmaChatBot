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
import random
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from db import get_user, inc_field, set_field, inv_add
from utils.text import hlink, is_id
from utils.users import get_or_create, resolve_user
from emojis import Emoji
router = Router()
DAILY_BASE = 100
DAILY_STREAK_BONUS = 25
DAILY_COOLDOWN = 24 * 60 * 60
ROB_COOLDOWN = 2 * 60 * 60
ROB_CHANCE = 0.30
SHOP_ITEMS = {
    "seed_wheat":   ("🌾 Трусы Вики",      20),
    "seed_corn":    ("🌽 Трусы Джимбо",     60),
    "seed_pumpkin": ("🎃 Трусы Алёны",       160),
    "seed_gold":    ("🌟 Трусы Туберкулёзника", 800),
}
@router.message(Command("balance", "бал", "баланс"))
async def cmd_balance(message: Message):
    if message.reply_to_message:
        target = await get_or_create(message.reply_to_message.from_user)
    else:
        target = await get_user(message.from_user.id)
    if not target:
        await message.answer(f"{Emoji.note.value} Нет информации")
        return
    total = target["balance"] + target["bank"]
    await message.answer(
        f"💰 <b>{target['nick']}</b>\n"
        f"👛 Кошелёк: <b>{target['balance']}</b> 💎\n"
        f"🏦 Банк: <b>{target['bank']}</b> 💎\n"
        f"💠 Всего: <b>{total}</b> 💎",
        parse_mode="HTML",
    )
@router.message(Command("daily", "дейли"))
async def cmd_daily(message: Message):
    u = await get_user(message.from_user.id)
    if not u:
        await message.answer(f"{Emoji.note.value} Тебя нет в БД")
        return
    now = datetime.datetime.now()
    streak = 1
    if u.get("last_daily"):
        try:
            last = datetime.datetime.fromisoformat(u["last_daily"])
            elapsed = (now - last).total_seconds()
            if elapsed < DAILY_COOLDOWN:
                left = int(DAILY_COOLDOWN - elapsed)
                h, rem = divmod(left, 3600)
                m, _ = divmod(rem, 60)
                await message.answer(
                    f"{Emoji.note.value} Уже получал. Осталось: {h}ч {m}м"
                )
                return
            if elapsed < DAILY_COOLDOWN * 2:
                streak = (u.get("daily_streak") or 0) + 1
        except Exception:
            pass
    reward = DAILY_BASE + DAILY_STREAK_BONUS * min(streak - 1, 10)
    await inc_field(u["id"], "balance", reward)
    await set_field(u["id"], "last_daily", now.isoformat())
    await set_field(u["id"], "daily_streak", streak)
    await message.answer(
        f"🎁 Ежедневный бонус: <b>+{reward}</b> 💎\n"
        f"🔥 Стрик: <b>{streak}</b> дн.",
        parse_mode="HTML",
    )
@router.message(Command("pay", "перевод"))
async def cmd_pay(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            f"{Emoji.note.value} Формат: <code>перевод @user 100</code>",
            parse_mode="HTML",
        )
        return
    target_arg, amount_str = parts[1], parts[2]
    if not amount_str.isdigit() or int(amount_str) <= 0:
        await message.answer(f"{Emoji.note.value} Сумма должна быть числом > 0")
        return
    amount = int(amount_str)
    target_arg = target_arg.replace("@", "")
    if is_id(target_arg):
        target = await get_user(int(target_arg))
    else:
        target, _ = await resolve_user(message, target_arg)
    if not target:
        await message.answer(f"{Emoji.note.value} Нет информации о юзере")
        return
    if target["id"] == message.from_user.id:
        await message.answer(f"{Emoji.note.value} Себе нельзя")
        return
    me = await get_user(message.from_user.id)
    if me["balance"] < amount:
        await message.answer(f"{Emoji.note.value} Недостаточно 💎")
        return
    await inc_field(me["id"], "balance", -amount)
    await inc_field(target["id"], "balance", amount)
    await message.answer(
        f"💸 {hlink(me['nick'], me['id'])} → "
        f"{hlink(target['nick'], target['id'])}: <b>{amount}</b> 💎",
        parse_mode="HTML",
    )
@router.message(Command("rob", "ограбить"))
async def cmd_rob(message: Message):
    if not message.reply_to_message:
        await message.answer(
            f"{Emoji.note.value} Ответь на сообщение жертвы"
        )
        return
    me = await get_user(message.from_user.id)
    if not me:
        await message.answer(f"{Emoji.note.value} Ты умрешь")
        return
    victim = await get_or_create(message.reply_to_message.from_user)
    if victim["id"] == me["id"]:
        await message.answer(f"{Emoji.note.value} Себя нельзя")
        return
    now = datetime.datetime.now()
    if me.get("last_rob"):
        try:
            last = datetime.datetime.fromisoformat(me["last_rob"])
            if (now - last).total_seconds() < ROB_COOLDOWN:
                left = int(ROB_COOLDOWN - (now - last).total_seconds())
                m, s = divmod(left, 60)
                await message.answer(
                    f"{Emoji.note.value} Рано. Осталось: {m}м {s}с"
                )
                return
        except Exception:
            pass
    if victim["balance"] < 50:
        await message.answer(f"{Emoji.note.value} У жертвы слишком мало 💎")
        return
    await set_field(me["id"], "last_rob", now.isoformat())
    if random.random() < ROB_CHANCE:
        stolen = max(1, int(victim["balance"] * random.uniform(0.10, 0.25)))
        await inc_field(victim["id"], "balance", -stolen)
        await inc_field(me["id"], "balance", stolen)
        await message.answer(
            f"🦹 Ограбление удалось!\n"
            f"Ты украл <b>{stolen}</b> 💎 у "
            f"{hlink(victim['nick'], victim['id'])}",
            parse_mode="HTML",
        )
    else:
        fine = max(1, int(me["balance"] * 0.10))
        await inc_field(me["id"], "balance", -fine)
        await message.answer(
            f"🚨 Ограбление провалилось!\n"
            f"Штраф: <b>{fine}</b> 💎",
            parse_mode="HTML",
        )
@router.message(Command("bank", "банк"))
async def cmd_bank(message: Message):
    u = await get_user(message.from_user.id)
    if not u:
        await message.answer(f"{Emoji.note.value} Тебя нет в БД")
        return
    parts = message.text.split(maxsplit=2)
    sub = parts[1].lower() if len(parts) > 1 else ""

    if sub in ("положить", "deposit", "вклад", "put"):
        if len(parts) < 3 or not parts[2].isdigit():
            await message.answer(
                f"{Emoji.note.value} Формат: <code>банк положить 100</code>",
                parse_mode="HTML",
            )
            return
        amount = int(parts[2])
        if amount <= 0 or u["balance"] < amount:
            await message.answer(f"{Emoji.note.value} Недостаточно 💎")
            return
        await inc_field(u["id"], "balance", -amount)
        await inc_field(u["id"], "bank", amount)
        await message.answer(
            f"🏦 Внесено: <b>{amount}</b> 💎", parse_mode="HTML"
        )
        return
    if sub in ("снять", "withdraw", "take"):
        if len(parts) < 3 or not parts[2].isdigit():
            await message.answer(
                f"{Emoji.note.value} Формат: <code>банк снять 100</code>",
                parse_mode="HTML",
            )
            return
        amount = int(parts[2])
        if amount <= 0 or u["bank"] < amount:
            await message.answer(f"{Emoji.note.value} Недостаточно 💎 в банке")
            return
        await inc_field(u["id"], "bank", -amount)
        await inc_field(u["id"], "balance", amount)
        await message.answer(
            f"🏦 Снято: <b>{amount}</b> 💎", parse_mode="HTML"
        )
        return
    await message.answer(
        f"🏦 <b>Банк</b>\n"
        f"\n"
        f"👛 Кошелёк: <b>{u['balance']}</b> 💎\n"
        f"🏦 Банк: <b>{u['bank']}</b> 💎\n"
        f"\n"
        f"<code>банк положить N</code> — внести\n"
        f"<code>банк снять N</code> — забрать",
        parse_mode="HTML",
    )
@router.message(Command("shop", "магазин"))
async def cmd_shop(message: Message):
    lines = ["🛒 <b>Магазин</b>\n"]
    for code, (name, price) in SHOP_ITEMS.items():
        lines.append(f"• {name} — <b>{price}</b> 💎 (<code>{code}</code>)")
    lines.append("\nКупить: <code>купить &lt;код&gt; [кол-во]</code>")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("buy", "купить"))
async def cmd_buy(message: Message):
    u = await get_user(message.from_user.id)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer(
            f"{Emoji.note.value} Формат: <code>купить &lt;код&gt; [кол-во]</code>\n"
            f"Магазин: <code>магазин</code>",
            parse_mode="HTML",
        )
        return
    code = parts[1].strip().lower()
    qty = 1
    if len(parts) > 2 and parts[2].strip().isdigit():
        qty = int(parts[2].strip())
    if qty <= 0 or qty > 100:
        await message.answer(f"{Emoji.note.value} Кол-во: 1–100")
        return
    item = SHOP_ITEMS.get(code)
    if not item:
        await message.answer(f"{Emoji.note.value} Нет такого товара")
        return
    name, price = item
    total = price * qty
    if u["balance"] < total:
        await message.answer(
            f"{Emoji.note.value} Нужно {total} 💎, у тебя {u['balance']}"
        )
        return
    await inc_field(u["id"], "balance", -total)
    await inv_add(u["id"], code, qty)
    await message.answer(
        f"🛒 Куплено: <b>{name}</b> ×{qty} за <b>{total}</b> 💎",
        parse_mode="HTML",
    )