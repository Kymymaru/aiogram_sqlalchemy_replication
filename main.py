import asyncio
import sys
from functools import partial

from loguru import logger

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

from redis.asyncio import Redis

from bot.middlewares import DatabaseInstance
from bot.handlers import default, chats, channels, user
from bot.database import DbManager
from bot.ui_commands import set_bot_commands

from config import Config

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <red>|</red> "
    "<level>{level: <8}</level> <red>|</red> "
    "<level>{message}</level>"
)
logger.remove()  # Удаляем предыдущие конфигурации
logger.add(sys.stdout, format=logger_format)


async def on_startup(
        bot: Bot,
        db: DbManager,
        config: Config,
):
    if config.bot.skip_updates:
        await bot.delete_webhook(drop_pending_updates=True)
    else:
        await bot.delete_webhook()

    if not config.bot.polling:
        await bot.set_webhook(f"{config.bot.webhook.url}{config.bot.webhook.path}")

    await db.create_tables()
    config.bot.username = (await bot.get_me()).username
    await set_bot_commands(bot)

    logger.info(f'@{config.bot.username} STARTED')


def main():
    config = Config.load_settings()

    logger.info(f"Attempting Bot Startup")

    bot = Bot(
        token=config.bot.token,
        session=AiohttpSession(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            protect_content=False,
            link_preview_is_disabled=True
        )
    )
    if config.bot.use_redis:
        storage = RedisStorage(Redis(host=config.redis.host, db=config.redis.db))
    else:
        storage = MemoryStorage()

    dp = Dispatcher(storage=storage, config=config)

    channels.reg_routers(dp)
    chats.reg_routers(dp)
    default.reg_routers(dp)
    user.reg_packages(dp)

    db = DbManager()
    db.initialize(config.database)

    dp.update.middleware(DatabaseInstance(db))
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    startup = partial(on_startup, db=db, config=config)
    dp.startup.register(startup)

    if config.bot.polling:
        asyncio.run(start_polling(dp, bot, config))
    else:
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.bot.webhook.path)
        setup_application(app, dp, bot=bot)

        logger.success('WEBHOOK')
        web.run_app(app, host=config.bot.webhook.host, port=config.bot.webhook.port)


async def start_polling(dp: Dispatcher, bot: Bot, config: Config):
    try:
        updates = dp.resolve_used_update_types()
        logger.opt(colors=True).info('Allowed updates: <fg #00ccff>[%s]</>' % ', '.join(updates))
        logger.success('POLLING')
        await dp.start_polling(bot, allowed_updates=updates)
    finally:
        config.save_settings()
        await bot.session.close()
        if config.bot.use_redis:
            await dp.storage.close()


if __name__ == "__main__":
    main()
