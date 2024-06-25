from aiogram import Router


def get_user_router() -> Router:
    """
    Get user handlers router
    Returns:
        router: Router instance with user routers inside.
    """
    from . import (callbacks,
                   info,
                   location,
                   menu,
                   start)

    router = Router()

    router.include_router(callbacks.router)
    router.include_router(info.router)
    router.include_router(location.router)
    router.include_router(start.router)
    
    # menu router needs to be imported latest, because otherwise menu will overtake another commands.
    router.include_router(menu.router)

    return router
