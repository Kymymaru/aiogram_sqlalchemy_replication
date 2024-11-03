from aiogram import types, Router
from aiogram.filters import Command

router = Router()


@router.message(Command('start'))
async def start_command(message: types.Message):
    """Start command handler"""
    pass
