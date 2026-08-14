from unittest.mock import Mock, patch

import pytest

from execution.binance_testnet import BinanceTestnetClient
from execution.api_errors import BinanceRateLimitError


@patch.dict(
    "os.environ",
    {
        "BINANCE_TESTNET_API_KEY": "test-api-key",
        "BINANCE_TESTNET_SECRET": "test-secret",
    },
)
@patch("execution.binance_testnet.requests.request")
def test_test_limit_order(mock_request):
    response = Mock()
    response.status_code = 200
    response.ok = True
    response.headers = {}
    response.json.return_value = {}
    mock_request.return_value = response

    client = BinanceTestnetClient()

    result = client.test_limit_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity="0.00008",
        price="65008.91",
    )

    assert result == {}
    mock_request.assert_called_once()


@patch.dict(
    "os.environ",
    {
        "BINANCE_TESTNET_API_KEY": "test-api-key",
        "BINANCE_TESTNET_SECRET": "test-secret",
    },
)
@patch("execution.binance_testnet.requests.request")
def test_api_error_is_converted_to_runtime_error(mock_request):
    response = Mock()
    response.status_code = 400
    response.ok = False
    response.headers = {}
    response.json.return_value = {
        "code": -1013,
        "msg": "Filter failure: NOTIONAL",
    }
    mock_request.return_value = response

    client = BinanceTestnetClient()

    with pytest.raises(RuntimeError) as error:
        client.test_limit_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.00001",
            price="65008.91",
        )

    assert "-1013" in str(error.value)
    assert "NOTIONAL" in str(error.value)


@patch.dict(
    "os.environ",
    {
        "BINANCE_TESTNET_API_KEY": "test-api-key",
        "BINANCE_TESTNET_SECRET": "test-secret",
    },
)
@patch("execution.binance_testnet.requests.request")
def test_429_raises_rate_limit_error(mock_request):
    response = Mock()
    response.status_code = 429
    response.ok = False
    response.headers = {"Retry-After": "3"}
    response.json.return_value = {
        "code": -1003,
        "msg": "Too many requests",
    }
    mock_request.return_value = response

    client = BinanceTestnetClient()

    with pytest.raises(BinanceRateLimitError) as error:
        client.get_account()

    assert error.value.status_code == 429
    assert error.value.error_code == -1003
    assert error.value.retry_after == 3
