<div align="center">

# Prizma

**Telegram-бот для чата Prizma**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.31-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-aiosqlite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Модерация, репутация, статистика и развлечения — всё в одном боте.

</div>

---

## О проекте

**Prizma** — Telegram чат бот, написанный специально для чата **Prizma**.

Изначально был переписан с другого бота под названием Iris.

---

## Возможности

### Для пользователей

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие |
| `/help` | Список всех команд |
| `/id` | Узнать ID (свой, по реплаю или `@username`) |
| `/profile` | Профиль пользователя |
| `/me` | Свой профиль |
| `/top` | Топ-10 по репутации |
| `/rep` | +1 репутации (ответом на сообщение) |
| `+ник <ник>` | Установить кастомный ник |
| `-ник` | Сбросить ник |
| `/report` | Жалоба на нарушителя (ответом) |
| `/version` | Версия бота |

### Для модераторов

| Команда | Описание |
|---------|----------|
| `/mute <время> [причина]` | Замутить (ответом или `@user`) |
| `/unmute` | Размутить |
| `/mute_list` | Список активных мутов |
| `/warn [кол-во] [причина]` | Выдать предупреждение |
| `/warn_list` | Список предупреждённых |
| `/kick` | Кикнуть |
| `/ban` | Забанить |
| `/delete` | Удалить сообщение |
| `/note <текст>` | Заметка о юзере |
| `/notes` | Список заметок |

### Для админов

| Команда | Описание |
|---------|----------|
| `/promote <ранг> @user` | Повысить |
| `/demote` | Понизить |
| `/snatvseh` | Снять всех (кроме создателя) |
| `/sozdatel` | Вернуть создателя (только создатель чата) |
| `/get` | Текущие настройки |
| `/set <ключ> <значение>` | Изменить настройку |
| `/admins` | Список админов |

### Развлечения

| Команда | Описание |
|---------|----------|
| `/random <мин> <макс>` | Случайное число |
| `/ping` | Проверка работы |
| `ПИНГ` / `ПИУ` / `КИНГ` / `БОТ` | Пасхалки |

---

## Установка

### Требования

- **Python 3.11+** (не 3.14 — `pydantic-core` не соберётся)
- Linux / macOS / Windows
- Токен бота от [@BotFather](https://t.me/BotFather)

### 1. Клонирование

```bash
git clone https://github.com/your-username/IrisTelegramBot.git
cd IrisTelegramBot
```

### 2. Виртуальное окружение

**Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка `.env`

```bash
cp .env.example .env
nano .env
```

```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
ADMIN_IDS=123456789,987654321
LOG_CHANNEL_ID=-1001234567890
PROXY_URL=
```

В `settings.json` вы можете настроить всё под себя.

### 5. Запуск

```bash
python run.py      # supervisor
python main.py     # напрямую
```

---

## Автоперезапуск (`run.py`)

`run.py` — это supervisor, который:

- запускает `main.py` как подпроцесс;
- перезапускает при падении (любая ошибка, segfault);
- убивает при зависании (если heartbeat старше 90 секунд);
- использует экспоненциальный backoff (5с → 10с → ... → 5мин), чтобы не спамить перезапусками.

### Как это работает

1. `main.py` раз в 10 секунд пишет timestamp в `data/heartbeat.txt`.
2. `run.py` проверяет этот файл раз в 5 секунд.
3. Если файл устарел (>90с) — процесс убивается и запускается заново.
4. Если процесс упал — перезапуск с задержкой.

### Логи

Все логи supervisor — в `data/supervisor.log` и stdout.

---

## Прокси

Если Telegram заблокирован (например, в РФ) — используй прокси.

### 1. Установи зависимость

```bash
pip install aiohttp-socks
```

### 2. Добавь в `.env`

```env
PROXY_URL=socks5://user:pass@host:port
```

### 3. Готово

Бот сам подхватит прокси при запуске. В логе будет:

```
INFO:iris:Использую прокси: host:port
```

### Типы прокси

| Тип | Пример |
|-----|--------|
| SOCKS5 | `socks5://user:pass@1.2.3.4:1080` |
| HTTP | `http://user:pass@1.2.3.4:8080` |
| HTTPS | `https://user:pass@1.2.3.4:8080` |

---

## Тесты (планируется)

```bash
pip install pytest pytest-asyncio
pytest
```

---

## 📊 Роадмап

- [x] Базовая модерация
- [x] Репутация
- [x] Профили
- [x] SQLite
- [x] Автоперезапуск
- [x] Прокси
- [ ] Экономика
- [ ] Уровни / XP
- [ ] Достижения
- [ ] Квесты
- [ ] Inline-режим
- [ ] Webhook
- [ ] Docker
- [ ] CI/CD

---

## Вклад

1. Форкни репозиторий.
2. Создай ветку: `git checkout -b feature/my-feature`.
3. Закоммить: `git commit -m "Add my feature"`.
4. Запушь: `git push origin feature/my-feature`.
5. Открой Pull Request.

---

## Авторы

- **Prizma Team** — идея, тестирование
- **WVCXX** — разработка

<div align="center">

Сделано с ❤️ для Prizma chat

</div>