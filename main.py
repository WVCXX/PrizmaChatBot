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
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from config import BOT_TOKEN, PROXY_URL
from db import init_db
from middlewares import UserMiddleware, RateLimitMiddleware
from utils.logs import setup_logging
from utils.backup import backup
from version import __version__, __build_date__
from handlers import base, user, admin, moderation, reputation, misc, version
setup_logging()
log = logging.getLogger("iris")
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
    if PROXY_URL:
        log.info(f"прокси: {PROXY_URL.split('@')[-1]}")
        session = AiohttpSession(proxy=PROXY_URL, timeout=120)
    else:
        session = AiohttpSession(timeout=120)

    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    me = await bot.get_me()
    log.info(f"@{me.username} (Iris v{__version__}, build {__build_date__})")
    dp = Dispatcher()
    dp.message.middleware(UserMiddleware())
    dp.message.middleware(RateLimitMiddleware(limit=15, window=1.0))
    dp.include_router(base.router)
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(moderation.router)
    dp.include_router(reputation.router)
    dp.include_router(misc.router)
    dp.include_router(version.router)
    asyncio.create_task(_periodic_backup())
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        try:
            backup()
        except Exception:
            log.exception("Backup failed")
        await bot.session.close()
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("остановлен")