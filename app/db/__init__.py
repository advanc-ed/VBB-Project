from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


async def init(database_url: str) -> sessionmaker:
    """
    Database connection init. Connects to database and creates engine if it doesn't exist.'
    Args:
        database_url: database connection url from config

    Returns:
        sessionmaker: SQLAlchemy sessionmaker

    """
    from app.common import DB

    from .base import Base

    engine = create_async_engine(
        url=database_url,
        echo=False,
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return sessionmaker(engine, expire_on_commit=False, class_=DB)
