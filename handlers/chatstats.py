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
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from db import _conn
from emojis import Emoji
router = Router()
WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
def _bar(value: int, max_value: int, width: int = 12) -> str:
    if max_value <= 0:
        return "░" * width
    filled = int(round(value / max_value * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)
async def _stats_hour(chat_id: int, date: str) -> list[dict]:
    async with _conn.execute(
        "SELECT hour, count FROM message_stats WHERE chat_id=? AND date=? ORDER BY hour",
        (chat_id, date),
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]
async def _stats_day(chat_id: int, days: int = 14) -> list[dict]:
    since = (datetime.date.today() - datetime.timedelta(days=days - 1)).isoformat()
    async with _conn.execute(
        "SELECT date, SUM(count) AS total FROM message_stats "
        "WHERE chat_id=? AND date>=? GROUP BY date ORDER BY date",
        (chat_id, since),
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]
async def _stats_week(chat_id: int, weeks: int = 8) -> list[dict]:
    since = (datetime.date.today() - datetime.timedelta(weeks=weeks)).isoformat()
    async with _conn.execute(
        "SELECT strftime('%Y-W%W', date) AS wk, SUM(count) AS total "
        "FROM message_stats WHERE chat_id=? AND date>=? "
        "GROUP BY wk ORDER BY wk",
        (chat_id, since),
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]
async def _stats_month(chat_id: int, months: int = 6) -> list[dict]:
    since = (datetime.date.today() - datetime.timedelta(days=months * 31)).isoformat()
    async with _conn.execute(
        "SELECT strftime('%Y-%m', date) AS mo, SUM(count) AS total "
        "FROM message_stats WHERE chat_id=? AND date>=? "
        "GROUP BY mo ORDER BY mo",
        (chat_id, since),
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]
async def _stats_all(chat_id: int) -> dict:
    async with _conn.execute(
        "SELECT COUNT(*) AS days, SUM(count) AS total, "
        "MIN(date) AS first, MAX(date) AS last "
        "FROM message_stats WHERE chat_id=?",
        (chat_id,),
    ) as cur:
        row = await cur.fetchone()
        return dict(row) if row else {}
@router.message(Command("chat_stats", "стата_чата"))
async def cmd_chat_stats(message: Message):
    data = await _stats_all(message.chat.id)
    if not data or not data.get("total"):
        await message.answer(f"{Emoji.note.value} Пока нет данных")
        return
    total = data["total"]
    days = data["days"] or 1
    avg = total / days
    text = (
        f"📊 <b>Статистика чата</b>\n"
        f"\n"
        f"💬 Всего сообщений: <b>{total}</b>\n"
        f"📅 Дней с данными: <b>{days}</b>\n"
        f"📈 В среднем в день: <b>{avg:.1f}</b>\n"
        f"🕐 Первая запись: <b>{data['first']}</b>\n"
        f"🕓 Последняя: <b>{data['last']}</b>\n"
        f"\n"
        f"Подробнее:\n"
        f"• <code>стата по часам</code>\n"
        f"• <code>стата по дням</code>\n"
        f"• <code>стата по неделям</code>\n"
        f"• <code>стата по месяцам</code>\n"
        f"• <code>стата за всё время</code>"
    )
    await message.answer(text, parse_mode="HTML")
@router.message(Command("chat_stats_hour", "стата_по_часам"))
async def cmd_chat_stats_hour(message: Message):
    today = datetime.date.today().isoformat()
    rows = await _stats_hour(message.chat.id, today)
    if not rows:
        await message.answer(f"{Emoji.note.value} Сегодня ещё не было сообщений")
        return
    by_hour = {r["hour"]: r["count"] for r in rows}
    peak = max(by_hour.values())
    lines = [f"🕐 <b>Активность за сегодня</b> (пик: {peak})\n"]
    for h in range(24):
        c = by_hour.get(h, 0)
        bar = _bar(c, peak, 12)
        lines.append(f"<code>{h:02d}:00</code> {bar} {c}")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("chat_stats_day", "стата_по_дням"))
async def cmd_chat_stats_day(message: Message):
    rows = await _stats_day(message.chat.id, days=14)
    if not rows:
        await message.answer(f"{Emoji.note.value} Нет данных")
        return
    peak = max(r["total"] for r in rows)
    lines = ["📅 <b>Последние 14 дней</b>\n"]
    for r in rows:
        bar = _bar(r["total"], peak, 10)
        lines.append(f"<code>{r['date']}</code> {bar} {r['total']}")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("chat_stats_week", "стата_по_неделям"))
async def cmd_chat_stats_week(message: Message):
    rows = await _stats_week(message.chat.id, weeks=8)
    if not rows:
        await message.answer(f"{Emoji.note.value} Нет данных")
        return
    peak = max(r["total"] for r in rows)
    lines = ["🗓 <b>Последние 8 недель</b>\n"]
    for r in rows:
        bar = _bar(r["total"], peak, 10)
        lines.append(f"<code>{r['wk']}</code> {bar} {r['total']}")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("chat_stats_month", "стата_по_месяцам"))
async def cmd_chat_stats_month(message: Message):
    rows = await _stats_month(message.chat.id, months=6)
    if not rows:
        await message.answer(f"{Emoji.note.value} Нет данных")
        return
    peak = max(r["total"] for r in rows)
    lines = ["📆 <b>Последние 6 месяцев</b>\n"]
    for r in rows:
        bar = _bar(r["total"], peak, 10)
        lines.append(f"<code>{r['mo']}</code> {bar} {r['total']}")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("chat_stats_all", "стата_за_всё_время"))
async def cmd_chat_stats_all(message: Message):
    rows = await _stats_day(message.chat.id, days=3650)
    if not rows:
        await message.answer(f"{Emoji.note.value} Нет данных")
        return
    total = sum(r["total"] for r in rows)
    peak_row = max(rows, key=lambda r: r["total"])
    lines = [
        f"🏛 <b>За всё время</b>\n",
        f"💬 Всего: <b>{total}</b>",
        f"📅 Дней с сообщениями: <b>{len(rows)}</b>",
        f"🔥 Пик: <b>{peak_row['date']}</b> — {peak_row['total']} сообщений",
        "",
        "По месяцам:",
    ]
    by_month: dict[str, int] = {}
    for r in rows:
        mo = r["date"][:7]
        by_month[mo] = by_month.get(mo, 0) + r["total"]
    peak_m = max(by_month.values())
    for mo in sorted(by_month):
        bar = _bar(by_month[mo], peak_m, 10)
        lines.append(f"<code>{mo}</code> {bar} {by_month[mo]}")
    await message.answer("\n".join(lines), parse_mode="HTML")