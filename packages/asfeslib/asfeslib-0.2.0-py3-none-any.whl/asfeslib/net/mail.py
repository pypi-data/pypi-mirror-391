import asyncio
import smtplib
import ssl
import mimetypes
from email.message import EmailMessage
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr
from asfeslib.core.logger import Logger

logger = Logger(name=__name__)


# -------------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------------

class MailAttachment(BaseModel):
    filename: str
    content: bytes
    mime_type: Optional[str] = None


class MailMessage(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    html: bool = False
    attachments: List[MailAttachment] = Field(default_factory=list)


class MailConfig(BaseModel):
    host: str = "mail.asfes.ru"
    port: int = 465               # SSL порт
    username: str
    password: str

    from_name: str = "ASFES Mailer"

    timeout: int = 10
    retry_count: int = 3
    retry_delay: float = 1.0
    rate_limit: float = 0.0       # пауза между письмами


# -------------------------------------------------------------------
# MailClient — SMTP SSL per email + async wrapper
# -------------------------------------------------------------------

class MailClient:
    """
    Асинхронный SMTP-клиент ASFESLIB через smtplib.SMTP_SSL.

    Причины реализации:
    - aiosmtplib несовместим с mail.asfes.ru (AUTH LOGIN → 535)
    - smtplib работает идеально, но синхронный
    - asyncio.to_thread позволяет использовать его асинхронно

    Важное:
    КАЖДОЕ письмо создаёт новое SSL соединение SMTP.
    Это гарантирует корректный AUTH LOGIN.
    """

    def __init__(self, cfg: MailConfig):
        self.cfg = cfg
        self._rate_lock = asyncio.Lock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    # ------------------------------------------------------------
    # Rate Limit
    # ------------------------------------------------------------

    async def _rate_limit(self):
        if self.cfg.rate_limit > 0:
            async with self._rate_lock:
                await asyncio.sleep(self.cfg.rate_limit)

    # ------------------------------------------------------------
    # Email builder
    # ------------------------------------------------------------

    def _build_email(self, msg: MailMessage) -> EmailMessage:
        email = EmailMessage()
        email["From"] = f"{self.cfg.from_name} <{self.cfg.username}>"
        email["To"] = ", ".join(msg.to)
        email["Subject"] = msg.subject

        if msg.html:
            email.set_content(msg.body, subtype="html")
        else:
            email.set_content(msg.body)

        for att in msg.attachments:
            mime = att.mime_type or mimetypes.guess_type(att.filename)[0] or "application/octet-stream"
            main_type, sub_type = mime.split("/", 1)
            email.add_attachment(att.content, maintype=main_type, subtype=sub_type, filename=att.filename)

        return email

    # ------------------------------------------------------------
    # AUTH LOGIN normalization
    # ------------------------------------------------------------

    def _normalize_login(self, username: str, password: str):
        """
        smtplib.SMTP_SSL expects `str` credentials.
        They must be ASCII-compatible, but provided as Python str.

        Поэтому:
        - гарантируем str
        - НЕ конвертируем в bytes
        - доверяем smtplib.base64_encode
        """
        return str(username), str(password)


    # ------------------------------------------------------------
    # Main send (new SMTP_SSL per email)
    # ------------------------------------------------------------

    async def send(self, msg: MailMessage) -> bool:
        await self._rate_limit()

        email = self._build_email(msg)

        for attempt in range(1, self.cfg.retry_count + 1):
            try:

                def blocking():
                    context = ssl.create_default_context()

                    smtp = smtplib.SMTP_SSL(
                        self.cfg.host,
                        self.cfg.port,
                        timeout=self.cfg.timeout,
                        context=context
                    )

                    # Нормализуем логин
                    username, password = self._normalize_login(
                        self.cfg.username,
                        self.cfg.password
                    )

                    smtp.login(username, password)
                    smtp.send_message(email)
                    smtp.quit()

                await asyncio.to_thread(blocking)
                logger.info(f"Email sent → {msg.to}")
                return True

            except Exception as e:
                logger.error(f"SMTP error on attempt {attempt}: {e}")

                if attempt < self.cfg.retry_count:
                    await asyncio.sleep(self.cfg.retry_delay)

        logger.error(f"Failed to send email after {self.cfg.retry_count} attempts")
        return False

    # ------------------------------------------------------------
    # Bulk
    # ------------------------------------------------------------

    async def send_bulk(self, messages: List[MailMessage]) -> List[bool]:
        results = []
        for msg in messages:
            results.append(await self.send(msg))
        return results


# -------------------------------------------------------------------
# Backward-compatibility wrapper
# -------------------------------------------------------------------

async def send_mail(cfg: MailConfig, msg: MailMessage) -> bool:
    async with MailClient(cfg) as client:
        return await client.send(msg)
