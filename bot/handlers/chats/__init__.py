from aiogram import Dispatcher
from aiogram.enums import ChatType
from loguru import logger

from bot.filters.chat_type import ChatTypeFilter


def reg_routers(dp: Dispatcher):
    handlers = [
        ...
    ]
    # for handler in handlers:
    #     handler.router.message.filter(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]))
    #
    #     dp.include_router(handler.router)
    logger.opt(colors=True).info(f'<fg #ffeeb9>[Chats module {len(handlers)} handlers imported]</>')
