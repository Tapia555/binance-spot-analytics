from unittest.mock import Mock, patch

from src.execution.binance_testnet import BinanceTestnetClient


@patch.dict(
    "os.environ",
    {
        "BINANCE_TESTNET_API_KEY": "test-api-key",
        "BINANCE_TESTNET_SECRET": "test-secret",
    },
)
@patch("src.execution.binance_testnet.requests.request")
def test_test_limit_order(mock_request):
    response = Mock()
    response.ok = True
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

    call = mock_request.call_args
    assert call.args[0] == "POST"
    assert call.args[1].endswith("/v3/order/test")
    assert call.kwargs["headers"]["X-MBX-APIKEY"] == "test-api-key"
    assert "signature" in call.kwargs["params"]


@patch.dict(
    "os.environ",
    {
        "BINANCE_TESTNET_API_KEY": "test-api-key",
        "BINANCE_TESTNET_SECRET": "test-secret",
    },
)
@patch("src.execution.binance_testnet.requests.request")
def test_api_error_is_converted_to_runtime_error(mock_request):
    response = Mock()
    response.ok = False
    response.json.return_value = {
        "code": -1013,
        "msg": "Filter failure: NOTIONAL",
    }
    mock_request.return_value = response

    client = BinanceTestnetClient()

    try:
        client.test_limit_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.00001",
            price="65008.91",
        )
    except RuntimeError as error:
        assert "-1013" in str(error)
        assert "NOTIONAL" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")
