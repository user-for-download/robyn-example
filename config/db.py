from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from orjson import orjson
from sqlalchemy import DateTime, UUID, CHAR, String, Text, Boolean, SmallInteger, BigInteger, JSON, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, class_mapper, Mapped, mapped_column, Session
from typing_extensions import Annotated

from common.utils import get_delta_time
from config.settings import settings

if settings.USE_SQLITE_DB == "True":
    SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3/"

    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL
    )
else:
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL
    )
async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    uuid: Mapped[UUID] = mapped_column(UUID,
                                       unique=True,
                                       primary_key=True,
                                       default=uuid.uuid4,
                                       index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def save(self, session: Session):
        if not self.uuid:
            self.__dict__['created_at'] = datetime.now()
        self.__dict__['updated_at'] = datetime.now()
        session.add(self)
        session.commit()

    def delete(self, session: Session):
        self.__dict__['deleted_at'] = datetime.now()
        self.save(session)

    def restore(self, session: Session):
        self.__dict__['deleted_at'] = None
        self.save(session)

    def get_last_update(self) -> str:
        return get_delta_time(self.updated_at)

    def __repr__(self) -> str:
        return orjson.dumps({col.key: getattr(self, col.key) for col in class_mapper(self.__class__).columns},
                            default=str)


a_id = Annotated[int, mapped_column(BigInteger, primary_key=True, unique=True, index=True)]
a_small_int = Annotated[int, mapped_column(SmallInteger, nullable=True)]
a_big_int = Annotated[int, mapped_column(BigInteger, nullable=True)]
a_int = Annotated[int, mapped_column(Integer, nullable=True)]
a_str = Annotated[str, mapped_column(String(240), nullable=True)]
a_text = Annotated[str, mapped_column(Text, nullable=True)]
a_bool = Annotated[str, mapped_column(Boolean, nullable=True)]
a_json = Annotated[JSON, mapped_column(JSON, nullable=True)]
a_char = Annotated[str, mapped_column(CHAR(20), nullable=True)]
