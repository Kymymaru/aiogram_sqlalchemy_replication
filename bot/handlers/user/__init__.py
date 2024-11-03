from aiogram import Dispatcher

from . import (
    main,
    deep_link,
)


def reg_packages(dp: Dispatcher):
    packages = [
        main,
        deep_link,
    ]
    for package in packages:
        package.reg_routers(dp)
