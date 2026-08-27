import asyncio
import logging
from typing import Awaitable, Callable, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

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
        
        # Постоянные кнопки (всегда видны под полем ввода)
        self.keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("▶️ Запустить"), KeyboardButton("⏹️ Остановить")],
                [KeyboardButton("📊 Статус"), KeyboardButton("💼 Ордера")],
                [KeyboardButton("📈 Баланс"), KeyboardButton("📜 Сделки")],
                [KeyboardButton("⚙️ Настройки"), KeyboardButton("🔔 Уведомления")],
                [KeyboardButton("🚨 Тревога"), KeyboardButton("🔄 Перезапуск")],
            ],
            resize_keyboard=True,  # Подстроить под размер экрана
        )

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Отправляем сообщение с кнопками
        keyboard = [
            [InlineKeyboardButton("▶️ Запустить", callback_data="start"), InlineKeyboardButton("⏹️ Остановить", callback_data="stop")],
            [InlineKeyboardButton("📊 Статус", callback_data="status"), InlineKeyboardButton("💼 Ордера", callback_data="orders")],
            [InlineKeyboardButton("📈 Баланс", callback_data="balance"), InlineKeyboardButton("📜 Сделки", callback_data="trades")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings"), InlineKeyboardButton("🔔 Уведомления", callback_data="notifications")],
            [InlineKeyboardButton("🚨 Тревога", callback_data="emergency"), InlineKeyboardButton("🔄 Перезапуск", callback_data="restart")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🤖 Crypto Trading Bot\n\nВыберите действие:", reply_markup=reply_markup)

    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        
        if text == "▶️ Запустить":
            await self.on_start()
            await update.message.reply_text("✅ Торговля запущена")
        elif text == "⏹️ Остановить":
            await self.on_stop()
            await update.message.reply_text("⏹️ Торговля остановлена")
        elif text == "📊 Статус":
            status = await self.on_status()
            await update.message.reply_text(f"📊 Статус:\n{status}")
        elif text == "💼 Ордера":
            orders = await self.on_orders()
            await update.message.reply_text(f"💼 Открытые ордера:\n{orders}")
        elif text == "📈 Баланс":
            balance = await self.on_balance()
            await update.message.reply_text(f"📈 Баланс:\n{balance}")
        elif text == "📜 Сделки":
            trades = await self.on_trades()
            await update.message.reply_text(f"📜 Последние сделки:\n{trades}")
        elif text == "⚙️ Настройки":
            settings = await self.on_settings()
            await update.message.reply_text(f"⚙️ Настройки:\n{settings}")
        elif text == "🔔 Уведомления":
            await update.message.reply_text("🔔 Уведомления: ВКЛ\n\n(В разработке)")
        elif text == "🚨 Тревога":
            emergency = await self.on_emergency()
            await update.message.reply_text(f"🚨 Тревога:\n{emergency}")
        elif text == "🔄 Перезапуск":
            await update.message.reply_text("🔄 Перезапуск...")
            await self.on_restart()

    async def _callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "start":
            await self.on_start()
            await query.edit_message_text("✅ Торговля запущена")
        elif query.data == "stop":
            await self.on_stop()
            await query.edit_message_text("⏹️ Торговля остановлена")
        elif query.data == "status":
            status = await self.on_status()
            await query.edit_message_text(f"📊 Статус:\n{status}")
        elif query.data == "orders":
            orders = await self.on_orders()
            await query.edit_message_text(f"💼 Открытые ордера:\n{orders}")
        elif query.data == "balance":
            balance = await self.on_balance()
            await query.edit_message_text(f"📈 Баланс:\n{balance}")
        elif query.data == "trades":
            trades = await self.on_trades()
            await query.edit_message_text(f"📜 Последние сделки:\n{trades}")
        elif query.data == "settings":
            settings = await self.on_settings()
            await query.edit_message_text(f"⚙️ Настройки:\n{settings}")
        elif query.data == "notifications":
            await query.edit_message_text("🔔 Уведомления: ВКЛ\n\n(В разработке)")
        elif query.data == "emergency":
            emergency = await self.on_emergency()
            await query.edit_message_text(f"🚨 Тревога:\n{emergency}")
        elif query.data == "restart":
            await query.edit_message_text("🔄 Перезапуск...")
            await self.on_restart()

    async def run(self) -> None:
        self._app = Application.builder().token(self.bot_token).build()
        self._app.add_handler(CommandHandler("start", self._start_command))
        self._app.add_handler(CallbackQueryHandler(self._callback_handler))
        self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text))
        
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
