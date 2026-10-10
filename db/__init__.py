"""
Публичный API слоя SQLite с сохранением старых импортов ``from db import ...``.

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
from .connection import (
    close_db,
    db_healthcheck,
    ensure_db_schema,
    get_connection,
    init_db,
)
from .economy import inv_add, inv_all, inv_remove
from .migrations import DB_SCHEMA_VERSION, MIGRATIONS, SCHEMA
from .moderation import (
    active_mutes,
    add_mute,
    add_note,
    get_notes,
    log_action,
    moder_stats,
    remove_mute,
)
from .quotes import (
    add_quote,
    count_quotes_by_user,
    delete_quote,
    get_quote,
    quotes_by_user,
    random_quote,
)
from .stats import (
    stats_all,
    stats_day,
    stats_hour,
    stats_month,
    stats_week,
    track_message_stat,
)
from .users import (
    ALLOWED_FIELDS,
    all_users,
    count_by,
    create_user,
    ensure_admin,
    find_by_nick,
    find_by_username,
    get_user,
    inc_field,
    log_rep,
    rep_history,
    set_field,
    top_by,
    update_user,
)
__all__ = [
    "ALLOWED_FIELDS",
    "DB_SCHEMA_VERSION",
    "MIGRATIONS",
    "SCHEMA",
    "active_mutes",
    "add_mute",
    "add_note",
    "add_quote",
    "all_users",
    "close_db",
    "count_by",
    "count_quotes_by_user",
    "create_user",
    "db_healthcheck",
    "delete_quote",
    "ensure_admin",
    "ensure_db_schema",
    "find_by_nick",
    "find_by_username",
    "get_connection",
    "get_notes",
    "get_quote",
    "get_user",
    "inc_field",
    "init_db",
    "inv_add",
    "inv_all",
    "inv_remove",
    "log_action",
    "log_rep",
    "moder_stats",
    "quotes_by_user",
    "random_quote",
    "remove_mute",
    "rep_history",
    "set_field",
    "stats_all",
    "stats_day",
    "stats_hour",
    "stats_month",
    "stats_week",
    "top_by",
    "track_message_stat",
    "update_user",
]