from aiogram import Dispatcher
from aiogram.enums import ChatType
from loguru import logger

from . import (
    unhandled,
)
from bot.filters.chat_type import ChatTypeFilter


def reg_routers(dp: Dispatcher):
    handlers = [
        unhandled,
    ]
    for handler in handlers:
        handler.router.message.filter(ChatTypeFilter(ChatType.PRIVATE))

        dp.include_router(handler.router)
    logger.opt(colors=True).info(f'<fg #c27ba0>[User.deep_links module {len(handlers)} files imported]</>')