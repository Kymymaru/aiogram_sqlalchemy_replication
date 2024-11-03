from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text='Button'
    )
    size = [1]
    return builder.adjust(*size).as_markup(
        resize_keyboard=True,
        input_field_placeholder='Main Menu'
    )

