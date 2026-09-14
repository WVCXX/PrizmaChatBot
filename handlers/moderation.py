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
from aiogram.types import Message, ChatPermissions,CallbackQuery
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
from db import (get_user, inc_field, set_field, log_action,
                add_mute, remove_mute, active_mutes, add_note, get_notes)
from utils.text import hlink, toSymbol
from utils.time_parser import t2s, toDate
from utils.users import resolve_user
from ranks import get_rank_name
from emojis import Emoji
from functions_settings import load_settings
from config import LOG_CHANNEL_ID
from utils.users import get_or_create
from keyboards.moderation import mod_actions_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
router = Router()
MUTE_PERMS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
)
FULL_PERMS = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
)
@router.message(Command("mute", "мут"))
async def cmd_mute(message: Message, bot: Bot):
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    if moder["rank"] < botData["DKmute"]:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    need = botData["DKmute"]
    if moder["rank"] < need:
        await message.answer(
            f"{Emoji.note.value} Нужен ранг {get_rank_name(botData, need, 1)} ({need})")
        return
    parts = message.text.split(maxsplit=1)
    rest = parts[1].strip() if len(parts) > 1 else ""

    target, rest = await resolve_user(message, rest)
    if not target:
        await message.answer(f"{Emoji.note.value} Нет информации о юзере")
        return
    if target["rank"] >= moder["rank"]:
        await message.answer(f"{Emoji.note.value} Нельзя замутить равного или выше")
        return
    time_part = toSymbol(rest, "\n").strip()
    prichina = rest[len(time_part):].lstrip("\n").strip() if "\n" in rest else ""
    try:
        if time_part.upper().startswith("ДО"):
            dateTo = toDate(time_part[2:].strip())
            label = time_part[2:].strip()
            prefix = "до"
        else:
            dateTo = t2s(time_part)
            label = time_part
            prefix = "на"
    except Exception:
        await message.answer(
            f"{Emoji.cross.value} Формат: <code>мут 1 час</code> "
            f"или <code>мут до 2030.12.31 23:59:59</code>", parse_mode="HTML")
        return
    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target["id"],
            permissions=MUTE_PERMS,
            until_date=dateTo,
        )
    except TelegramAPIError as e:
        await message.answer(f"{Emoji.cross.value} Не удалось замутить: {e}")
        return
    await add_mute(target["id"], message.chat.id, dateTo.isoformat(), prichina)
    await log_action(message.chat.id, moder["id"], target["id"], "mute", label, prichina)
    text = (f"{Emoji.mute.value} {hlink(target['nick'], target['id'])} "
            f"лишается права слова {prefix} {label}\n"
            f"{Emoji.user.value} Модератор: {hlink(moder['nick'], moder['id'])}")
    if prichina:
        text += f"\n{Emoji.comment.value} Причина: {prichina}"
    await message.answer(text, parse_mode="HTML")
@router.message(Command("unmute", "размут"))
async def cmd_unmute(message: Message, bot: Bot):
    moder = await get_user(message.from_user.id)
    botData = load_settings()
    if moder["rank"] < botData["DKmute"]:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    if not message.reply_to_message:
        await message.answer(f"{Emoji.note.value} Ответь на сообщение")
        return
    uid = message.reply_to_message.from_user.id
    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id, user_id=uid, permissions=FULL_PERMS)
    except TelegramAPIError as e:
        await message.answer(f"{Emoji.cross.value} Ошибка: {e}")
        return
    await remove_mute(uid)
    target = await get_user(uid)
    await message.answer(
        f"{Emoji.check.value} {hlink(target['nick'], uid)} размучен",
        parse_mode="HTML")
@router.message(Command("mute_list", "муты"))
async def cmd_mute_list(message: Message):
    mutes = await active_mutes()
    if not mutes:
        await message.answer("🔇 Активных мутов нет")
        return
    lines = [f"🔇 Активные муты ({len(mutes)}):"]
    for m in mutes:
        u = await get_user(m["target_id"])
        nick = hlink(u["nick"], u["id"]) if u else f"id{m['target_id']}"
        lines.append(f"• {nick} — до {m['until']} ({m['reason'] or 'без причины'})")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("warn", "варн"))
async def cmd_warn(message: Message, bot: Bot):
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    need = botData["DKvarn"]
    if moder["rank"] < need:
        await message.answer(
            f"{Emoji.note.value} Нужен ранг {get_rank_name(botData, need, 1)} ({need})")
        return
    parts = message.text.split(maxsplit=1)
    rest = parts[1].strip() if len(parts) > 1 else ""
    count = 1
    count_str = ""
    for ch in rest:
        if ch in "0123456789-":
            count_str += ch
        else:
            break
    if count_str and count_str not in ("-",):
        count = int(count_str)
        rest = rest[len(count_str):].strip()

    target, rest = await resolve_user(message, rest)
    if not target:
        await message.answer(f"{Emoji.note.value} Нет информации о юзере")
        return
    if target["rank"] >= moder["rank"]:
        await message.answer(f"{Emoji.note.value} Нельзя выдать равному или выше")
        return
    prichina = rest.lstrip("\n").strip()
    await inc_field(target["id"], "varn", count)
    target = await get_user(target["id"])
    await log_action(message.chat.id, moder["id"], target["id"], "warn",
                     str(count), prichina)
    if target["varn"] >= botData["varnLimit"]:
        try:
            await bot.ban_chat_member(chat_id=message.chat.id, user_id=target["id"])
        except TelegramAPIError as e:
            await message.answer(f"{Emoji.cross.value} Ошибка бана: {e}")
            return
        await set_field(target["id"], "varn", 0)
        await message.answer(
            f"{Emoji.ban.value} {hlink(target['nick'], target['id'])} получает бан "
            f"навсегда (лимит предупреждений)", parse_mode="HTML")
        return
    text = (f"{Emoji.exclamation.value} {hlink(target['nick'], target['id'])} получает "
            f"предупреждение ({target['varn']}/{botData['varnLimit']})\n"
            f"Выдано: {count}\n"
            f"Модератор: {hlink(moder['nick'], moder['id'])}")
    if prichina:
        text += f"\n{Emoji.comment.value} Причина: {prichina}"
    await message.answer(text, parse_mode="HTML")
@router.message(Command("warn_list", "варны"))
async def cmd_warn_list(message: Message):
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    if moder["rank"] < botData["DKvarn"]:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    from db import all_users
    users = [u for u in await all_users() if u["varn"] > 0]
    users.sort(key=lambda u: u["varn"], reverse=True)
    if not users:
        await message.answer("⚠️ Предупреждённых нет")
        return
    lines = [f"⚠️ Предупреждённые ({len(users)}):"]
    for u in users[:30]:
        lines.append(f"• {hlink(u['nick'], u['id'])} — {u['varn']}")
    await message.answer("\n".join(lines), parse_mode="HTML")
@router.message(Command("kick", "кик"))
async def cmd_kick(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer(f"{Emoji.note.value} Ответь на сообщение")
        return
    moder = await get_user(message.from_user.id)
    botData = load_settings()
    if moder["rank"] < botData["DKkick"]:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    uid = message.reply_to_message.from_user.id
    target = await get_or_create(message.reply_to_message.from_user)
    if target["rank"] >= moder["rank"]:
        await message.answer(f"{Emoji.note.value} Нельзя кикнуть равного или выше")
        return
    try:
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=uid)
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=uid)
    except TelegramAPIError as e:
        await message.answer(f"{Emoji.cross.value} Ошибка: {e}")
        return
    await log_action(message.chat.id, moder["id"], uid, "kick")
    await message.answer(
        f"{Emoji.kick.value} {hlink(target['nick'], uid)} кикнут", parse_mode="HTML")
@router.message(Command("ban", "бан"))
async def cmd_ban(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer(f"{Emoji.note.value} Ответь на сообщение")
        return
    moder = await get_user(message.from_user.id)
    botData = load_settings()
    if moder["rank"] < botData["DKban"]:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    uid = message.reply_to_message.from_user.id
    target = await get_or_create(message.reply_to_message.from_user)
    if target["rank"] >= moder["rank"]:
        await message.answer(f"{Emoji.note.value} Нельзя забанить равного или выше")
        return
    try:
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=uid)
    except TelegramAPIError as e:
        await message.answer(f"{Emoji.cross.value} Ошибка: {e}")
        return
    await log_action(message.chat.id, moder["id"], uid, "ban")
    await message.answer(
        f"{Emoji.ban.value} {hlink(target['nick'], uid)} забанен", parse_mode="HTML")
@router.message(Command("delete", "удалить"))
async def cmd_delete(message: Message):
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    if moder["rank"] < botData["DKkick"]:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    if not message.reply_to_message:
        await message.answer(f"{Emoji.note.value} Ответь на сообщение")
        return
    try:
        await message.reply_to_message.delete()
        await message.delete()
    except TelegramAPIError:
        pass
@router.message(Command("report", "репорт"))
async def cmd_report(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer(f"{Emoji.note.value} Ответь на сообщение нарушителя")
        return
    botData = load_settings()
    parts = message.text.split(maxsplit=1)
    reason = parts[1].strip() if len(parts) > 1 else "без причины"
    target = message.reply_to_message.from_user
    text = (f"📨 <b>Жалоба</b>\n"
            f"Чат: {message.chat.title}\n"
            f"От: {hlink(message.from_user.full_name, message.from_user.id)}\n"
            f"На: {hlink(target.full_name, target.id)}\n"
            f"Причина: {reason}")
    if LOG_CHANNEL_ID:
        try:
            await bot.send_message(LOG_CHANNEL_ID, text, parse_mode="HTML")
        except TelegramAPIError:
            pass
    from db import all_users
    for u in await all_users():
        if u["rank"] >= botData["DKvarn"]:
            try:
                await bot.send_message(u["id"], text, parse_mode="HTML")
            except (TelegramForbiddenError, TelegramAPIError):
                pass
    await message.answer(
        f"📨 Жалоба на {hlink(target.full_name, target.id)} отправлена.",
        parse_mode="HTML")
@router.message(Command("note", "заметка"))
async def cmd_note(message: Message):
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    if moder["rank"] < botData["DKvarn"]:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    if not message.reply_to_message:
        await message.answer(f"{Emoji.note.value} Ответь на сообщение")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(f"{Emoji.note.value} Напиши текст заметки")
        return
    uid = message.reply_to_message.from_user.id
    await add_note(uid, message.from_user.id, parts[1].strip())
    await message.answer(f"{Emoji.check.value} Заметка добавлена")
@router.message(Command("notes", "заметки"))
async def cmd_notes(message: Message):
    botData = load_settings()
    moder = await get_user(message.from_user.id)
    if moder["rank"] < botData["DKvarn"]:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    if not message.reply_to_message:
        await message.answer(f"{Emoji.note.value} Ответь на сообщение")
        return
    uid = message.reply_to_message.from_user.id
    notes = await get_notes(uid)
    if not notes:
        await message.answer("📝 Заметок нет")
        return
    lines = [f"📝 Заметки о {hlink(message.reply_to_message.from_user.full_name, uid)}:"]
    for n in notes:
        lines.append(f"• [{n['ts']}] {n['text']}")
    await message.answer("\n".join(lines), parse_mode="HTML")

class ModAction(StatesGroup):
    waiting_reason = State()
@router.message(Command("mod", "мод"))
async def cmd_mod(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer(
            f"{Emoji.note.value} Ответь на сообщение нарушителя и напиши /mod"
        )
        return
    moder = await get_user(message.from_user.id)
    botData = load_settings()
    if moder["rank"] < botData["DKmute"]:
        await message.answer(f"{Emoji.note.value} Недостаточно прав")
        return
    target = message.reply_to_message.from_user
    target_db = await get_or_create(target)
    if target_db["rank"] >= moder["rank"]:
        await message.answer(
            f"{Emoji.note.value} Нельзя применять действия к равному или выше"
        )
        return
    kb = mod_actions_keyboard(target.id)
    await message.answer(
        f"Действия для <b>{target.full_name}</b> (id <code>{target.id}</code>):",
        reply_markup=kb,
        parse_mode="HTML",
    )
@router.callback_query(F.data.startswith("mod:"))
async def cb_mod_action(cb: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        _, action, arg, target_id_str = cb.data.split(":")
        target_id = int(target_id_str)
    except (ValueError, AttributeError):
        await cb.answer("Некорректная кнопка", show_alert=True)
        return
    moder = await get_user(cb.from_user.id)
    botData = load_settings()
    if action == "cancel":
        try:
            await cb.message.delete()
        except TelegramAPIError:
            pass
        await cb.answer("Отменено")
        return
    target = await get_user(target_id)
    if not target:
        await cb.answer("Юзер не найден", show_alert=True)
        return
    if target["rank"] >= moder["rank"]:
        await cb.answer("Нельзя применить к равному или выше", show_alert=True)
        return
    if action in ("mute", "warn"):
        need = botData["DKmute"] if action == "mute" else botData["DKvarn"]
        if moder["rank"] < need:
            await cb.answer(
                f"Нужен ранг {get_rank_name(botData, need, 1)}", show_alert=True
            )
            return
        await state.set_state(ModAction.waiting_reason)
        await state.update_data(
            action=action,
            arg=arg,
            target_id=target_id,
            chat_id=cb.message.chat.id,
            moder_id=moder["id"],
            message_id=cb.message.message_id,
        )
        label = "мута" if action == "mute" else "варна"
        try:
            await cb.message.edit_text(
                f"✏️ Напиши причину {label} для "
                f"{hlink(target['nick'], target_id)} "
                f"или /skip, чтобы без причины.",
                parse_mode="HTML",
            )
        except TelegramAPIError:
            pass
        await cb.answer()
        return
    if action == "kick":
        need = botData["DKkick"]
        if moder["rank"] < need:
            await cb.answer(f"Нужен ранг {get_rank_name(botData, need, 1)}", show_alert=True)
            return
        try:
            await bot.ban_chat_member(chat_id=cb.message.chat.id, user_id=target_id)
            await bot.unban_chat_member(chat_id=cb.message.chat.id, user_id=target_id)
        except TelegramAPIError as e:
            await cb.answer(f"Ошибка: {e}", show_alert=True)
            return
        await log_action(cb.message.chat.id, moder["id"], target_id, "kick", "", "кнопкой")
        try:
            await cb.message.edit_text(
                f"{Emoji.kick.value} {hlink(target['nick'], target_id)} кикнут",
                parse_mode="HTML",
            )
        except TelegramAPIError:
            pass
        await cb.answer("Кикнут")
        return
    if action == "ban":
        need = botData["DKban"]
        if moder["rank"] < need:
            await cb.answer(f"Нужен ранг {get_rank_name(botData, need, 1)}", show_alert=True)
            return
        try:
            await bot.ban_chat_member(chat_id=cb.message.chat.id, user_id=target_id)
        except TelegramAPIError as e:
            await cb.answer(f"Ошибка: {e}", show_alert=True)
            return
        await log_action(cb.message.chat.id, moder["id"], target_id, "ban", "", "кнопкой")
        try:
            await cb.message.edit_text(
                f"{Emoji.ban.value} {hlink(target['nick'], target_id)} забанен",
                parse_mode="HTML",
            )
        except TelegramAPIError:
            pass
        await cb.answer("Забанен")
        return
    await cb.answer("Неизвестное действие", show_alert=True)

@router.message(ModAction.waiting_reason)
async def mod_reason(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    action = data.get("action")
    arg = data.get("arg", "1")
    target_id = data.get("target_id")
    chat_id = data.get("chat_id")
    if not target_id:
        await message.answer("⚠️ Контекст потерян, начни заново")
        return
    text = (message.text or "").strip()
    if text.lower() == "/skip" or text == "":
        reason = ""
    else:
        reason = text
    try:
        await message.delete()
    except TelegramAPIError:
        pass
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=data["message_id"],
            text="⏳ Применяю...",
        )
    except TelegramAPIError:
        pass
    target = await get_user(target_id)
    moder = await get_user(data["moder_id"])
    botData = load_settings()
    if not target:
        return
    if action == "mute":
        durations = {"1h": "1 час", "1d": "1 день", "7d": "7 дней"}
        label = durations.get(arg, "1 час")
        try:
            dateTo = t2s(label)
        except Exception:
            return
        try:
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=target_id,
                permissions=MUTE_PERMS,
                until_date=dateTo,
            )
        except TelegramAPIError:
            return

        await add_mute(target_id, chat_id, dateTo.isoformat(), reason)
        await log_action(chat_id, moder["id"], target_id, "mute", label, reason)
        result = (
            f"{Emoji.mute.value} {hlink(target['nick'], target_id)} "
            f"лишается права слова на {label}\n"
            f"{Emoji.user.value} Модератор: {hlink(moder['nick'], moder['id'])}"
        )
        if reason:
            result += f"\n{Emoji.comment.value} Причина: {reason}"
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=data["message_id"],
                text=result,
                parse_mode="HTML",
            )
        except TelegramAPIError:
            pass
        return
    if action == "warn":
        await inc_field(target_id, "varn", 1)
        target = await get_user(target_id)
        await log_action(chat_id, moder["id"], target_id, "warn", "1", reason)

        if target["varn"] >= botData["varnLimit"]:
            try:
                await bot.ban_chat_member(chat_id=chat_id, user_id=target_id)
            except TelegramAPIError:
                return
            await set_field(target_id, "varn", 0)
            result = (
                f"{Emoji.ban.value} {hlink(target['nick'], target_id)} "
                f"получает бан навсегда (лимит предупреждений)"
            )
            if reason:
                result += f"\n{Emoji.comment.value} Причина: {reason}"
        else:
            result = (
                f"{Emoji.exclamation.value} {hlink(target['nick'], target_id)} "
                f"получает предупреждение ({target['varn']}/{botData['varnLimit']})\n"
                f"{Emoji.user.value} Модератор: {hlink(moder['nick'], moder['id'])}"
            )
            if reason:
                result += f"\n{Emoji.comment.value} Причина: {reason}"
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=data["message_id"],
                text=result,
                parse_mode="HTML",
            )
        except TelegramAPIError:
            pass
        return