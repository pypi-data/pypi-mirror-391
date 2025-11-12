# الملف: inspeakbot/__init__.py

import time
import requests
from datetime import datetime

class InSpeakBot:
    """
    فئة البوت الأساسية للتفاعل مع InSpeak API،
    تم تحديثها لدعم واجهة @bot.command("/command") و bot.run().
    """
    def __init__(self, token, base_url="https://inspeak.levelupstudios.xyz", bot_id=1):
        self.BOT_TOKEN = token
        self.BASE_URL = base_url
        self.BOT_ID = bot_id
        self.last_message_id = 0
        self.commands = {}
        self.general_message_handlers = []

    # ----------------------------------------
    # وظائف API (لا تغيير)
    # ----------------------------------------
    def send_message(self, target_id, message, is_group=0):
        """إرسال رسالة إلى معرّف هدف محدد (target_id)."""
        try:
            url = f"{self.BASE_URL}/send_message.php"
            headers = {
                "Authorization": f"Bearer {self.BOT_TOKEN}",
                "Content-Type": "application/json"
            }
            json_data = {
                "target_id": target_id,
                "message": message,
                "is_group": is_group
            }
            res = requests.post(url, headers=headers, json=json_data, timeout=10)
            res.raise_for_status() 
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ أثناء الإرسال: {e}")

    def _get_updates(self):
        """جلب الرسائل الجديدة من API."""
        try:
            url = f"{self.BASE_URL}/bot_get_updates.php"
            response = requests.post(url, json={"token": self.BOT_TOKEN}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("ok") and "messages" in data:
                return data["messages"]
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في جلب التحديثات: {e}")
            return []

    # ----------------------------------------
    # المجمِّل الجديد (Decorator): @bot.command()
    # ----------------------------------------
    def command(self, command_str):
        """
        مجمِّل لتسجيل دوال معالجة أمر محدد. 
        يأخذ الأمر كاملاً مثل "/start".
        """
        def decorator(handler_func):
            # نزيل علامة / ونخزن الأمر كـ key
            command_name = command_str.strip().lower().lstrip('/')
            self.commands[command_name] = handler_func
            return handler_func
        return decorator
        
    # ----------------------------------------
    # حلقة التشغيل الرئيسية: run()
    # ----------------------------------------
    def run(self, interval=5):
        """
        تبدأ حلقة الاستماع (Polling) اللانهائية للرسائل الجديدة.
        """
        print(f"🚀 البوت قيد التشغيل (Polling) كل {interval} ثوانٍ...")
        while True:
            try:
                messages = self._get_updates()

                for msg in messages:
                    msg_id = msg.get("id", 0)
                    sender = msg.get("sender_id")
                    text = msg.get("message", "")
                    
                    if msg_id > self.last_message_id:
                        self.last_message_id = msg_id
                        if sender == self.BOT_ID:
                            continue

                        print(f"📩 رسالة جديدة من المستخدم ({sender}): {text}")
                        reply = self._process_message(sender, text)
                        
                        if reply:
                            self.send_message(sender, reply)

                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ خطأ في الحلقة الرئيسية: {e}")
                time.sleep(interval)

    # ----------------------------------------
    # منطق معالجة الرسالة (تأكد من قراءة الأمر بدون /)
    # ----------------------------------------
    def _process_message(self, sender, text):
        """منطق معالجة الرسالة: تحديد هل هي أمر أم نص عادي."""
        text_lower = text.strip().lower()
        
        # 1. التحقق من الأوامر
        if text_lower.startswith("/"):
            # يستخرج الأمر بدون / (مثل "start" من "/start hello")
            command = text_lower[1:].split()[0]
            
            if command in self.commands:
                # يستدعي الدالة المخزنة في @bot.command()
                return self.commands[command](sender)
        
        # 2. التحقق من معالجات الرسائل العامة (إذا أردت إضافتها لاحقاً)
        for handler in self.general_message_handlers:
            reply = handler(sender, text)
            if reply:
                return reply
        
        # 3. الرد الافتراضي
        return f"🤖 لم أفهم الأمر '{text}'. اكتب /help لعرض الأوامر المتاحة."