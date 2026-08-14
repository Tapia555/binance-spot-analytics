from __future__ import annotations

import argparse
from decimal import Decimal

from execution.binance_testnet import BinanceTestnetClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place a Binance Spot Testnet order",
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
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm sending the Testnet order",
    )
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

    if not args.confirm:
        print("Order preview only. Nothing was sent.")
        print(f"  symbol: {args.symbol.upper()}")
        print(f"  side: {args.side}")
        print(f"  type: {args.order_type}")
        print(f"  quantity: {args.quantity}")

        if price is not None:
            print(f"  price: {args.price}")

        print()
        print(
            "To send this Testnet order, add: --confirm"
        )
        return 0

    client = BinanceTestnetClient()

    params = {
        "symbol": args.symbol.upper(),
        "side": args.side,
        "type": args.order_type,
        "quantity": format(quantity, "f"),
        "newOrderRespType": "RESULT",
    }

    if price is not None:
        params["price"] = format(price, "f")
        params["timeInForce"] = "GTC"

    result = client._signed_request(
        "POST",
        "/v3/order",
        params=params,
    )

    print("Testnet order submitted")

    if result:
        print(f"  orderId: {result.get('orderId')}")
        print(f"  status: {result.get('status')}")
        print(f"  symbol: {result.get('symbol')}")
        print(f"  side: {result.get('side')}")
        print(f"  type: {result.get('type')}")
    else:
        print("The server returned an empty response.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
