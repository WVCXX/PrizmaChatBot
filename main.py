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
from pathlib import Path
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from config import BOT_TOKEN, PROXY_URL, ADMIN_IDS
from db import init_db, close_db, ensure_admin
from middlewares import ErrorMiddleware, UserMiddleware, RateLimitMiddleware
from functions_settings import load_settings
from utils.logs import setup_logging
from utils.backup import backup
from version import __version__, __build_date__
from commands_menu import setup_commands
from handlers import (base, user, admin, moderation, reputation, misc,
                      version, antispam, greeting, stats,
                      rules, whois, fun, quotes, content, aliases_router)
import time
setup_logging()
log = logging.getLogger("iris")
HEARTBEAT_FILE = Path("data/heartbeat.txt")
def _write_heartbeat():
    try:
        HEARTBEAT_FILE.write_text(str(time.time()), encoding="utf-8")
    except Exception:
        pass
async def _heartbeat_loop():
    while True:
        _write_heartbeat()
        await asyncio.sleep(10)
async def _periodic_backup():
    while True:
        await asyncio.sleep(86400)
        try:
            backup()
            log.info("бэкап создан")
        except Exception as e:
            log.exception(f"ошибка бэкапа: {e}")
async def main():
    await init_db()
    load_settings()
    if PROXY_URL:
        log.info(f"прокси: {PROXY_URL.split('@')[-1]}")
        session = AiohttpSession(proxy=PROXY_URL, timeout=120)
    else:
        session = AiohttpSession(timeout=120)
    for admin_id in ADMIN_IDS:
        await ensure_admin(admin_id, rank=5)
    if ADMIN_IDS:
        log.info(f"админов из .env: {len(ADMIN_IDS)}")
    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    me = await bot.get_me()
    log.info(f"@{me.username} (Iris v{__version__}, build {__build_date__})")
    try:
        await setup_commands(bot)
        log.info("меню команд зарегистрировано")
    except Exception as e:
        log.exception(f"не удалось зарегистрировать меню: {e}")
    dp = Dispatcher()
    user_mw = UserMiddleware()
    error_mw = ErrorMiddleware()
    dp.message.outer_middleware(error_mw)
    dp.callback_query.outer_middleware(error_mw)
    dp.chat_member.outer_middleware(error_mw)
    dp.message.middleware(user_mw)
    dp.message.middleware(RateLimitMiddleware(limit=15, window=1.0))
    dp.include_router(aliases_router.router)
    dp.include_router(base.router)
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(moderation.router)
    dp.include_router(reputation.router)
    dp.include_router(misc.router)
    dp.include_router(version.router)
    dp.include_router(greeting.router)
    dp.include_router(stats.router)
    dp.include_router(rules.router)
    dp.include_router(whois.router)
    dp.include_router(fun.router)
    dp.include_router(quotes.router)
    dp.include_router(content.router)
    dp.include_router(antispam.router)
    hb_task = asyncio.create_task(_heartbeat_loop())
    backup_task = asyncio.create_task(_periodic_backup())
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        hb_task.cancel()
        backup_task.cancel()
        try:
            await user_mw.flush()
        except Exception:
            log.exception("flush failed")
        try:
            await close_db()
        except Exception:
            log.exception("close_db failed")
        await bot.session.close()
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("остановлен")