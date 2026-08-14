from __future__ import annotations

import argparse
from decimal import Decimal

from execution.binance_testnet import BinanceTestnetClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Binance Testnet order",
    )
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument(
        "--side",
        choices=("BUY", "SELL"),
        required=True,
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        choices=("LIMIT", "MARKET"),
        required=True,
    )
    parser.add_argument("--quantity", required=True)
    parser.add_argument("--price")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    quantity = Decimal(args.quantity)

    if quantity <= 0:
        raise SystemExit("quantity must be greater than zero")

    if args.order_type == "LIMIT":
        if args.price is None:
            raise SystemExit(
                "--price is required for LIMIT orders"
            )

        price = Decimal(args.price)

        if price <= 0:
            raise SystemExit("price must be greater than zero")
    else:
        price = None

    client = BinanceTestnetClient()

    params = {
        "symbol": args.symbol.upper(),
        "side": args.side,
        "type": args.order_type,
        "quantity": format(quantity, "f"),
    }

    if price is not None:
        params["price"] = format(price, "f")
        params["timeInForce"] = "GTC"

    client.test_order(**params)

    print("Order parameters are valid")
    print(f"  symbol: {params['symbol']}")
    print(f"  side: {params['side']}")
    print(f"  type: {params['type']}")
    print(f"  quantity: {params['quantity']}")

    if price is not None:
        print(f"  price: {params['price']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
