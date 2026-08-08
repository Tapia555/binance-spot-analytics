from __future__ import annotations

import json

from src.execution.execution_state import ExecutionState
from src.execution.user_stream import BinanceUserStream


class TrackingUserStream(BinanceUserStream):
    def __init__(self, state: ExecutionState) -> None:
        super().__init__()
        self.state = state

    def handle_message(self, message: dict) -> None:
        event_type = self.state.apply_event(message)

        if event_type == "executionReport":
            event = message.get("event", message)
            print(
                "ORDER UPDATE:",
                event.get("i"),
                event.get("s"),
                event.get("X"),
            )
            return

        if event_type == "outboundAccountPosition":
            event = message.get("event", message)
            print(
                "ACCOUNT UPDATE:",
                event.get("e"),
                "at",
                event.get("u"),
            )
            return

        print(json.dumps(message, indent=2))


if __name__ == "__main__":
    TrackingUserStream(
        state=ExecutionState(),
    ).subscribe()
