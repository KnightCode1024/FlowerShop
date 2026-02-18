import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from entrypoint.config import config

engine = create_async_engine(
    config.database.get_db_url(), future=True
)

session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)