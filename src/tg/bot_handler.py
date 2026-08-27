from __future__ import annotations

import asyncio
import logging
from typing import Callable, Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    def __init__(
        self,
        bot_token: str,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        on_status: Optional[Callable] = None,
    ) -> None:
        self.bot_token = bot_token
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_status = on_status
        self.is_running = False
        self.application: Optional[Application] = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("Received /start command")
        if self.on_start:
            await self.on_start()
        await update.message.reply_text("🚀 Trading started!")

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("Received /stop command")
        if self.on_stop:
            await self.on_stop()
        await update.message.reply_text("⏹️ Trading stopped!")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("Received /status command")
        if self.on_status:
            status = await self.on_status()
            await update.message.reply_text(status)
        else:
            await update.message.reply_text(f"Status: {'Running' if self.is_running else 'Stopped'}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "🤖 <b>Bot Commands</b>\n\n"
            "/start - Start trading\n"
            "/stop - Stop trading\n"
            "/status - Check bot status\n"
            "/help - Show this help"
        )
        await update.message.reply_text(help_text, parse_mode="HTML")

    async def run(self) -> None:
        self.application = (
            Application.builder()
            .token(self.bot_token)
            .build()
        )
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        logger.info("Telegram bot started")
        
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Keep running
        while True:
            await asyncio.sleep(1)
