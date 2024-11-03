from typing import Any, Awaitable, Dict, Callable, Union

from aiogram import BaseMiddleware
from aiogram.types import Update

from bot.database import DbManager


class DatabaseInstance(BaseMiddleware):
    def __init__(self, db: DbManager):
        self.db = db

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Union[Update, Any],
            data: Dict[str, Any]
    ) -> Any:
        async with self.db.get_session() as session:
            async with session.begin():
                data['session'] = session
                await handler(event, data)
