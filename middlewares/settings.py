"""
Middleware для передачи настроек обработчикам обновлений.

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
from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from functions_settings import load_settings
from utils.message_cleanup import schedule_message_deletion
SERVICE_COMMANDS = {
    "mute", "unmute", "mute_list", "warn", "warn_list", "kick", "ban",
    "delete", "report", "note", "notes", "mod", "promote", "demote",
    "snatvseh", "rules_reset", "rule_add", "rule_del", "link_add", "link_del",
    "mod_kb", "mod_kb_off",
}
class SettingsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        settings = load_settings()
        data["settings"] = settings
        result = await handler(event, data)
        if isinstance(event, Message) and settings.get("autodelete_service", 0) > 0:
            text = event.text or ""
            command = text.split(maxsplit=1)[0].lstrip("/").split("@", 1)[0]
            if command.lower() in SERVICE_COMMANDS:
                schedule_message_deletion(
                    event,
                    settings["autodelete_service"],
                )
        return result