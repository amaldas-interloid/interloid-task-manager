import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_model import BaseModelMixin

if TYPE_CHECKING:
    from app.models.user import User


class Task(BaseModelMixin, Base):
    __tablename__ = "tasks"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Todo",
        index=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Medium",
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )

    owner: Mapped["User"] = relationship(
        back_populates="tasks",
    )