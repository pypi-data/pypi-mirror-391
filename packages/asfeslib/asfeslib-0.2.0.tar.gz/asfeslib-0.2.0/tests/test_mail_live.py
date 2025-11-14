import os
import pytest
from asfeslib.net.mail import MailClient, MailConfig, MailMessage

SMTP_KEY_ENV = "ASFESLIB_SMTP_PASSWORD"
SMTP_USER_ENV = "ASFESLIB_SMTP_USER"

pytestmark = pytest.mark.live


@pytest.mark.asyncio
async def test_live_mail_send():
    user = os.getenv(SMTP_USER_ENV)
    password = os.getenv(SMTP_KEY_ENV)

    if not user or not password:
        pytest.skip("Нет ASFESLIB_SMTP_USER / ASFESLIB_SMTP_PASSWORD")

    cfg = MailConfig(username=user, password=password, port=465,use_tls=True)

    msg = MailMessage(
        to=[user],
        subject="ASFESLIB Live SMTP Test",
        body="Если ты получил это письмо — SMTP работает!",
        html=False
    )

    async with MailClient(cfg) as mail:
        ok = await mail.send(msg)

    assert ok is True
