import asyncio
import logging
from typing import Awaitable, Callable, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    def __init__(
        self,
        bot_token: str,
        on_start,
        on_stop,
        on_status,
        on_orders,
        on_balance,
        on_trades,
        on_settings,
        on_emergency,
        on_restart,
    ) -> None:
        self.bot_token = bot_token
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_status = on_status
        self.on_orders = on_orders
        self.on_balance = on_balance
        self.on_trades = on_trades
        self.on_settings = on_settings
        self.on_emergency = on_emergency
        self.on_restart = on_restart
        self._app = None

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("▶️ Start", callback_data="start"), InlineKeyboardButton("⏹️ Stop", callback_data="stop")],
            [InlineKeyboardButton("📊 Status", callback_data="status"), InlineKeyboardButton("💼 Orders", callback_data="orders")],
            [InlineKeyboardButton("📈 Balance", callback_data="balance"), InlineKeyboardButton("📜 Trades", callback_data="trades")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings"), InlineKeyboardButton("🔔 Notifications", callback_data="notifications")],
            [InlineKeyboardButton("🚨 Emergency", callback_data="emergency"), InlineKeyboardButton("🔄 Restart", callback_data="restart")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🤖 Crypto Trading Bot\n\nНажми на кнопку:", reply_markup=reply_markup)

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
        elif query.data == "orders":
            orders = await self.on_orders()
            await query.edit_message_text(f"💼 Open Orders:\n{orders}")
        elif query.data == "balance":
            balance = await self.on_balance()
            await query.edit_message_text(f"📈 Balance:\n{balance}")
        elif query.data == "trades":
            trades = await self.on_trades()
            await query.edit_message_text(f"📜 Recent Trades:\n{trades}")
        elif query.data == "settings":
            settings = await self.on_settings()
            await query.edit_message_text(f"⚙️ Settings:\n{settings}")
        elif query.data == "notifications":
            await query.edit_message_text("🔔 Notifications: ON")
        elif query.data == "emergency":
            emergency = await self.on_emergency()
            await query.edit_message_text(f"🚨 Emergency:\n{emergency}")
        elif query.data == "restart":
            await query.edit_message_text("🔄 Restarting...")
            await self.on_restart()

    async def run(self) -> None:
        self._app = Application.builder().token(self.bot_token).build()
        self._app.add_handler(CommandHandler("start", self._start_command))
        self._app.add_handler(CallbackQueryHandler(self._callback_handler))
        
        logger.info("Telegram bot polling started")
        
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Bot handler cancelled")
        finally:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
