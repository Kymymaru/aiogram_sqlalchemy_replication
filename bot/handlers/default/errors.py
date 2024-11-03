from aiogram import types, Router

router = Router()


@router.errors()
async def error_handler(event: types.ErrorEvent):
    """Обработка ошибок"""
    pass
