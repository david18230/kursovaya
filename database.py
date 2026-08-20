import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    DATABASE_URL,
    echo = True,
    pool_size = 5,
    max_overflow = 10,
    pool_pre_ping=True,
    pool_recycle = 3600,

)

SessionLocal = async_sessionmaker(bind = engine, expire_on_commit = False)

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


