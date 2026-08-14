from __future__ import annotations

import argparse

from execution.binance_testnet import BinanceTestnetClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cancel a Binance Spot Testnet order",
    )
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--order-id", required=True, type=int)
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm cancellation",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.order_id <= 0:
        raise SystemExit("order-id must be greater than zero")

    if not args.confirm:
        print("Cancellation preview only. Nothing was sent.")
        print(f"  symbol: {args.symbol.upper()}")
        print(f"  order_id: {args.order_id}")
        print()
        print("To cancel this Testnet order, add: --confirm")
        return 0

    client = BinanceTestnetClient()

    result = client.cancel_order(
        symbol=args.symbol.upper(),
        order_id=args.order_id,
    )

    print("Testnet order cancellation submitted")
    print(f"  orderId: {result.get('orderId')}")
    print(f"  status: {result.get('status')}")
    print(f"  symbol: {result.get('symbol')}")
    print(f"  side: {result.get('side')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
