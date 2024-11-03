from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_bot_commands(bot: Bot):
    user_commands = [
        BotCommand(command='start', description='Перезагрузить бота 🔄')
    ]
    await bot.set_my_commands(commands=user_commands, scope=BotCommandScopeAllPrivateChats())
