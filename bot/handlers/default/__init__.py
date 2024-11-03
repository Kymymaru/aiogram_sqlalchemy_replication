from aiogram import Dispatcher
from aiogram.enums import ChatType
from loguru import logger

from . import (
    blocks,
    errors,
)
from bot.filters.chat_type import ChatTypeFilter


def reg_routers(dp: Dispatcher):
    handlers = [
        blocks,
        errors,
    ]
    for handler in handlers:
        handler.router.message.filter(ChatTypeFilter(ChatType.PRIVATE))

        dp.include_router(handler.router)

    logger.opt(colors=True).info(f'<fg #ff7a00>[Default module {len(handlers)} files imported]</>')
