import asyncio
import logging
from typing import Awaitable, Callable, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    def __init__(
        self,
        bot_token: str,
        on_start: Callable[[], Awaitable[None]],
        on_stop: Callable[[], Awaitable[None]],
        on_status: Callable[[], Awaitable[str]],
        on_orders: Callable[[], Awaitable[str]],
        on_balance: Callable[[], Awaitable[str]],
        on_trades: Callable[[], Awaitable[str]],
        on_settings: Callable[[], Awaitable[str]],
        on_emergency: Callable[[], Awaitable[str]],
        on_restart: Callable[[], Awaitable[None]],
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
        self._app: Optional[Application] = None
        
        # Постоянные кнопки
        self.main_keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("▶️ Start"), KeyboardButton("⏹️ Stop")],
                [KeyboardButton("📊 Status"), KeyboardButton("💼 Orders")],
                [KeyboardButton("📈 Balance"), KeyboardButton("📜 Trades")],
                [KeyboardButton("⚙️ Settings"), KeyboardButton("🔔 Notifications")],
                [KeyboardButton("🚨 Emergency"), KeyboardButton("🔄 Restart")],
            ],
            resize_keyboard=True,
        )

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("▶️ Start", callback_data="start"),
                InlineKeyboardButton("⏹️ Stop", callback_data="stop"),
            ],
            [
                InlineKeyboardButton("📊 Status", callback_data="status"),
                InlineKeyboardButton("💼 Orders", callback_data="orders"),
            ],
            [
                InlineKeyboardButton("📈 Balance", callback_data="balance"),
                InlineKeyboardButton("📜 Trades", callback_data="trades"),
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                InlineKeyboardButton("🔔 Notifications", callback_data="notifications"),
            ],
            [
                InlineKeyboardButton("🚨 Emergency", callback_data="emergency"),
                InlineKeyboardButton("🔄 Restart", callback_data="restart"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🤖 Crypto Trading Bot\n\nВыберите действие:",
            reply_markup=reply_markup,
        )

    async def _handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        
        if text == "▶️ Start":
            await self.on_start()
            await update.message.reply_text("✅ Trading started")
        elif text == "⏹️ Stop":
            await self.on_stop()
            await update.message.reply_text("⏹️ Trading stopped")
        elif text == "📊 Status":
            status = await self.on_status()
            await update.message.reply_text(f"📊 Status:\n{status}")
        elif text == "💼 Orders":
            orders = await self.on_orders()
            await update.message.reply_text(f"💼 Open Orders:\n{orders}")
        elif text == "📈 Balance":
            balance = await self.on_balance()
            await update.message.reply_text(f"📈 Balance:\n{balance}")
        elif text == "📜 Trades":
            trades = await self.on_trades()
            await update.message.reply_text(f"📜 Recent Trades:\n{trades}")
        elif text == "⚙️ Settings":
            settings = await self.on_settings()
            await update.message.reply_text(f"⚙️ Settings:\n{settings}")
        elif text == "🔔 Notifications":
            await update.message.reply_text("🔔 Notifications: ON\n\n(Coming soon)")
        elif text == "🚨 Emergency":
            emergency = await self.on_emergency()
            await update.message.reply_text(f"🚨 Emergency:\n{emergency}")
        elif text == "🔄 Restart":
            await update.message.reply_text("🔄 Restarting...")
            await self.on_restart()

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
            await query.edit_message_text("🔔 Notifications: ON\n\n(Coming soon)")
        elif query.data == "emergency":
            emergency = await self.on_emergency()
            await query.edit_message_text(f"🚨 Emergency:\n{emergency}")
        elif query.data == "restart":
            await query.edit_message_text("🔄 Restarting...")
            await self.on_restart()

    async def run(self) -> None:
        self._app = Application.builder().token(self.bot_token).build()
        
        # Команды
        self._app.add_handler(CommandHandler("start", self._start_command))
        
        # Callback (inline кнопки)
        self._app.add_handler(CallbackQueryHandler(self._callback_handler))
        
        # Текст (постоянные кнопки)
        self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_button))
        
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
