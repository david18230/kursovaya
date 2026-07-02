from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = "postgresql+asyncpg://postgres:Admin@localhost:5432/mybackend"
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size = 5,
    max_overflow = 10,
    pool_pre_ping=True)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session