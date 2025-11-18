from drpython.telegram import notify_telegram
import os
from dotenv import load_dotenv

load_dotenv()


token = os.getenv("DRPYTHON_TELEGRAM_TOKEN")
chat_id = os.getenv("DRPYTHON_CHAT_ID")
print(token, chat_id)
success = notify_telegram(
    message="Test from Dr. Python – it works!",
    token=token,  # ← real token
    chat_id=chat_id,  # ← real chat id
    parse_mode="HTML",
    disable_notification=False,
)

print("Sent!" if success else "Failed")
