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
import os
from pathlib import Path
HEARTBEAT_FILE = Path("data/heartbeat.txt")
LOCK_FILE = Path("data/supervisor.lock")
HEARTBEAT_TIMEOUT = 90
CHECK_INTERVAL = 5
os.makedirs("data", exist_ok=True)
LOG_FILE = "data/Prizma_chat_bot.log"
RESTART_DELAY = 5
MAX_RESTART_DELAY = 300
def _read_lock_pid(lock_path: Path) -> int | None:
    try:
        text = lock_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None
def _pid_is_alive(pid: int | None) -> bool:
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
def acquire_supervisor_lock():
    while True:
        try:
            fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
            return
        except FileExistsError:
            pid = _read_lock_pid(LOCK_FILE)
            if _pid_is_alive(pid):
                raise RuntimeError(f"supervisor уже запущен (pid {pid})")
            try:
                LOCK_FILE.unlink(missing_ok=True)
            except OSError:
                pass
def release_supervisor_lock():
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass
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
    HEARTBEAT_FILE.unlink(missing_ok=True)
    while True:
        HEARTBEAT_FILE.unlink(missing_ok=True)
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
    try:
        acquire_supervisor_lock()
        main()
    except KeyboardInterrupt:
        log.info("Выход по Ctrl+C")
    except RuntimeError as exc:
        log.warning(str(exc))
    finally:
        release_supervisor_lock()