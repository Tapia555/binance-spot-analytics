from unittest.mock import Mock, patch

import pytest

from execution.api_errors import BinanceRateLimitError
from execution.binance_testnet import BinanceTestnetClient


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


@patch.dict(
    "os.environ",
    {
        "BINANCE_TESTNET_API_KEY": "test-api-key",
        "BINANCE_TESTNET_SECRET": "test-secret",
    },
)
@patch("execution.binance_testnet.requests.request")
def test_418_raises_rate_limit_error(mock_request):
    response = Mock()
    response.status_code = 418
    response.ok = False
    response.headers = {"Retry-After": "60"}
    response.json.return_value = {
        "code": -1003,
        "msg": "IP banned",
    }
    mock_request.return_value = response

    client = BinanceTestnetClient()

    with pytest.raises(BinanceRateLimitError) as error:
        client.get_account()

    assert error.value.status_code == 418
    assert error.value.retry_after == 60
