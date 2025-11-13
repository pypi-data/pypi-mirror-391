import os
from typing import Optional
import requests

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.base_url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def send(self, message: str, parse_mode: Optional[str] = "HTML", disable_notification: bool = False) -> bool:
        params = {"chat_id": self.chat_id, "text": message, "parse_mode": parse_mode or None, "disable_notification": disable_notification}
        try:
            resp = requests.get(self.base_url, params=params, timeout=10)
            return resp.json().get("ok", False)
        except requests.RequestException:
            return False

def notify_telegram(message: str, token: Optional[str] = None, chat_id: Optional[str] = None, **kwargs) -> bool:
    token = token or os.getenv("DRPYTHON_TELEGRAM_TOKEN")
    chat_id = chat_id or os.getenv("DRPYTHON_CHAT_ID")
    if not token or not chat_id:
        raise ValueError("Telegram token and chat_id required.")
    return TelegramNotifier(token, chat_id).send(message, **kwargs)