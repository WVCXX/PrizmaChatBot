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
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from db import get_user, set_field, all_users, log_action, find_by_username
from utils.text import startInList, hlink, is_id
from ranks import get_rank_name
from emojis import Emoji
from functions_settings import load_settings, save_settings
from config import ADMIN_IDS
from command_lists import admin, snatyVseh, povisit, ponizit, sozdatel
from utils.pagination import paginate, pagination_keyboard
from utils.confirm import (
    ConfirmationError,
    consume_confirmation,
    request_confirmation,
)
router = Router()
@router.message(lambda m: m.text and startInList(m.text, admin)[0])
async def who_admin(message: Message):
    botData = load_settings()
    buckets = {1: [], 2: [], 3: [], 4: [], 5: []}
    for u in await all_users():
        r = u.get("rank", 0)
        if r in buckets:
            buckets[r].append(hlink(u["nick"], u["id"]))
    if not any(buckets.values()):
        await message.answer(f"{Emoji.note.value} В этой беседе анархия")
        return
    parts = []
    for rank in (5, 4, 3, 2, 1):
        users = buckets[rank]
        if not users:
            continue
        stars = Emoji.star.value * rank
        if len(users) == 1:
            parts.append(f"{stars} {get_rank_name(botData, rank, 0)}\n{users[0]}\n")
        else:
            parts.append(f"{stars} {get_rank_name(botData, rank, 4)}\n" +
                         "\n".join(users) + "\n")
    await message.answer("\n".join(parts), parse_mode="HTML")
@router.message(lambda m: m.text and startInList(m.text, snatyVseh)[0])
async def remove_all(message: Message):
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    need = botData["DKsnatvseh"]
    if moder["rank"] < need and message.from_user.id not in ADMIN_IDS:
        await message.answer(
            f"{Emoji.note.value} Команда доступна с ранга "
            f"{get_rank_name(botData, need, 1)} ({need})")
        return
    await request_confirmation(
        message,
        action="snatvseh",
        target_id=0,
        payload={"chat_id": message.chat.id},
        prompt=f"{Emoji.cross.value} Подтвердить снятие всех рангов ниже создателя?",
    )
@router.callback_query(F.data.startswith("confirm:snatvseh:"))
async def cb_confirm_remove_all(cb: CallbackQuery):
    try:
        data = consume_confirmation(cb, "snatvseh")
    except ConfirmationError as exc:
        await cb.answer(str(exc), show_alert=True)
        return
    settings = load_settings()
    moderator = await get_user(cb.from_user.id)
    if (
        not moderator
        or (
            moderator["rank"] < settings["DKsnatvseh"]
            and cb.from_user.id not in ADMIN_IDS
        )
    ):
        await cb.answer("Недостаточно прав; действие отменено", show_alert=True)
        return
    for u in await all_users():
        if u["rank"] < 5:
            await set_field(u["id"], "rank", 0)
    await cb.message.edit_text(
        f"{Emoji.cross.value} Все модераторы разжалованы\n\n"
        f"{Emoji.comment.value} Создатель может ввести "
        f"<code>восстановить создателя</code>", parse_mode="HTML")
    await cb.answer("Ранги сняты")
@router.message(lambda m: m.text and startInList(m.text, sozdatel)[0])
async def restore_creator(message: Message, bot: Bot):
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status != "creator":
            await message.answer(
                f"{Emoji.cross.value} Только создатель чата может это сделать")
            return
    except Exception:
        await message.answer(f"{Emoji.cross.value} Не удалось проверить права")
        return
    await set_field(message.from_user.id, "rank", 5)
    botData = load_settings()
    await message.answer(
        f"{Emoji.check.value} Вы восстановлены как "
        f"{get_rank_name(botData, 5, 0)}")
@router.message(lambda m: m.text and startInList(m.text, povisit)[0])
async def promote(message: Message):
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    need = botData["DKpovisit"]
    if moder["rank"] < need and message.from_user.id not in ADMIN_IDS:
        await message.answer(
            f"{Emoji.note.value} Команда доступна с ранга "
            f"{get_rank_name(botData, need, 1)} ({need})")
        return
    ok, prefix = startInList(message.text, povisit)
    rest = message.text[len(prefix):].strip()

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        rank_str = rest.split()[0] if rest else ""
    else:
        parts = rest.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer(
                f"{Emoji.note.value} Формат: повысить {{ранг 1-5}} @юзер/ид")
            return
        rank_str, target = parts
        target = target.strip().replace("@", "")
        if is_id(target):
            target_id = int(target)
        else:
            u = await find_by_username(target)
            if not u:
                await message.answer(f"{Emoji.note.value} Нет информации о юзере")
                return
            target_id = u["id"]
    if not rank_str.isdigit():
        await message.answer(f"{Emoji.note.value} Ранг должен быть числом 1-5")
        return
    rank = int(rank_str)
    if not 1 <= rank <= 5:
        await message.answer(f"{Emoji.note.value} Ранг должен быть 1-5")
        return
    if rank > moder["rank"]:
        await message.answer(
            f"{Emoji.note.value} Нельзя назначить ранг выше своего"
        )
        return
    userData = await get_user(target_id)
    if not userData:
        await message.answer(f"{Emoji.note.value} Нет информации о юзере")
        return
    if userData["rank"] >= rank:
        await message.answer(f"{Emoji.note.value} Уже на этой должности или выше")
        return
    await set_field(target_id, "rank", rank)
    await log_action(message.chat.id, moder["id"], target_id, "promote", str(rank))
    await message.answer(
        f"{Emoji.check.value} {hlink(userData['nick'], target_id)} назначен "
        f"{get_rank_name(botData, rank, 3)}", parse_mode="HTML")
@router.message(lambda m: m.text and startInList(m.text, ponizit)[0])
async def demote(message: Message):
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    need = botData["DKpovisit"]
    if moder["rank"] < need and message.from_user.id not in ADMIN_IDS:
        await message.answer(
            f"{Emoji.note.value} Команда доступна с ранга "
            f"{get_rank_name(botData, need, 1)} ({need})")
        return
    if not message.reply_to_message:
        await message.answer(f"{Emoji.note.value} Ответьте на сообщение")
        return
    target_id = message.reply_to_message.from_user.id
    userData = await get_user(target_id)
    if not userData or userData["rank"] <= 0:
        await message.answer(f"{Emoji.note.value} Пользователь и так не модератор")
        return
    if userData["rank"] >= moder["rank"]:
        await message.answer(f"{Emoji.note.value} Нельзя понизить равного или выше")
        return
    await request_confirmation(
        message,
        action="demote",
        target_id=target_id,
        payload={"chat_id": message.chat.id},
        prompt=f"{Emoji.minus.value} Подтвердить разжалование "
        f"{hlink(userData['nick'], target_id)}?",
    )
@router.callback_query(F.data.startswith("confirm:demote:"))
async def cb_confirm_demote(cb: CallbackQuery):
    try:
        data = consume_confirmation(cb, "demote")
    except ConfirmationError as exc:
        await cb.answer(str(exc), show_alert=True)
        return
    settings = load_settings()
    moderator = await get_user(cb.from_user.id)
    target = await get_user(data["target_id"])
    if (
        not moderator
        or (
            moderator["rank"] < settings["DKpovisit"]
            and cb.from_user.id not in ADMIN_IDS
        )
        or not target
        or target["rank"] <= 0
        or target["rank"] >= moderator["rank"]
    ):
        await cb.answer("Права изменились; действие отменено", show_alert=True)
        return
    await set_field(data["target_id"], "rank", 0)
    await log_action(
        data["chat_id"], moderator["id"], data["target_id"], "demote"
    )
    await cb.message.edit_text(
        f"{Emoji.minus.value} {hlink(target['nick'], target['id'])} разжалован",
        parse_mode="HTML",
    )
    await cb.answer("Ранг понижен")
@router.message(Command("get", "гет"))
async def cmd_get(message: Message):
    moder = await get_user(message.from_user.id)
    if moder["rank"] < 4 and message.from_user.id not in ADMIN_IDS:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    botData = load_settings()
    keys = ["varnLimit", "DKmute", "DKvarn", "DKban", "DKkick",
            "DKpovisit", "symbolLimit"]
    lines = ["⚙️ <b>Настройки</b>"]
    for k in keys:
        lines.append(f"• <code>{k}</code>: {botData[k]}")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("set", "сет"))
async def cmd_set(message: Message):
    moder = await get_user(message.from_user.id)
    if moder["rank"] < 5 and message.from_user.id not in ADMIN_IDS:
        await message.answer(f"{Emoji.note.value} Только создатель")
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(f"{Emoji.note.value} Формат: /set varnLimit 50")
        return
    key, val = parts[1], parts[2]
    botData = load_settings()
    if key not in botData:
        await message.answer(f"{Emoji.note.value} Неизвестный ключ")
        return
    int_keys = {"varnLimit", "DKmute", "DKvarn", "DKban", "DKkick",
                "DKpovisit", "DKsnatvseh", "DKvarnLimit", "symbolLimit"}
    if key in int_keys:
        if not val.isdigit():
            await message.answer(f"{Emoji.note.value} Значение должно быть числом")
            return
        val = int(val)
    botData[key] = val
    save_settings(botData)
    await message.answer(f"{Emoji.check.value} {key} = {val}")
@router.message(Command("admins", "админы"))
async def cmd_admins(message: Message):
    text, keyboard = await _admins_page(1)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
async def _admins_page(page: int) -> tuple[str, InlineKeyboardMarkup | None]:
    botData = load_settings()
    users = await all_users()
    ranked_users = [
        user
        for rank in (5, 4, 3, 2, 1)
        for user in users
        if user["rank"] == rank
    ]
    page_users, current_page, total_pages = paginate(ranked_users, page)
    buckets: dict[int, list[str]] = {1: [], 2: [], 3: [], 4: [], 5: []}
    for user in page_users:
        buckets[user["rank"]].append(hlink(user["nick"], user["id"]))
    lines = []
    for rank in (5, 4, 3, 2, 1):
        if not buckets[rank]:
            continue
        stars = Emoji.star.value * rank
        if len(buckets[rank]) == 1:
            lines.append(f"{stars} {get_rank_name(botData, rank, 0)}\n{buckets[rank][0]}")
        else:
            lines.append(f"{stars} {get_rank_name(botData, rank, 4)}\n" +
                         "\n".join(buckets[rank]))
    if not lines:
        return "В чате анархия", None
    return "\n\n".join(lines), pagination_keyboard(
        "admins", current_page, total_pages
    )
@router.callback_query(F.data.startswith("page:admins:"))
async def cb_admins_page(cb: CallbackQuery):
    try:
        page = int(cb.data.split(":")[2])
    except (AttributeError, IndexError, ValueError):
        await cb.answer("Некорректная страница", show_alert=True)
        return
    text, keyboard = await _admins_page(page)
    await cb.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await cb.answer()