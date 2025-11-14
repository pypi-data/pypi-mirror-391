import pytest
from asfeslib.net.mail import MailConfig, MailMessage, send_mail


@pytest.mark.asyncio
async def test_mail_model_creation():
    cfg = MailConfig(username="noreply@asfes.ru", password="secret")
    msg = MailMessage(to=["user@asfes.ru"], subject="Test", body="Hello!")
    assert msg.to[0].endswith("@asfes.ru")
    assert cfg.from_name == "ASFES Mailer"
