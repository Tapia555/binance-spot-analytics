from __future__ import annotations

import argparse
from decimal import Decimal

from execution.binance_testnet import BinanceTestnetClient
from execution.execution_state import ExecutionState
from execution.state_sync import StateSynchronizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show Binance Testnet account state",
    )
    parser.add_argument(
        "--symbol",
        default="BTCUSDT",
        help="Trading symbol, default: BTCUSDT",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    client = BinanceTestnetClient()
    state = ExecutionState()

    StateSynchronizer(
        client=client,
        state=state,
    ).sync(args.symbol)

    snapshot = state.snapshot()

    print("Balances:")
    for balance in snapshot.balances:
        total = balance.free + balance.locked

        if total == Decimal("0"):
            continue

        print(
            f"  {balance.asset}: "
            f"free={balance.free} "
            f"locked={balance.locked} "
            f"total={total}"
        )

    print()
    print(f"Open orders: {len(snapshot.orders)}")

    for order in snapshot.orders:
        print(
            f"  #{order.order_id} "
            f"{order.symbol} "
            f"{order.side} "
            f"{order.order_type} "
            f"status={order.status} "
            f"executed={order.executed_quantity}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
