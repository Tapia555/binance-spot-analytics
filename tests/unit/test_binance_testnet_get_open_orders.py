from src.execution.binance_testnet import BinanceTestnetClient


def test_get_open_orders_returns_list():
    client = BinanceTestnetClient()
    orders = client.get_open_orders(symbol="BTCUSDT")
    assert isinstance(orders, list)
