from aiogram import Router


def get_owner_router() -> Router:
    from . import ping, statistics

    router = Router()
    router.include_router(ping.router)
    router.include_router(statistics.router)

    return router
