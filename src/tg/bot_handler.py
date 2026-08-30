import asyncio
import logging
from typing import Awaitable, Callable, Optional

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

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
        on_pnl=None,
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
        self.on_pnl = on_pnl
        self._app = None
        
        self.keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("▶️ Запустить"), KeyboardButton("⏹️ Остановить")],
                [KeyboardButton("📊 Статус"), KeyboardButton("💼 Ордера")],
                [KeyboardButton("📈 Баланс"), KeyboardButton("📜 Сделки")],
                [KeyboardButton("📊 PNL"), KeyboardButton("⚙️ Настройки")],
                [KeyboardButton("🚨 Тревога"), KeyboardButton("🔄 Перезапуск")],
            ],
            resize_keyboard=True,
        )

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 Crypto Trading Bot", reply_markup=self.keyboard)

    async def _handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        logger.info(f"Button pressed: {text}")
        
        if text == "▶️ Запустить":
            await self.on_start()
            await update.message.reply_text("✅ Торговля запущена", reply_markup=self.keyboard)
        elif text == "⏹️ Остановить":
            await self.on_stop()
            await update.message.reply_text("⏹️ Торговля остановлена", reply_markup=self.keyboard)
        elif text == "📊 Статус":
            status = await self.on_status()
            await update.message.reply_text(f"📊 Статус:\n{status}", reply_markup=self.keyboard)
        elif text == "💼 Ордера":
            orders = await self.on_orders()
            await update.message.reply_text(f"💼 Ордера:\n{orders}", reply_markup=self.keyboard)
        elif text == "📈 Баланс":
            balance = await self.on_balance()
            await update.message.reply_text(f"📈 Баланс:\n{balance}", reply_markup=self.keyboard)
        elif text == "📜 Сделки":
            trades = await self.on_trades()
            await update.message.reply_text(f"📜 Сделки:\n{trades}", reply_markup=self.keyboard)
        elif text == "📊 PNL":
            if self.on_pnl:
                pnl = await self.on_pnl()
                await update.message.reply_text(f"📊 PNL:\n{pnl}", reply_markup=self.keyboard)
            else:
                await update.message.reply_text("📊 PNL: N/A", reply_markup=self.keyboard)
        elif text == "⚙️ Настройки":
            settings = await self.on_settings()
            await update.message.reply_text(f"⚙️ Настройки:\n{settings}", reply_markup=self.keyboard)
        elif text == "🚨 Тревога":
            emergency = await self.on_emergency()
            await update.message.reply_text(f"🚨 Тревога:\n{emergency}", reply_markup=self.keyboard)
        elif text == "🔄 Перезапуск":
            await update.message.reply_text("🔄 Перезапуск...", reply_markup=self.keyboard)

    async def run(self) -> None:
        self._app = Application.builder().token(self.bot_token).build()
        self._app.add_handler(CommandHandler("start", self._start_command))
        self._app.add_handler(MessageHandler(filters.ALL, self._handle_button))
        
        logger.info("Telegram bot started")
        
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()
        
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
