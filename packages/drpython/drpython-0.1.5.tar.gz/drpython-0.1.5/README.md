# drpython

Modular notifications for Python projects: simple helpers for Telegram bots and SMTP email.

This library provides two small utilities:
- `drpython.telegram`: send messages via a Telegram bot.
- `drpython.email`: send emails via an SMTP server.

Both modules expose a light class (`TelegramNotifier`, `EmailNotifier`) and a convenience function (`notify_telegram`, `notify_email`).

## Installation

- Using uv (recommended for projects):

  ```powershell
  uv add drpython
  ```

- Using pip:

  ```powershell
  pip install drpython
  ```

## Quickstart

You can pass credentials directly to the functions/classes, or supply them via environment variables. If you keep secrets in a `.env` file, load it with `python-dotenv` before calling the notifiers.

```python
from dotenv import load_dotenv
load_dotenv()  # Only needed if using a .env file
```

### Telegram

Environment variables used:
- `DRPYTHON_TELEGRAM_TOKEN`
- `DRPYTHON_CHAT_ID`

Send a Telegram message using environment variables:

```python
from drpython.telegram import notify_telegram

ok = notify_telegram("Hello from drpython!", parse_mode="HTML")
print(ok)  # True if sent
```

Or pass credentials explicitly:

```python
from drpython.telegram import TelegramNotifier

bot = TelegramNotifier(token="<BOT_TOKEN>", chat_id="<CHAT_ID>")
ok = bot.send("<b>Bold</b> and <i>italic</i>", parse_mode="HTML", disable_notification=False)
print(ok)
```

### Email (SMTP)

Environment variables used:
- `DRPYTHON_SMTP_HOST` (e.g., `smtp.gmail.com`)
- `DRPYTHON_SMTP_PORT` (default `587`)
- `DRPYTHON_SMTP_USER`
- `DRPYTHON_SMTP_PASSWORD`
- `DRPYTHON_SMTP_FROM` (defaults to user)

Send an email using environment variables:

```python
from drpython.email import notify_email

ok = notify_email(
    to="recipient@example.com",
    subject="Greetings",
    body="Hello from drpython!",
    html=False,  # set True to send HTML
)
print(ok)
```

Or pass credentials explicitly and use the class:

```python
from drpython.email import EmailNotifier

mailer = EmailNotifier(
    host="smtp.example.com",
    port=587,
    user="user@example.com",
    password="app_password",
    from_addr="user@example.com",
)

ok = mailer.send(
    to=["recipient@example.com", "other@example.com"],
    subject="Attachments and HTML",
    body="<b>Hello</b> world",
    html=True,
    cc="cc@example.com",
    bcc=["bcc1@example.com", "bcc2@example.com"],
    attachments=["path/to/file.pdf"],
)
print(ok)
```

## Using `.env`

If you prefer a `.env` file, create it and load it in your app:

```env
# Telegram
DRPYTHON_TELEGRAM_TOKEN=your-bot-token
DRPYTHON_CHAT_ID=your-chat-id

# SMTP
DRPYTHON_SMTP_HOST=smtp.example.com
DRPYTHON_SMTP_PORT=587
DRPYTHON_SMTP_USER=user@example.com
DRPYTHON_SMTP_PASSWORD=app_password
DRPYTHON_SMTP_FROM=user@example.com
```

Then load it:

```python
from dotenv import load_dotenv
load_dotenv()
```

Never commit real tokens or passwords to source control.

## Notes

- Commands above are shown for Windows PowerShell.
- `notify_telegram` uses `requests.get` and returns `True/False` based on Telegram API response.
- `notify_email` uses `smtplib.SMTP` and returns `True/False` based on send success.
- If you encounter build/publish issues, ensure your `pyproject.toml` includes a `src/drpython` wheel target and excludes `.env` from distributions.