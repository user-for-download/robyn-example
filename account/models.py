from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, String, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from config.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger,
                                    unique=True,
                                    primary_key=True,
                                    autoincrement=True,
                                    index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    file: Mapped[str] = mapped_column(String, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    privileged: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __str__(self):
        return f"u-{self.uuid} / id-{self.id} / e-{self.email}"

    def get_display_name(self) -> str:
        return self.name or ""

    def get_id(self) -> int:
        assert self.id
        return self.id

    def get_hashed_password(self) -> str:
        return self.password or ""
