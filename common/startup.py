from __future__ import annotations

from config.db import engine, Base


async def on_app_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def on_app_shutdown() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
