import os
from typing import Optional
import requests

class TelegramNotifier:
    """
    A simple helper to send messages to a Telegram chat via the Bot API.
    """

    def __init__(self, token: str, chat_id: str):
        """
        Initialize the notifier with a bot token and target chat identifier.

        Args:
            token: The Telegram bot token obtained from @BotFather.
            chat_id: The chat ID (user or group) that will receive messages.
        """
        self.base_url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def send(self, message: str, parse_mode: Optional[str] = "HTML", disable_notification: bool = False) -> bool:
        """
        Send a text message to the configured chat.

        Args:
            message: The text content to deliver.
            parse_mode: Telegram parse mode ("HTML", "Markdown", etc.). Defaults to "HTML".
            disable_notification: If True, the recipient receives the message silently.

        Returns:
            True if Telegram confirms the message was sent successfully, otherwise False.
        """
        params = {"chat_id": self.chat_id, "text": message, "parse_mode": parse_mode or None, "disable_notification": disable_notification}
        try:
            resp = requests.get(self.base_url, params=params, timeout=10)
            return resp.json().get("ok", False)
        except requests.RequestException:
            return False


def notify_telegram(message: str, token: Optional[str] = None, chat_id: Optional[str] = None, **kwargs) -> bool:
    """
    Convenience wrapper that creates a TelegramNotifier and sends a message.

    Environment variables DRPYTHON_TELEGRAM_TOKEN and DRPYTHON_CHAT_ID are
    used as fallbacks when token or chat_id are not provided explicitly.

    Args:
        message: The text to send.
        token: Telegram bot token. Falls back to DRPYTHON_TELEGRAM_TOKEN env var.
        chat_id: Target chat ID. Falls back to DRPYTHON_CHAT_ID env var.
        **kwargs: Additional options passed to TelegramNotifier.send().

    Returns:
        True on successful delivery, False otherwise.

    Raises:
        ValueError: If both token and chat_id cannot be determined.
    """
    token = token or os.getenv("DRPYTHON_TELEGRAM_TOKEN")
    chat_id = chat_id or os.getenv("DRPYTHON_CHAT_ID")
    if not token or not chat_id:
        raise ValueError("Telegram token and chat_id required.")
    return TelegramNotifier(token, chat_id).send(message, **kwargs)