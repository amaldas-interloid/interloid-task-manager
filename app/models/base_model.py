from app.models.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class BaseModelMixin(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    pass
