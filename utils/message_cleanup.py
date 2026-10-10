"""
Отложенное удаление сервисных сообщений бота.

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
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message
log = logging.getLogger("iris")
_deletion_tasks: set[asyncio.Task[None]] = set()
async def _delete_after(message: Message, delay: int) -> None:
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except TelegramAPIError as exc:
        log.debug("Не удалось удалить сервисное сообщение: %s", exc)
def schedule_message_deletion(message: Message, delay: int) -> None:
    task = asyncio.create_task(_delete_after(message, delay))
    _deletion_tasks.add(task)
    task.add_done_callback(_deletion_tasks.discard)