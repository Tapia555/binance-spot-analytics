import asyncio
import logging
from typing import Awaitable, Callable, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    def __init__(
        self,
        bot_token: str,
        on_start: Callable[[], Awaitable[None]],
        on_stop: Callable[[], Awaitable[None]],
        on_status: Callable[[], Awaitable[str]],
    ) -> None:
        self.bot_token = bot_token
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_status = on_status
        self._app: Optional[Application] = None

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("▶️ Start", callback_data="start"),
                InlineKeyboardButton("⏹️ Stop", callback_data="stop"),
            ],
            [InlineKeyboardButton("📊 Status", callback_data="status")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Crypto Trading Bot\n\nВыберите действие:",
            reply_markup=reply_markup,
        )

    async def _callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "start":
            await self.on_start()
            await query.edit_message_text("✅ Trading started")
        elif query.data == "stop":
            await self.on_stop()
            await query.edit_message_text("⏹️ Trading stopped")
        elif query.data == "status":
            status = await self.on_status()
            await query.edit_message_text(f"📊 Status:\n{status}")

    async def run(self) -> None:
        self._app = Application.builder().token(self.bot_token).build()
        
        self._app.add_handler(CommandHandler("start", self._start_command))
        self._app.add_handler(CallbackQueryHandler(self._callback_handler))
        
        logger.info("Telegram bot polling started")
        await self._app.run_polling(allowed_updates=Update.ALL_TYPES)
