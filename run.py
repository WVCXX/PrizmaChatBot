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
import subprocess
import sys
import time
import logging
from pathlib import Path
import os
HEARTBEAT_FILE = Path("data/heartbeat.txt")
HEARTBEAT_TIMEOUT = 90
CHECK_INTERVAL = 5
os.makedirs("data", exist_ok=True)
LOG_FILE = "data/Prizma_chat_bot.log"
RESTART_DELAY = 5
MAX_RESTART_DELAY = 300  
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("supervisor")
BASE_DIR = Path(__file__).parent.resolve()
def run_bot():
    proc = subprocess.Popen(
        [sys.executable, "-u", str(BASE_DIR / "main.py")],
        cwd=str(BASE_DIR),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    try:
        while True:
            try:
                proc.wait(timeout=CHECK_INTERVAL)
                return proc.returncode
            except subprocess.TimeoutExpired:
                pass
            if HEARTBEAT_FILE.exists():
                try:
                    last = float(HEARTBEAT_FILE.read_text(encoding="utf-8"))
                except Exception:
                    last = 0
                if time.time() - last > HEARTBEAT_TIMEOUT:
                    log.warning(
                        f"heartbeat устарел (>{HEARTBEAT_TIMEOUT}с), убиваю процесс"
                    )
                    proc.kill()
                    return -1
    except KeyboardInterrupt:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        raise
def main():
    delay = RESTART_DELAY
    while True:
        start = time.time()
        try:
            code = run_bot()
        except KeyboardInterrupt:
            log.info("Выход по Ctrl+C")
            break
        uptime = time.time() - start
        log.warning(f"бот упал (код {code}) через {uptime:.1f}с. "
                    f"перезапуск через {delay}с")
        time.sleep(delay)
        if uptime < 60:
            delay = min(delay * 2, MAX_RESTART_DELAY)
        else:
            delay = RESTART_DELAY
if __name__ == "__main__":
    main()