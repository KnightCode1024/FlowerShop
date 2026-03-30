from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from entrypoint.config import config


engine = create_async_engine(
    config.database.DATABASE_URI,
    pool_pre_ping=True,
    echo=True,
    pool_size=5,
    max_overflow=10
)
session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)