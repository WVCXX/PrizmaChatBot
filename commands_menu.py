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
from aiogram.types import BotCommand
USER_COMMANDS = [
    BotCommand(command="start",       description="Приветствие"),
    BotCommand(command="help",        description="Все команды"),
    BotCommand(command="profile",     description="Профиль"),
    BotCommand(command="me",          description="Свой профиль"),
    BotCommand(command="top",         description="Топ по репутации"),
    BotCommand(command="top_active",  description="Топ по сообщениям"),
    BotCommand(command="rep",         description="+1 репутации (ответом)"),
    BotCommand(command="report",      description="Жалоба на юзера (ответом)"),
    BotCommand(command="ping",        description="Проверка работы"),
    BotCommand(command="chat_stats",  description="Статистика чата"),
    BotCommand(command="balance",     description="Баланс"),
    BotCommand(command="daily",       description="Ежедневный бонус"),
    BotCommand(command="bank",        description="Банк"),
    BotCommand(command="shop",        description="Магазин"),
]
MODER_COMMANDS = USER_COMMANDS + [
    BotCommand(command="mod",         description="🛡 Панель действий (ответом)"),
    BotCommand(command="mute",        description="🛡 Мут"),
    BotCommand(command="unmute",      description="🛡 Размут"),
    BotCommand(command="mute_list",   description="🛡 Активные муты"),
    BotCommand(command="warn",        description="🛡 Предупреждение"),
    BotCommand(command="warn_list",   description="🛡 Список варнов"),
    BotCommand(command="kick",        description="🛡 Кикнуть"),
    BotCommand(command="ban",         description="🛡 Забанить"),
    BotCommand(command="delete",      description="🛡 Удалить сообщение"),
    BotCommand(command="note",        description="🛡 Заметка о юзере"),
    BotCommand(command="notes",       description="🛡 Заметки"),
    BotCommand(command="moder_stats", description="🛡 Стата модера"),
]
ADMIN_COMMANDS = MODER_COMMANDS + [
    BotCommand(command="promote",     description="👑 Повысить"),
    BotCommand(command="demote",      description="👑 Понизить"),
    BotCommand(command="admins",      description="👑 Список админов"),
    BotCommand(command="stats",       description="👑 Статистика чата"),
    BotCommand(command="get",         description="👑 Настройки"),
    BotCommand(command="set",         description="👑 Изменить настройку"),
    BotCommand(command="snatvseh",    description="👑 Снять всех"),
]
async def setup_commands(bot):
    await bot.set_my_commands(USER_COMMANDS)