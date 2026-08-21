from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


# Import models so they are registered with Base.metadata
from app.models import RefreshToken, Task, User  # noqa: E402,F401
