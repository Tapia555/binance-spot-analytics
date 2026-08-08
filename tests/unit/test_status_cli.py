from decimal import Decimal
from unittest.mock import patch

from src.cli.status import build_parser, main
from src.execution.execution_state import StateSnapshot


def test_status_parser_default_symbol():
    args = build_parser().parse_args([])

    assert args.symbol == "BTCUSDT"


def test_status_parser_custom_symbol():
    args = build_parser().parse_args(
        ["--symbol", "ETHUSDT"]
    )

    assert args.symbol == "ETHUSDT"


def test_status_main_prints_state(capsys):
    snapshot = StateSnapshot(
        orders=(),
        balances=(
            type(
                "Balance",
                (),
                {
                    "asset": "USDT",
                    "free": Decimal("10000"),
                    "locked": Decimal("0"),
                },
            )(),
        ),
    )

    with patch(
        "src.cli.status.StateSynchronizer.sync"
    ), patch(
        "src.cli.status.ExecutionState.snapshot",
        return_value=snapshot,
    ):
        result = main([])

    output = capsys.readouterr().out

    assert result == 0
    assert "USDT" in output
    assert "Open orders: 0" in output
