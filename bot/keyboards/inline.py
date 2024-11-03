from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.factory import ExampleCallback


def example():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Common Button',
        callback_data=ExampleCallback(param_1='some param', param_2=123).pack()
    )
    sizes = [1]
    return builder.adjust(*sizes).as_markup()
