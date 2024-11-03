from aiogram import Dispatcher
from aiogram.enums import ChatType
from loguru import logger

from . import (
    start,
)
from bot.filters.chat_type import ChatTypeFilter


def reg_routers(dp: Dispatcher):
    handlers = [
        start,
    ]
    for handler in handlers:
        handler.router.message.filter(ChatTypeFilter(ChatType.PRIVATE))

        dp.include_router(handler.router)
    logger.opt(colors=True).info(f'<fg #6fa8dc>[User.main module {len(handlers)} files imported]</>')
