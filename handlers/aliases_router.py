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
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.dispatcher.event.bases import SkipHandler
from aliases import resolve
log = logging.getLogger("iris")
router = Router()
SAFE_NO_REPLY = {
    "help", "me", "profile", "stats", "id", "whois", "ping",
    "version", "rules", "links", "top", "top_active", "top_varn",
    "top_balance", "top_level", "balance", "daily", "bank",
    "shop", "level", "achievements", "roll", "coin", "8ball",
    "choose", "dice", "slot", "quote", "quotes", "random", "mystats",
    "chat_stats", "chat_stats_hour", "chat_stats_day",
    "chat_stats_week", "chat_stats_month", "chat_stats_all",
    "greeting",    "fish", "hunt", "farm", "inventory", "sell",
    "balance", "daily", "pay", "rob", "bank", "shop", "buy",
    "greeting",
}
@router.message(F.text)
async def alias_dispatch(message: Message, bot: Bot):
    if not message.text:
        return
    canon, args = resolve(message.text)
    if not canon:
        return
    explicit = message.text.lstrip()[:1] in "!./"
    if not explicit and not message.reply_to_message:
        if canon not in SAFE_NO_REPLY:
            return
    fake = f"/{canon} {args}".strip() if args else f"/{canon}"
    try:
        message.text = fake
    except Exception:
        pass
    handled = await _call(canon, message, bot)
    if handled:
        raise SkipHandler
async def _call(canon: str, message: Message, bot: Bot) -> bool:
    from handlers import (
        base, admin, moderation, reputation, stats,
        rules as rules_mod,
        whois as whois_mod,
        fun as fun_mod,
        quotes as quotes_mod,
        version as version_mod,
        content as content_mod,
        chatstats as chatstats_mod,
        economy as economy_mod,
    )
    table = {
        "help":         base.cmd_help,
        "me":           base.cmd_me,
        "profile":      base.cmd_profile,
        "id":           base.cmd_id,
        "ping":         base.cmd_ping,
        "version":      version_mod.cmd_version,
        "top":          reputation.cmd_top,
        "rep":          reputation.cmd_rep,
        "stats":        stats.cmd_stats,
        "top_active":   stats.cmd_top_active,
        "top_varn":     stats.cmd_top_varn,
        "mystats":      stats.cmd_stats,
        "chat_stats":       chatstats_mod.cmd_chat_stats,
        "chat_stats_hour":  chatstats_mod.cmd_chat_stats_hour,
        "chat_stats_day":   chatstats_mod.cmd_chat_stats_day,
        "chat_stats_week":  chatstats_mod.cmd_chat_stats_week,
        "chat_stats_month": chatstats_mod.cmd_chat_stats_month,
        "chat_stats_all":   chatstats_mod.cmd_chat_stats_all,
        "admins":       admin.cmd_admins,
        "get":          admin.cmd_get,
        "set":          admin.cmd_set,
        "mute":         moderation.cmd_mute,
        "unmute":       moderation.cmd_unmute,
        "warn":         moderation.cmd_warn,
        "kick":         moderation.cmd_kick,
        "ban":          moderation.cmd_ban,
        "delete":       moderation.cmd_delete,
        "report":       moderation.cmd_report,
        "mod":          moderation.cmd_mod,
        "rules":        rules_mod.cmd_rules,
        "links":        rules_mod.cmd_links,
        "whois":        whois_mod.cmd_whois,
        "dice":         fun_mod.cmd_dice,
        "coin":         fun_mod.cmd_coin,
        "8ball":        fun_mod.cmd_8ball,
        "choose":       fun_mod.cmd_choose,
        "roll":         fun_mod.cmd_roll,
        "quote":        quotes_mod.cmd_quote,
        "quotes":       quotes_mod.cmd_quotes,
        "greeting":     content_mod.cmd_greeting,
        "rule_add":     content_mod.cmd_rule_add,
        "rule_del":     content_mod.cmd_rule_del,
        "rules_reset":  content_mod.cmd_rules_reset,
        "link_add":     content_mod.cmd_link_add,
        "link_del":     content_mod.cmd_link_del,
    }
    fn = table.get(canon)
    if fn is None:
        log.info(f"алиас '{canon}' распознан, но хендлер не реализован")
        return False
    await _invoke(fn, message, bot)
    return True
async def _invoke(fn, message: Message, bot: Bot):
    import inspect
    sig = inspect.signature(fn)
    kwargs = {}
    if "bot" in sig.parameters:
        kwargs["bot"] = bot
    try:
        return await fn(message, **kwargs)
    except TypeError as e:
        log.exception(f"alias invoke error для {getattr(fn, '__name__', fn)}: {e}")