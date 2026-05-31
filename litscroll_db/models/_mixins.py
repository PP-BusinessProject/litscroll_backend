"""The module with the mixins for the mapped classes."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Self
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import UUID as sa_UUID
from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm.decl_api import declared_attr
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.functions import func, now
from sqlalchemy.sql.schema import CheckConstraint, Column, FetchedValue, Index
from sqlalchemy.sql.sqltypes import (
    Boolean,
    DateTime,
    Integer,
    SmallInteger,
    String,
)


if TYPE_CHECKING:
    pass


class Incremented(object):
    """Adds a unique identifier to an instance."""

    id: Mapped[int] = Column(
        Integer,
        CheckConstraint('id > 0'),
        FetchedValue(),
        autoincrement=True,
        primary_key=True,
    )


class Identified(object):
    """Adds a unique identifier to an instance."""

    @declared_attr
    def id(self: Self, /) -> Mapped[str]:
        return Column(
            String(63),
            CheckConstraint("id ~ '^(?![0-9]+$)(?!-)[a-z0-9-]{1,63}(?<!-)$'"),
            primary_key=True,
        )


class IdentifiedUUID(object):
    """Adds a unique identifier to an instance."""

    @declared_attr
    def id(self: Self, /) -> Mapped[UUID]:
        return Column(
            sa_UUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
            server_default=func.gen_random_uuid(),
        )


class Positioned(object):
    """Adds an active status switch to an instance."""

    @declared_attr
    def position(self: Self, /) -> Mapped[int]:
        """Return the active status of this instance."""
        return Column(
            SmallInteger,
            CheckConstraint('position > 0'),
            FetchedValue(),
            nullable=False,
        )


class Toggleable(object):
    """Adds an active status switch to an instance."""

    @declared_attr
    def active(self: Self, /) -> Mapped[bool]:
        """Return the active status of this instance."""
        return Column(
            Boolean(create_constraint=True),
            nullable=False,
            default=True,
        )


class Named(object):
    """Adds instance's name and description."""

    @declared_attr
    def name(self: Self, /) -> Mapped[str]:
        """Return the name of this instance."""
        return Column(
            String(255),
            CheckConstraint("name <> ''"),
            index=Index(None, text('lower(name)'), unique=True),
            nullable=False,
        )

    @declared_attr
    def description(self: Self, /) -> Mapped[Optional[str]]:
        """Return the optional description of this instance."""
        return Column(
            String(1023),
            CheckConstraint("description IS NULL OR description <> ''"),
        )


class FallbackNamed(object):
    """Adds instance's fallback name and description."""

    @declared_attr
    def fallback_name(self: Self, /) -> Mapped[str]:
        """Return the fallback name of this instance."""
        return Column(
            String(255),
            CheckConstraint("fallback_name <> ''"),
            index=Index(None, text('lower(fallback_name)'), unique=True),
            nullable=False,
        )

    @declared_attr
    def fallback_description(self: Self, /) -> Mapped[Optional[str]]:
        """Return the optional fallback description of this instance."""
        return Column(
            String(1023),
            CheckConstraint(
                "fallback_description IS NULL OR fallback_description <> ''"
            ),
        )

    def name(self: Self, locale_tag: str, /) -> str:
        """Return the name of this instance."""
        if not hasattr(self, 'localizations'):
            return self.fallback_name

        for localization in self.localizations:
            if locale_tag == localization.locale_tag:
                if localization.name:
                    return localization.name
                break
        return self.fallback_name

    def description(self: Self, locale_tag: str, /) -> Optional[str]:
        """Return the description of this instance."""
        if not hasattr(self, 'localizations'):
            return self.fallback_description

        for localization in self.localizations:
            if locale_tag == localization.locale_tag:
                if localization.description:
                    return localization.description
                break
        return self.fallback_description


class Timestamped(object):
    """Tracks timestamps when the instance was created and updated."""

    @declared_attr
    def created_at(self: Self, /) -> Mapped[datetime]:
        """Set the date and time when the instance was created."""
        return Column(
            DateTime(),
            nullable=False,
            default=lambda: datetime.now(),
            server_default=now(),
        )

    @declared_attr
    def updated_at(self: Self, /) -> Mapped[datetime]:
        """Set the date and time of the last time the instance was updated."""
        return Column(
            DateTime(),
            nullable=False,
            default=lambda: datetime.now(),
            server_default=now(),
            onupdate=lambda: datetime.now(),
            server_onupdate=FetchedValue(),
        )
