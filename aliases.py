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
ALIASES: dict[str, list[str]] = {
    #инфо
    "help":         ["помощь", "хелп", "команды", "help"],
    "me":           ["я", "me", "кто я"],
    "profile":      ["профиль", "профайл", "profile"],
    "stats":        ["стата", "статистика", "stats"],
    "id":           ["ид", "айди", "id"],
    "whois":        ["кто это", "инфа", "whois"],
    "ping":         ["пинг", "ping", "жив"],
    "version":      ["версия", "version", "v", "о боте"],
    "rules":        ["правила", "устав", "rules"],
    "links":        ["ссылки", "links"],

    #топы
    "top":          ["топ", "рейтинг", "top"],
    "top_active":   ["топ актив", "болтуны", "top_active"],
    "top_varn":     ["антитоп", "нарушители", "top_varn"],
    "top_balance":  ["топ богатых", "топ бал", "top_balance"],
    "top_level":    ["топ лвл", "топ уровня", "top_level"],

    #репа
    "rep":          ["реп", "плюс", "уважение", "респект", "rep"],

    #модерация
    "mute":         ["мут", "заткнуть", "замолчать", "mute"],
    "unmute":       ["размут", "анмут", "unmute"],
    "warn":         ["варн", "пред", "предупреждение", "warn"],
    "unwarn":       ["снять варн", "unwarn"],
    "kick":         ["кик", "выгнать", "kick"],
    "ban":          ["бан", "забанить", "ban"],
    "delete":       ["удалить", "снести", "убрать", "delete"],
    "report":       ["жалоба", "репорт", "стук", "report"],
    "mod":          ["мод", "панель", "действия", "mod"],

    #админ
    "promote":      ["повысить", "promote"],
    "demote":       ["понизить", "demote"],
    "admins":       ["админы", "кто админ", "admins"],
    "get":          ["настройки", "гет", "get"],
    "set":          ["сет", "set"],

    #экономика
    "balance":      ["бал", "баланс", "б", "кошелёк", "balance"],
    "daily":        ["дейли", "бонус", "ежедневка", "daily"],
    "pay":          ["перевод", "заплатить", "pay"],
    "rob":          ["ограбить", "rob"],
    "bank":         ["банк", "bank"],
    "shop":         ["магазин", "shop"],

    #уровни
    "level":        ["лвл", "уровень", "опыт", "level"],
    "achievements": ["ачивки", "достижения", "медали", "achievements"],

    #развлечения
    "roll":         ["кубик", "дайс", "roll"],
    "coin":         ["монетка", "орёл", "coin"],
    "8ball":        ["шар", "8ball"],
    "choose":       ["выбери", "выбор", "choose"],
    "dice":         ["dice"],
    "slot":         ["слоты", "казино", "slot"],
    "quote":        ["цитата", "ц", "quote"],
    "random":       ["рандом", "случайное", "random"],
    "mystats":      ["моя стата", "моя статистика", "mystats"],
    # редактирование контента
    "greeting":     ["приветствие", "greeting"],
    "rule_add":     ["правило добавить", "rule_add"],
    "rule_del":     ["правило удалить", "rule_del"],
    "rules_reset":  ["правила сбросить", "rules_reset"],
    "link_add":     ["ссылка добавить", "link_add"],
    "link_del":     ["ссылка удалить", "link_del"],
}
_REVERSE: dict[str, str] = {}
for _canon, _list in ALIASES.items():
    for _alias in _list:
        _REVERSE[_alias.lower()] = _canon
def resolve(text: str) -> tuple[str | None, str]:
    if not text:
        return None, ""
    stripped = text.lstrip()
    while stripped and stripped[0] in "!./":
        stripped = stripped[1:]
    stripped = stripped.strip()
    if not stripped:
        return None, ""
    parts = stripped.split(maxsplit=2)
    if len(parts) >= 2:
        two = f"{parts[0]} {parts[1]}".lower()
        if two in _REVERSE:
            canon = _REVERSE[two]
            rest = parts[2] if len(parts) > 2 else ""
            return canon, rest.strip()
    one = parts[0].lower()
    if one in _REVERSE:
        canon = _REVERSE[one]
        rest = " ".join(parts[1:]).strip()
        return canon, rest
    return None, ""