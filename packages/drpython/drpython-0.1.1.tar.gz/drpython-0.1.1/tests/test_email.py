from unittest.mock import patch, MagicMock
from drpython.email import notify_email


@patch("smtplib.SMTP")
def test_email(mock_smtp_class):
    mock_smtp = MagicMock()
    mock_smtp_class.return_value = mock_smtp
    assert (
        notify_email(
            to="a@b.c", subject="s", body="b", host="h", user="u", password="p"
        )
        is True
    )
