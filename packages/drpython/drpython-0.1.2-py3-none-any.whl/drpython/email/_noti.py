import os, smtplib
from email.message import EmailMessage
from typing import List, Optional


class EmailNotifier:
    def __init__(
        self,
        host: str,
        port: int = 587,
        user: Optional[str] = None,
        password: Optional[str] = None,
        from_addr: Optional[str] = None,
        use_tls: bool = True,
    ):
        self.host, self.port, self.user, self.password, self.from_addr, self.use_tls = (
            host,
            port,
            user,
            password,
            from_addr or user,
            use_tls,
        )

    def _connect(self):
        s = smtplib.SMTP(self.host, self.port, timeout=10)
        if self.use_tls:
            s.starttls()
        if self.user and self.password:
            s.login(self.user, self.password)
        return s

    def send(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        *,
        html: bool = False,
        cc=None,
        bcc=None,
        attachments=None,
    ) -> bool:
        msg = EmailMessage()
        msg["From"], msg["Subject"] = self.from_addr, subject
        to_list = [to] if isinstance(to, str) else to
        msg["To"] = ", ".join(to_list)
        if cc:
            msg["Cc"] = ", ".join([cc] if isinstance(cc, str) else cc)
        if bcc:
            msg["Bcc"] = ", ".join([bcc] if isinstance(bcc, str) else bcc)
        if html:
            msg.set_content(body, subtype="html")
            msg.add_alternative(
                body.replace("<b>", "**")
                .replace("</b>", "**")
                .replace("<i>", "_")
                .replace("</i>", "_"),
                subtype="plain",
            )
        else:
            msg.set_content(body)
        if attachments:
            import mimetypes

            for p in attachments:
                ctype = mimetypes.guess_type(p)[0] or "application/octet-stream"
                main, sub = ctype.split("/")
                with open(p, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype=main,
                        subtype=sub,
                        filename=os.path.basename(p),
                    )
        try:
            self._connect().send_message(msg).quit()
            return True
        except:
            return False


def notify_email(
    to,
    subject,
    body,
    *,
    host=None,
    port=None,
    user=None,
    password=None,
    from_addr=None,
    html=False,
    **kw,
):
    host = host or os.getenv("DRPYTHON_SMTP_HOST")
    port = int(port or os.getenv("DRPYTHON_SMTP_PORT", "587"))
    user = user or os.getenv("DRPYTHON_SMTP_USER")
    password = password or os.getenv("DRPYTHON_SMTP_PASSWORD")
    from_addr = from_addr or os.getenv("DRPYTHON_SMTP_FROM") or user
    if not all([host, user, password]):
        raise ValueError("SMTP credentials required.")
    return EmailNotifier(host, port, user, password, from_addr).send(
        to, subject, body, html=html, **kw
    )
