from aiogram import Router


def get_handlers_router() -> Router:
    """
    Get all handlers router
    Returns:
        router: Router instance with ALL routers inside.
    """
    from .owner import get_owner_router
    from .user import get_user_router

    router = Router()

    owner_router = get_owner_router()
    user_router = get_user_router()

    router.include_router(owner_router)
    router.include_router(user_router)

    return router
