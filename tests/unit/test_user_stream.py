from unittest.mock import Mock, patch

from execution.user_stream import BinanceUserStream


def test_user_stream_uses_callback():
    callback = Mock()

    with patch.dict(
        "os.environ",
        {
            "BINANCE_TESTNET_API_KEY": "test-api-key",
            "BINANCE_TESTNET_SECRET": "test-secret",
        },
        clear=False,
    ):
        stream = BinanceUserStream(on_message=callback)

    message = {
        "e": "executionReport",
        "s": "BTCUSDT",
        "i": 913476,
        "X": "CANCELED",
    }

    stream.on_message(message)

    callback.assert_called_once_with(message)


def test_subscription_request_has_signature():
    with patch.dict(
        "os.environ",
        {
            "BINANCE_TESTNET_API_KEY": "test-api-key",
            "BINANCE_TESTNET_SECRET": "test-secret",
        },
        clear=False,
    ):
        stream = BinanceUserStream()

    request = stream._subscription_request()

    assert request["method"] == ("userDataStream.subscribe.signature")
    assert request["params"]["apiKey"] == "test-api-key"
    assert request["params"]["signature"]
    assert request["params"]["timestamp"] > 0
