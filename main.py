import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.client.bot import DefaultBotProperties

import config
from handlers import main_menu, admin_menu, registration

async def on_startup(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="/start", description="Начать"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/admin", description="Mеню админа"),
        BotCommand(command="/get_state", description="Узнать текущее состояние")
    ])

async def main():
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(registration.reg_router)  # Регистрируем роутер для регистрации первым
    dp.include_router(main_menu.router)
    dp.include_router(admin_menu.router)
    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
