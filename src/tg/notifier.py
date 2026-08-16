from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        if not enabled:
            logger.info("Telegram notifications disabled")

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.enabled:
            return False
            
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode,
            }
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Telegram: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False

    def notify_trade(
        self,
        action: str,
        symbol: str,
        price: float,
        amount: float,
        reason: str,
    ) -> None:
        emoji = "🟢" if action == "BUY" else "🔴"
        text = (
            f"{emoji} <b>{action}</b>\n\n"
            f"Symbol: {symbol}\n"
            f"Price: {price}\n"
            f"Amount: {amount}\n"
            f"Reason: {reason}"
        )
        self.send_message(text)

    def notify_balance(
        self,
        balance: float,
        equity: float,
        pnl: float,
    ) -> None:
        pnl_emoji = "📈" if pnl >= 0 else "📉"
        text = (
            f"💰 <b>Balance Update</b>\n\n"
            f"Balance: {balance} USDT\n"
            f"Equity: {equity} USDT\n"
            f"{pnl_emoji} PnL: {pnl:.2f} USDT"
        )
        self.send_message(text)

    def notify_status(
        self,
        is_running: bool,
        symbol: str,
        trades_count: int,
    ) -> None:
        status_emoji = "✅" if is_running else "⏸️"
        text = (
            f"{status_emoji} <b>Bot Status</b>\n\n"
            f"Running: {is_running}\n"
            f"Symbol: {symbol}\n"
            f"Trades: {trades_count}"
        )
        self.send_message(text)

    def notify_start(self) -> None:
        self.send_message("🚀 <b>Bot Started</b>")

    def notify_stop(self) -> None:
        self.send_message("⏹️ <b>Bot Stopped</b>")
