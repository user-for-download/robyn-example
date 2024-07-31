from typing import Type, Tuple, Dict, Any

from robyn import logger
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import Base, async_session


async def active(session, model, **kwargs):
    stmt = select(model).filter(model.deleted_at.is_(None)).filter_by(**kwargs).order_by(model.id.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def active_random(session, model, **kwargs):
    stmt = select(model).filter(model.deleted_at.is_(None)).filter_by(**kwargs)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_from_id(session, model, model_id: int):
    stmt = select(model).filter(model.deleted_at.is_(None)).where(model.id == model_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_from(session: AsyncSession, model, field, value):
    try:
        stmt = select(model).where(field == value)
        result = await session.execute(stmt)
        return result.scalars().first()
    except Exception as e:
        logger.error("get_from: %s", e)


async def get_auth(model, field, value):
    try:
        async with async_session() as session:
            stmt = select(model).where(field == value)
            result = await session.execute(stmt)
            return result.scalars().first()
    except Exception as e:
        logger.error("get_auth: %s", e)
    finally:
        await session.aclose()


async def filter_model(session, model, filter_):
    stmt = select(model).filter(filter_)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_count_conn():
    async with async_session() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active';"))
        count = result.scalar()
    return {"count": count}


async def get_or_create(
        session: AsyncSession,
        model: Type[Base],
        defaults: Dict[str, Any] = None,
        **kwargs
) -> Tuple[Base, bool]:
    """
    Attempts to get an instance of the model matching the kwargs.
    If not found, creates a new instance with the combined kwargs and defaults.

    :param session: SQLAlchemy AsyncSession
    :param model: SQLAlchemy model class
    :param defaults: Dictionary of fields to create the new instance
    :param kwargs: Fields to filter the query
    :return: Tuple containing the instance and a boolean indicating if it was created
    """
    result = await session.execute(select(model).filter_by(**kwargs))
    instance = result.scalars().first()

    if instance:
        return instance, False

    params = {**kwargs, **(defaults or {})}
    instance = model(**params)
    session.add(instance)
    try:
        await session.commit()
        return instance, True
    except IntegrityError:
        await session.rollback()
        result = await session.execute(select(model).filter_by(**kwargs))
        instance = result.scalars().first()
        if instance:
            return instance, False
        raise


async def update_or_create(
        session: AsyncSession,
        model: Type[Base],
        defaults: Dict[str, Any] = None,
        **kwargs
) -> Tuple[Base, bool]:
    """
    Attempts to get an instance of the model matching the kwargs.
    If found, updates it with the defaults.
    If not found, creates a new instance with the combined kwargs and defaults.

    :param session: SQLAlchemy AsyncSession
    :param model: SQLAlchemy model class
    :param defaults: Dictionary of fields to update or create
    :param kwargs: Fields to filter the query
    :return: Tuple containing the instance and a boolean indicating if it was created
    """
    result = await session.execute(select(model).filter_by(**kwargs))
    instance = result.scalars().first()

    if instance:
        for key, value in (defaults or {}).items():
            setattr(instance, key, value)
        created = False
    else:
        params = {**kwargs, **(defaults or {})}
        instance = model(**params)
        session.add(instance)
        created = True

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        result = await session.execute(select(model).filter_by(**kwargs))
        instance = result.scalars().first()
        if instance:
            for key, value in (defaults or {}).items():
                setattr(instance, key, value)
            await session.commit()
            created = False
        else:
            raise

    return instance, created
