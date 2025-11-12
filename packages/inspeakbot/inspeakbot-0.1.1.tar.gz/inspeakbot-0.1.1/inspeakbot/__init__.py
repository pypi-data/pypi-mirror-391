# inspeakbot/__init__.py
import time
import requests
import threading
import os
import mysql.connector
from datetime import datetime
from typing import Callable, Any, Optional

DEFAULT_BASE_URL = "https://inspeak.levelupstudios.xyz"

# =============================================
# 🗄️ MySQL State Storage
# =============================================
class MySQLStateStorage:
    def __init__(self, host="localhost", user="root", password="", database="inspeakbot"):
        self.conn = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self._lock = threading.RLock()
        self._init_table()

    def _init_table(self):
        with self._lock:
            cur = self.conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bot_state (
                    token VARCHAR(255) PRIMARY KEY,
                    last_message_id BIGINT DEFAULT 0,
                    updated_at DATETIME
                )
            """)
            self.conn.commit()

    def get_last_message_id(self, token: str) -> int:
        with self._lock:
            cur = self.conn.cursor()
            cur.execute("SELECT last_message_id FROM bot_state WHERE token = %s", (token,))
            row = cur.fetchone()
            return int(row[0]) if row and row[0] is not None else 0

    def set_last_message_id(self, token: str, last_id: int):
        with self._lock:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO bot_state (token, last_message_id, updated_at)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    last_message_id = VALUES(last_message_id),
                    updated_at = VALUES(updated_at)
            """, (token, int(last_id), datetime.utcnow()))
            self.conn.commit()

# =============================================
# 🤖 InSpeakBot Core
# =============================================
class InSpeakBot:
    def __init__(self, token: str,
                 base_url: str = DEFAULT_BASE_URL,
                 db_config: dict = None,
                 long_poll_timeout: int = 25):
        self.BOT_TOKEN = token
        self.BASE_URL = base_url.rstrip('/')
        self.commands = {}
        self.message_handlers = []
        self._running = False

        self._session = requests.Session()
        self._send_lock = threading.RLock()

        # Database config (MySQL)
        self.db_conf = db_config or {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "inspeakbot"
        }
        self._storage = MySQLStateStorage(**self.db_conf)

        # Load last processed message
        self.last_message_id = self._storage.get_last_message_id(self.BOT_TOKEN)

        # Polling behavior
        self.long_poll_timeout = int(long_poll_timeout)
        self.BOT_ID = None

        print(f"ℹ️ InSpeakBot started — token hash: {hash(token)%9999} — last_id={self.last_message_id}")

    # =============================================
    #  🧩 Decorators
    # =============================================
    def command(self, command_str: str):
        cmd = command_str.strip().lower().lstrip('/')
        def decorator(func):
            self.commands[cmd] = func
            return func
        return decorator

    def message_handler(self, func: Callable):
        self.message_handlers.append(func)
        return func

    # =============================================
    #  💬 Send Message
    # =============================================
    def send_message(self, target_id: int, message: str, is_group: int = 0):
        url = f"{self.BASE_URL}/send_message.php"
        headers = {
            "Authorization": f"Bearer {self.BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        json_data = {"target_id": target_id, "message": message, "is_group": is_group}
        try:
            with self._send_lock:
                r = self._session.post(url, headers=headers, json=json_data, timeout=10)
            j = r.json()
            print(f"📤 [SEND] -> {target_id}: {message!r}")
            return j
        except Exception as e:
            print(f"❌ [SEND ERROR]: {e}")
            return None

    # =============================================
    #  🔍 Get Bot Info (to fetch BOT_ID)
    # =============================================
    def _fetch_bot_info(self):
        url = f"{self.BASE_URL}/bot_get_info.php"
        try:
            r = self._session.post(url, json={"token": self.BOT_TOKEN}, timeout=10)
            data = r.json()
            if data.get("ok"):
                self.BOT_ID = int(data["bot"]["id"])
                print(f"✅ Bot ID = {self.BOT_ID}")
            else:
                print(f"⚠️ Failed to fetch bot info: {data}")
        except Exception as e:
            print(f"❌ BOT INFO ERROR: {e}")

    # =============================================
    #  📨 Get Updates (Long Poll)
    # =============================================
    def _get_updates(self):
        url = f"{self.BASE_URL}/bot_get_updates.php"
        payload = {"token": self.BOT_TOKEN}
        try:
            r = self._session.post(url, json=payload, timeout=self.long_poll_timeout + 5)
            data = r.json()
            if data.get("ok") and "messages" in data:
                return data["messages"]
        except Exception as e:
            print(f"❌ [UPDATES ERROR]: {e}")
        return []

    # =============================================
    #  🧠 Message Processing
    # =============================================
    def _process_message(self, msg: dict):
        msg_id = int(msg.get("id", 0))
        sender = msg.get("sender_id")
        text = (msg.get("message") or "").strip()

        if not text:
            return None

        if text.startswith("/"):
            cmd = text[1:].split()[0].lower()
            func = self.commands.get(cmd)
            if func:
                try:
                    return func(sender, text)
                except TypeError:
                    return func(sender)

        for handler in self.message_handlers:
            try:
                return handler(sender, text)
            except TypeError:
                return handler(sender)
        return None

    # =============================================
    #  🔁 Run Loop
    # =============================================
    def run(self):
        self._fetch_bot_info()
        print(f"🚀 Running InSpeakBot (long-poll={self.long_poll_timeout}s)...")

        self._running = True
        while self._running:
            messages = self._get_updates()

            for msg in messages:
                msg_id = int(msg.get("id", 0))
                if msg_id <= self.last_message_id:
                    continue  # skip old messages

                sender = msg.get("sender_id")
                if sender == self.BOT_ID:
                    continue

                print(f"📩 Received ({msg_id}) from {sender}: {msg.get('message')!r}")

                self.last_message_id = msg_id
                self._storage.set_last_message_id(self.BOT_TOKEN, msg_id)

                reply = self._process_message(msg)
                if reply:
                    if isinstance(reply, tuple) and len(reply) == 2:
                        text, delay = reply
                        threading.Timer(float(delay), self.send_message, args=(sender, text)).start()
                        print(f"⏳ Scheduled reply to {sender} in {delay}s")
                    else:
                        self.send_message(sender, reply)
        print("🛑 Bot stopped.")

    def stop(self):
        self._running = False
