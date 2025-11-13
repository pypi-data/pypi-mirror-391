from unittest.mock import patch
from drpython.telegram import notify_telegram


@patch("requests.get")
def test_telegram(mock_get):
    mock_get.return_value.json.return_value = {"ok": True}
    assert notify_telegram("hi", token="t", chat_id="c") is True
