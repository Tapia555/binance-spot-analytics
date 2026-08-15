from __future__ import annotations

import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Отправляет уведомления в Telegram."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: bool = False,
    ) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = enabled and bot_token and chat_id
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def send_message(self, message: str) -> bool:
        """Отправляет сообщение в Telegram."""
        if not self.enabled:
            logger.debug("Telegram notifier disabled, skipping message")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        try:
            session = await self._get_session()
            async with session.post(url, json=data) as resp:
                if resp.status == 200:
                    logger.info(f"Telegram message sent: {message[:50]}...")
                    return True
                else:
                    logger.error(
                        f"Telegram API error: {resp.status} - {await resp.text()}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    async def notify_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        signal: str,
    ) -> None:
        """Уведомление об ордере."""
        emoji = "🟢" if side == "BUY" else "🔴"
        message = (
            f"{emoji} <b>{side} Order</b>\n\n"
            f"Symbol: {symbol}\n"
            f"Quantity: {quantity}\n"
            f"Price: ${price:,.2f}\n"
            f"Signal: {signal}"
        )
        await self.send_message(message)

    async def notify_pnl(
        self,
        symbol: str,
        pnl: float,
        pnl_pct: float,
    ) -> None:
        """Уведомление о PnL."""
        emoji = "✅" if pnl >= 0 else "❌"
        color = "🟢" if pnl >= 0 else "🔴"
        message = (
            f"{emoji} <b>Position Closed</b>\n\n"
            f"Symbol: {symbol}\n"
            f"{color} PnL: ${pnl:,.2f} ({pnl_pct:+.2f}%)"
        )
        await self.send_message(message)

    async def notify_error(self, error: str) -> None:
        """Уведомление об ошибке."""
        message = f"❌ <b>Error</b>\n\n{error}"
        await self.send_message(message)
