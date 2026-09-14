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
import json
import logging
from pathlib import Path
from config import SETTINGS_FILE
log = logging.getLogger("iris")
SCHEMA = {
    "varnLimit": int,
    "DKpovisit": int,
    "DKvarn": int,
    "DKvarnLimit": int,
    "DKmute": int,
    "DKsnatvseh": int,
    "DKban": int,
    "DKkick": int,
    "DKreport": int,
    "symbolLimit": int,
    "antiflood": dict,
    "antimat": dict,
    "rank1": list,
    "rank2": list,
    "rank3": list,
    "rank4": list,
    "rank5": list,
    "rules": list,
    "links": dict,
    "greeting": str,
}
_cache: dict | None = None
_cache_mtime: float = 0
def validate(data: dict) -> list[str]:
    errors = []
    for key, expected in SCHEMA.items():
        if key not in data:
            errors.append(f"отсутствует ключ '{key}'")
            continue
        if not isinstance(data[key], expected):
            errors.append(
                f"'{key}' должен быть {expected.__name__}, "
                f"а получен {type(data[key]).__name__}"
            )
    for rank in ("rank1", "rank2", "rank3", "rank4", "rank5"):
        val = data.get(rank)
        if isinstance(val, list) and len(val) != 5:
            errors.append(f"'{rank}' должен содержать 5 форм, а не {len(val)}")
    af = data.get("antiflood")
    if isinstance(af, dict):
        for k in ("enabled", "messages", "seconds", "mute_minutes"):
            if k not in af:
                errors.append(f"antiflood.{k} отсутствует")
    am = data.get("antimat")
    if isinstance(am, dict):
        for k in ("enabled", "words", "action"):
            if k not in am:
                errors.append(f"antimat.{k} отсутствует")
    return errors
def load_settings(force: bool = False) -> dict:
    global _cache, _cache_mtime
    path = Path(SETTINGS_FILE)
    if not path.exists():
        raise FileNotFoundError(f"{SETTINGS_FILE} не найден")
    mtime = path.stat().st_mtime
    if _cache is not None and not force and mtime == _cache_mtime:
        return _cache
    with open(SETTINGS_FILE, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"{SETTINGS_FILE}: ошибка JSON — {e.msg} "
                f"(строка {e.lineno}, колонка {e.colno})"
            ) from e
    errors = validate(data)
    if errors:
        raise RuntimeError(
            f"{SETTINGS_FILE}: ошибки валидации:\n  - " + "\n  - ".join(errors)
        )
    _cache = data
    _cache_mtime = mtime
    log.info(f"{SETTINGS_FILE} загружен ({len(data)} ключей)")
    return data
def save_settings(data: dict):
    global _cache, _cache_mtime
    errors = validate(data)
    if errors:
        raise ValueError(
            "нельзя сохранить некорректные настройки:\n  - " + "\n  - ".join(errors)
        )
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    _cache = data
    _cache_mtime = Path(SETTINGS_FILE).stat().st_mtime
def reload_settings() -> dict:
    return load_settings(force=True)