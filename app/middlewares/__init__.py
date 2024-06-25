# import os
# from importlib import import_module
#
# for module in os.listdir(os.path.dirname(__file__)):
#     if module == "__init__.py" or module[-3:] != ".py":
#         continue
#     import_module(f".{module[:-3]}", __package__)

from aiogram import Dispatcher

from app.config import Config


def register_middlewares(dp: Dispatcher, config: Config):
    from . import main as main_middleware
    from . import throttling

    main_middleware.register_middleware(dp=dp)
    throttling.register_middleware(dp=dp, config=config)
