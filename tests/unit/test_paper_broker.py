import pytest

from src.simulation.paper_broker import OrderSide, PaperBroker


def test_buy_and_sell():
    broker = PaperBroker(
        quote_balance=1000.0,
        fee_rate=0.001,
    )

    buy = broker.buy(price=100.0, quantity=2.0)

    assert buy.side is OrderSide.BUY
    assert broker.base_balance == pytest.approx(2.0)
    assert broker.quote_balance == pytest.approx(799.8)

    sell = broker.sell(price=110.0, quantity=2.0)

    assert sell.side is OrderSide.SELL
    assert broker.base_balance == pytest.approx(0.0)
    assert broker.quote_balance == pytest.approx(1019.58)


def test_reject_insufficient_balance():
    broker = PaperBroker(quote_balance=100.0)

    with pytest.raises(ValueError):
        broker.buy(price=100.0, quantity=2.0)

    with pytest.raises(ValueError):
        broker.sell(price=100.0, quantity=1.0)


def test_equity():
    broker = PaperBroker(
        quote_balance=500.0,
        base_balance=0.01,
    )

    assert broker.equity(60000.0) == pytest.approx(1100.0)
