import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.flowershop_api.entrypoint.ioc.database import engine
from src.flowershop_api.models import Base


async def drop_all_tables_cascade():
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(
                text(f'DROP TABLE IF EXISTS "{table.name}" CASCADE')
            )


async def async_recreate_schemas():
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
            logging.info("Dropped all tables")
        except SQLAlchemyError as e:
            logging.warning("Drop all failed, using CASCADE", exc_info=e)
            await drop_all_tables_cascade()

        await conn.run_sync(Base.metadata.create_all)


def recreate_schemas():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logging.info("Recreate all tables")

