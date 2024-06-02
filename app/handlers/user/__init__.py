# import os
# from importlib import import_module
#
# for module in os.listdir(os.path.dirname(__file__)):
#     if module == "__init__.py" or module[-3:] != ".py":
#         continue
#     import_module(f".{module[:-3]}", __package__)

from aiogram import Router


def get_user_router() -> Router:
    from . import (callbacks,
                   geolocation,
                   info,
                   location,
                   menu,
                   start)

    router = Router()
    router.include_router(callbacks.router)
    router.include_router(info.router)
    router.include_router(menu.router)
    router.include_router(start.router)
    router.include_router(geolocation.router)
    router.include_router(location.router)

    return router
