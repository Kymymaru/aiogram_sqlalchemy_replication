from aiogram import types, Router
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart(deep_link=True))
async def deep_links(message: types.Message):
    """Deep links handler. Example /start qwerty"""
