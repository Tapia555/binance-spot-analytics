from __future__ import annotations

import argparse

from execution.binance_testnet import BinanceTestnetClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query a Binance Spot Testnet order",
    )
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--order-id", required=True, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.order_id <= 0:
        raise SystemExit("order-id must be greater than zero")

    client = BinanceTestnetClient()

    order = client.get_order(
        symbol=args.symbol.upper(),
        order_id=args.order_id,
    )

    print("Testnet order status")
    print(f"  orderId: {order.get('orderId')}")
    print(f"  status: {order.get('status')}")
    print(f"  symbol: {order.get('symbol')}")
    print(f"  side: {order.get('side')}")
    print(f"  type: {order.get('type')}")
    print(f"  price: {order.get('price')}")
    print(f"  origQty: {order.get('origQty')}")
    print(f"  executedQty: {order.get('executedQty')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
