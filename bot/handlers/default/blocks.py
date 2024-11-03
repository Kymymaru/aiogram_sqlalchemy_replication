from aiogram import types, Router
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, KICKED

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> KICKED))
async def bot_blocked(event: types.ChatMemberUpdated):
    """Блок бота"""
    pass


@router.my_chat_member(ChatMemberUpdatedFilter(KICKED >> IS_MEMBER))
async def bot_unblocked(event: types.ChatMemberUpdated):
    """Разблок"""
    pass
