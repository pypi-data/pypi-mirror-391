import requests, threading, time
from .context import Message

class Bot:
    def __init__(self, token, polling_interval=2.0):
        self.token = token
        self.base_url = "https://botapi.rubika.ir/v3"
        self.polling_interval = polling_interval
        self._on_start = None
        self._running = False

    def on_start(self, func):
        self._on_start = func
        return func

    def _call(self, method, data=None):
        url = f"{self.base_url}/{self.token}/{method}"
        r = requests.post(url, json=data or {}, timeout=15)
        r.raise_for_status()
        return r.json()

    def send_message(self, chat_id, text):
        return self._call("sendMessage", {"chat_id": chat_id, "text": text})

    def get_updates(self, offset=None):
        data = {"limit": 10}
        if offset:
            data["offset"] = offset
        return self._call("getUpdates", data)

    def _dispatch(self, update):
        msg = update.get("message")
        if not msg:
            return
        text = msg.get("text", "")
        chat_id = msg["chat"]["chat_id"]
        message_id = msg["message_id"]
        sender_id = msg["author_object_guid"]
        message = Message(self, chat_id, message_id, sender_id, text)

        if text.startswith("/start") and self._on_start:
            self._on_start(self, message)

    def run_polling(self):
        offset = None
        self._running = True
        print("✅ Bot started (polling)...")
        while self._running:
            try:
                updates = self.get_updates(offset)
                for upd in updates.get("data", []):
                    offset = upd.get("update_id")
                    self._dispatch(upd)
            except Exception as e:
                print("polling error:", e)
            time.sleep(self.polling_interval)
