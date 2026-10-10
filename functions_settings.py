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
import os
import tempfile
from pathlib import Path
from typing import Any
from config import SETTINGS_FILE
log = logging.getLogger("iris")
DEFAULT_SETTINGS = {
    "varnLimit": 10,
    "DKpovisit": 4,
    "DKvarn": 1,
    "DKvarnLimit": 4,
    "DKmute": 3,
    "DKsnatvseh": 5,
    "DKban": 4,
    "DKkick": 3,
    "DKreport": 0,
    "symbolLimit": 32,
    "autodelete_service": 5,
    "antiflood": {
        "enabled": True,
        "messages": 5,
        "seconds": 10,
        "mute_minutes": 10,
    },
    "antimat": {
        "enabled": False,
        "words": ["слово1", "слово2"],
        "action": "warn",
    },
    "rank1": ["Младший Модератор", "Младшего Модератора", "Младшему Модератору", "Младшим Модератором", "Младшие Модераторы"],
    "rank2": ["Старший Модератор", "Старшего Модератора", "Старшему Модератору", "Старшим Модератором", "Старшие Модераторы"],
    "rank3": ["Младший Админ", "Младшего Админа", "Младшему Админу", "Младшим Админом", "Младшие Админы"],
    "rank4": ["Старший Админ", "Старшего Админа", "Старшему Админу", "Старшим Админом", "Старшие Админы"],
    "rank5": ["Создатель", "Создателя", "Создателю", "Создателем", "Создатели"],
    "rules": [
        "Уважай других участников.",
        "Не спамь и не флуди.",
        "Реклама — только с разрешения админов.",
        "Общение по теме чата.",
        "Слушай модераторов.",
    ],
    "links": {"Сайт": "https://example.com", "Канал": "https://t.me/example"},
    "greeting": "добро пожаловать на сервер безумные зомби",
}
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
    "autodelete_service": int,
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
_cache_mtime_ns: int | None = None
def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=4, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
def ensure_default_settings(path: str | Path = SETTINGS_FILE) -> dict:
    settings_path = Path(path)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    if not settings_path.exists():
        _atomic_write_json(settings_path, DEFAULT_SETTINGS)
        return json.loads(json.dumps(DEFAULT_SETTINGS))
    try:
        with settings_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        backup_path = settings_path.with_suffix(f"{settings_path.suffix}.bak")
        if settings_path.exists():
            backup_path.write_bytes(settings_path.read_bytes())
        _atomic_write_json(settings_path, DEFAULT_SETTINGS)
        return json.loads(json.dumps(DEFAULT_SETTINGS))
    if not isinstance(data, dict):
        raise RuntimeError(f"{settings_path}: JSON должен содержать объект")
    merged = json.loads(json.dumps(DEFAULT_SETTINGS))
    merged.update(data)
    return merged
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
    delete_delay = data.get("autodelete_service")
    if isinstance(delete_delay, bool):
        errors.append("'autodelete_service' должен быть целым числом")
    elif isinstance(delete_delay, int):
        if delete_delay < 0:
            errors.append("'autodelete_service' не может быть отрицательным")
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
    global _cache, _cache_mtime_ns
    path = Path(SETTINGS_FILE)
    ensure_default_settings(path)
    mtime_ns = path.stat().st_mtime_ns
    if _cache is not None and not force and mtime_ns == _cache_mtime_ns:
        return _cache
    with path.open(encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"{SETTINGS_FILE}: ошибка JSON — {e.msg} "
                f"(строка {e.lineno}, колонка {e.colno})"
            ) from e
    merged = json.loads(json.dumps(DEFAULT_SETTINGS))
    merged.update(data)
    errors = validate(merged)
    if errors:
        raise RuntimeError(
            f"{SETTINGS_FILE}: ошибки валидации:\n  - " + "\n  - ".join(errors)
        )
    _cache = merged
    _cache_mtime_ns = mtime_ns
    log.info(f"{SETTINGS_FILE} загружен ({len(merged)} ключей)")
    return merged
def save_settings(data: dict):
    global _cache, _cache_mtime_ns
    errors = validate(data)
    if errors:
        raise ValueError(
            "нельзя сохранить некорректные настройки:\n  - " + "\n  - ".join(errors)
        )
    path = Path(SETTINGS_FILE)
    _atomic_write_json(path, data)
    _cache = data
    _cache_mtime_ns = path.stat().st_mtime_ns
def reload_settings() -> dict:
    return load_settings(force=True)