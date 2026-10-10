"""
Схема базы данных и применение версионированных миграций.

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
import aiosqlite
DB_SCHEMA_VERSION = 1
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    username    TEXT,
    nick        TEXT,
    custom_nick INTEGER DEFAULT 0,
    rank        INTEGER DEFAULT 0,
    reputation  INTEGER DEFAULT 0,
    varn        INTEGER DEFAULT 0,
    balance     INTEGER DEFAULT 0,
    bank        INTEGER DEFAULT 0,
    last_daily  TEXT,
    last_rob    TEXT,
    daily_streak INTEGER DEFAULT 0,
    last_rep_given_to INTEGER,
    last_rep_time     TEXT,
    joined_at   TEXT DEFAULT CURRENT_TIMESTAMP,
    messages    INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS actions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP,
    chat_id   INTEGER,
    moder_id  INTEGER,
    target_id INTEGER,
    action    TEXT,
    duration  TEXT,
    reason    TEXT
);
CREATE TABLE IF NOT EXISTS mutes (
    target_id INTEGER PRIMARY KEY,
    chat_id   INTEGER,
    until     TEXT,
    reason    TEXT
);
CREATE TABLE IF NOT EXISTS notes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER,
    author_id INTEGER,
    text      TEXT,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS quotes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER,
    text      TEXT,
    saved_by  INTEGER,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS reputation_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP,
    from_id   INTEGER,
    to_id     INTEGER,
    delta     INTEGER
);
CREATE TABLE IF NOT EXISTS warnings_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP,
    moder_id  INTEGER,
    target_id INTEGER,
    delta     INTEGER,
    reason    TEXT
);
CREATE TABLE IF NOT EXISTS achievements (
    user_id  INTEGER,
    code     TEXT,
    ts       TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, code)
);
CREATE TABLE IF NOT EXISTS farms (
    user_id          INTEGER PRIMARY KEY,
    last_fish        TEXT,
    last_hunt        TEXT,
    last_farm        TEXT,
    seeds            INTEGER DEFAULT 0,
    harvest_ready_at TEXT,
    fish_caught      INTEGER DEFAULT 0,
    hunt_kills       INTEGER DEFAULT 0,
    harvest_total    INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS inventory (
    user_id   INTEGER,
    item_code TEXT,
    qty       INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, item_code)
);
CREATE TABLE IF NOT EXISTS roles (
    code     TEXT PRIMARY KEY,
    name     TEXT,
    emoji    TEXT,
    price    INTEGER DEFAULT 0,
    min_rank INTEGER DEFAULT 0,
    enabled  INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS user_roles (
    user_id   INTEGER PRIMARY KEY,
    role_code TEXT,
    until     TEXT
);
CREATE TABLE IF NOT EXISTS message_stats (
    chat_id INTEGER,
    date    TEXT,
    hour    INTEGER,
    count   INTEGER DEFAULT 0,
    PRIMARY KEY (chat_id, date, hour)
);
CREATE TABLE IF NOT EXISTS duels (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id    INTEGER,
    challenger INTEGER,
    opponent   INTEGER,
    bet        INTEGER,
    status     TEXT DEFAULT 'pending',
    winner     INTEGER,
    ts         TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ttt_games (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id  INTEGER,
    player_x INTEGER,
    player_o INTEGER,
    board    TEXT,
    turn     INTEGER,
    status   TEXT DEFAULT 'active',
    ts       TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS clans (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT UNIQUE,
    owner_id   INTEGER,
    balance    INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS clan_members (
    clan_id   INTEGER,
    user_id   INTEGER PRIMARY KEY,
    role      TEXT DEFAULT 'member',
    joined_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS clan_invites (
    clan_id   INTEGER,
    user_id   INTEGER,
    ts        TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (clan_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_stats_chat_date ON message_stats(chat_id, date);
CREATE INDEX IF NOT EXISTS idx_duels_status ON duels(status);
CREATE INDEX IF NOT EXISTS idx_clan_members_clan ON clan_members(clan_id);
CREATE INDEX IF NOT EXISTS idx_users_rank ON users(rank);
CREATE INDEX IF NOT EXISTS idx_users_rep ON users(reputation);
CREATE INDEX IF NOT EXISTS idx_users_nick ON users(nick);
CREATE INDEX IF NOT EXISTS idx_actions_moder ON actions(moder_id);
CREATE INDEX IF NOT EXISTS idx_actions_target ON actions(target_id);
CREATE INDEX IF NOT EXISTS idx_rep_to ON reputation_log(to_id);
"""
MIGRATIONS = {1: SCHEMA}
async def apply_migrations(connection: aiosqlite.Connection) -> int:
    await connection.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "version INTEGER PRIMARY KEY, "
        "applied_at TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    await connection.commit()
    async with connection.execute(
        "SELECT MAX(version) FROM schema_migrations"
    ) as cursor:
        row = await cursor.fetchone()
    legacy_version = int(row[0]) if row and row[0] is not None else 0
    async with connection.execute("PRAGMA user_version") as cursor:
        row = await cursor.fetchone()
    pragma_version = int(row[0]) if row and row[0] is not None else 0
    current_version = max(legacy_version, pragma_version)
    if pragma_version < current_version:
        await connection.execute(f"PRAGMA user_version = {current_version}")
    if legacy_version < current_version:
        await connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
            (current_version,),
        )
    await connection.commit()
    for version in sorted(MIGRATIONS):
        if version <= current_version:
            continue
        await connection.executescript(MIGRATIONS[version])
        await connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
            (version,),
        )
        await connection.execute(f"PRAGMA user_version = {version}")
        await connection.commit()
        current_version = version
    return current_version