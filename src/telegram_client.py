from __future__ import annotations

import logging

import aiohttp

from .config import settings

logger = logging.getLogger(__name__)


async def send_telegram_message(message: str) -> None:
    """Sends a message to Telegram."""
    if not settings.telegram.enabled:
        logger.debug("Telegram disabled")
        return
    
    if not settings.telegram.bot_token or not settings.telegram.chat_id:
        logger.warning("Telegram bot_token or chat_id not configured")
        return
    
    url = f"https://api.telegram.org/bot{settings.telegram.bot_token}/sendMessage"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={
                    "chat_id": settings.telegram.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                },
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    logger.info("Telegram message sent")
                else:
                    logger.error(f"Telegram error: {response.status}")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
