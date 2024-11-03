from aiogram.filters.callback_data import CallbackData


class ExampleCallback(CallbackData, prefix='example'):
    param_1: str
    param_2: int
