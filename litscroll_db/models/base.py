from __future__ import annotations

from contextlib import suppress
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from json import dumps
from pathlib import Path
from re import findall
from typing import (
    Callable,
    ClassVar,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Self,
    Sequence,
    Tuple,
    Type,
    Union,
)
from uuid import UUID

from inflect import engine
from regex import IGNORECASE, search
from sqlalchemy.dialects.postgresql.ranges import Range
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import deferred, mapped_column
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm.decl_api import DeclarativeBase, declared_attr
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import (
    Column,
    PrimaryKeyConstraint,
    SchemaItem,
    Table,
)
from sqlalchemy.sql.selectable import Select

from ..utils.descriptors import cachedclassproperty
from ._types import TID


#
TableArgs = Sequence[Union[SchemaItem, Mapping[str, object]]]
Policies = Mapping[str, Mapping[str, Union[bool, str, Iterable[str]]]]
Permissions = Mapping[str, Mapping[str, Iterable[Column]]]
Events = Mapping[str, Union[str, Iterable[str]]]
Serializable = Union[
    Union[None, bool, int, float, Decimal, str],
    Union[List['Serializable'], Mapping[str, 'Serializable']],
]


def serialize(
    value: object,
    /,
    checked: Iterable[BaseInterface] = (),
    *,
    encoding: str = 'utf8',
    relationships: bool = True,
) -> Serializable:
    if isinstance(value, BaseInterface):
        state: InstanceState = inspect(value)
        serialized = {c.key: state.dict.get(c.key) for c in value.columns}
        for relationship in value.relationships if relationships else ():
            _def = [] if relationship.property.uselist else None
            if (_value := state.dict.get(relationship.key, _def)) in checked:
                _value = None
            elif isinstance(_value, list):
                for checked_model in checked:
                    while checked_model in _value:
                        _value.remove(checked_model)
            serialized[relationship.key] = _value
        return serialize(serialized, (*checked, value))
    elif isinstance(value, (type(None), bytes, bool, int, float, str)):
        return value
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, (UUID, Range)):
        return str(value)
    elif isinstance(value, timedelta):
        return value.total_seconds()
    elif isinstance(value, (date, time, datetime)):
        return value.isoformat()
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, Callable):
        return f'{value.__module__}.{value.__name__}'
    elif isinstance(value, dict):
        return {
            serialize(k, checked): serialize(v, checked)
            for k, v in value.items()
        }
    elif isinstance(value, Iterable):
        return [serialize(_, checked) for _ in value]
    else:
        raise TypeError(f'Unserializable type "{type(value)}": {value}')


class BaseInterface(object):
    """The base class for all :module:`SQLAlchemy` models."""

    _inflect: ClassVar[engine] = engine()

    __allow_unmapped__: ClassVar[Optional[bool]] = True
    __is_materialized__: ClassVar[Optional[bool]] = None
    __is_materialized_concurrently__: ClassVar[Optional[bool]] = None
    __materialized_refresh_cron__: ClassVar[Optional[str]] = None
    __is_materialized_depending_on__: ClassVar[
        Optional[Sequence[Type[Self]]]
    ] = None
    __selectable__: ClassVar[Optional[Select]] = None

    __table_args__: ClassVar[Optional[TableArgs]] = None
    __policies__: ClassVar[Optional[Policies]] = None
    __permissions__: ClassVar[Optional[Permissions]] = None
    __events__: ClassVar[Optional[Events]] = None
    __instances__: ClassVar[Optional[Iterable[Self]]] = None
    __mapper_args__: ClassVar[Optional[Mapping[str, object]]] = dict(
        eager_defaults=True
    )

    STORAGE_PATH: ClassVar[Path] = Path('assets', 'storage')
    LOCALIZATIONS_PATH: ClassVar[Path] = Path('assets', 'localizations')

    @declared_attr
    def ctid(cls: Type[Self], /) -> Mapped[Tuple[int, int]]:
        return deferred(
            mapped_column(
                TID,
                nullable=False,
                system=True,
                server_default=text('DEFAULT'),
            )
        )

    @cachedclassproperty
    def __table__(cls: Type[Self], /) -> Table:
        if cls.__selectable__ is None:
            raise ValueError('No selected for table creation present.')

        columns: Iterable[Column] = cls.__selectable__.selected_columns
        args = [
            Column(c.name, c.type, primary_key=c.primary_key) for c in columns
        ]
        kwargs = {}
        for arg in cls.__table_args__:
            if isinstance(arg, Mapping):
                kwargs |= arg
            else:
                args.append(arg)
        if 'schema' not in kwargs or not kwargs['schema']:
            kwargs['schema'] = 'public'
        table = Table(cls.__tablename__, Base.metadata, *args, **kwargs)
        if not any(c.primary_key for c in columns):
            table.append_constraint(
                PrimaryKeyConstraint(*[c.name for c in columns])
            )
        return table

    @cachedclassproperty
    def __tablename__(cls: Type[Self], /) -> str:
        words = findall(r'[A-Z]+[^A-Z]*', cls.__name__.removesuffix('Model'))
        words.append(cls._inflect.plural(words.pop().lower()))
        return '_'.join(word.lower() for word in words)

    @classmethod
    def from_other(cls: Type[Self], other: object, /) -> Self:
        return cls(
            **{
                column.key: getattr(other, column.key)
                for column in cls.columns
            }
        )

    @classmethod
    def from_previous_state(cls: Type[Self], state: InstanceState, /) -> Self:
        return cls(
            **{
                prop.key: next(
                    iter(getattr(state.attrs, prop.key).history.deleted or ()),
                    getattr(state.attrs, prop.key).value,
                )
                for prop in state.mapper.iterate_properties
                if isinstance(prop, ColumnProperty)
            }
        )

    @cachedclassproperty
    def columns(cls: Type[Self], /) -> Iterable[InstrumentedAttribute]:
        return [
            (
                column.fget(cls)
                if isinstance(column, declared_attr)
                else column.expression
            )
            for key, column in cls.__dict__.items()
            if not key.startswith('_')
            and (
                isinstance(column, declared_attr)
                or isinstance(column, InstrumentedAttribute)
                and isinstance(column.expression, Column)
            )
        ]

    @cachedclassproperty
    def column_types(cls: Type[Self], /) -> Dict[Column, Type[object]]:
        column_types: Dict[Column, Type[object]] = {}
        for column in cls.columns:
            if getattr(getattr(column.type, 'impl', None), 'python_type', ''):
                column_types[column] = column.type.impl.python_type
            elif getattr(column.type, 'python_type', None):
                column_types[column] = column.type.python_type
            else:
                raise ValueError(f'Could not infer python type for {column}')
        return column_types

    @cachedclassproperty
    def relationships(cls: Type[Self], /) -> Iterable[InstrumentedAttribute]:
        return [
            column
            for key, column in cls.__dict__.items()
            if not key.startswith('_')
            and isinstance(column, InstrumentedAttribute)
            and not isinstance(column.expression, Column)
        ]

    @cachedclassproperty
    def relationship_types(
        cls: Type[Self],
        /,
    ) -> Dict[RelationshipProperty, Type[Base]]:
        relationship_types: Dict[Column, Type[object]] = {}
        for relationship in cls.relationships:
            if getattr(getattr(relationship, 'entity', None), 'class_', None):
                relationship_types[relationship] = relationship.entity.class_
            elif getattr(relationship, 'argument', None):
                with suppress(NameError):
                    relationship_types[relationship] = eval(
                        relationship.argument
                    )
                    continue
            raise ValueError(f'Could not infer type for {relationship}')
        return relationship_types

    @property
    def dict(self: Self, /) -> Dict[str, object]:
        return {_.key: self.__dict__.get(_.key) for _ in self.columns} | {
            _.key: self.__dict__.get(_.key) for _ in self.relationships
        }

    def json(
        self: Self,
        /,
        *,
        relationships: bool = False,
    ) -> Dict[str, Serializable]:
        return serialize(self, relationships=relationships)

    def __str__(
        self: Self,
        /,
        *,
        relationships: bool = False,
    ) -> str:
        return dumps(
            self.json(relationships=relationships),
            ensure_ascii=False,
            indent=2,
        )

    def __repr__(self: Self, /) -> str:
        return f'{self.__class__.__name__}(%s)' % ', '.join(
            f'{key}={repr(value)}'
            for key, value in self.json().items()
            if value is not None
        )

    @classmethod
    def cron(
        cls: Type[Self],
        /,
        name: str,
        body: str,
        cron: str = '* * * * *',
    ) -> Iterable[str]:
        _cron = []
        if search(r'\bBEGIN\b', body, IGNORECASE):
            _cron.append(
                f'CREATE OR REPLACE FUNCTION {cls.__table__.schema}.{name}() AS ${name}$ {body} ${name}$ LANGUAGE plpgsql;',
            )
            body = f"'CALL {cls.__table__.schema}.{name}()'"
        else:
            body = f'$${body.rstrip(";")}$$'
        _cron.append(f"SELECT cron.schedule('{name}', '{cron}', {body});")
        return tuple(_cron)

    @classmethod
    def trigger(
        cls: Type[Self],
        /,
        name: str,
        body: str,
        comment: Optional[str] = None,
        *,
        scope: str = 'ROW',
        before: bool = True,
        insert: bool = True,
        update: bool = True,
        delete: bool = False,
    ) -> Iterable[str]:
        if not (insert or update or delete):
            raise RuntimeError(
                'At least one of the `INSERT`, `UPDATE`, `DELETE` should be specified!'
            )
        before = 'BEFORE' if before else 'AFTER'
        event = ' OR '.join(
            _
            for _ in (
                'INSERT' if insert else '',
                'UPDATE' if update else '',
                'DELETE' if delete else '',
            )
            if _
        )
        return (
            f"""
CREATE OR REPLACE FUNCTION {cls.__table__.schema}.{name}()
RETURNS TRIGGER AS ${name}$
    {body}
${name}$ LANGUAGE plpgsql;
""",
            f"""
CREATE OR REPLACE TRIGGER {name} {before} {event}
ON {cls.__table__.fullname} FOR EACH {scope}
EXECUTE FUNCTION {cls.__table__.schema}.{name}();
""",
            *(
                (
                    f"COMMENT ON FUNCTION {cls.__table__.schema}.{name} IS '{comment}';",
                    f'COMMENT ON TRIGGER {name} ON '
                    f"{cls.__table__.fullname} IS '{comment}';",
                )
                if comment
                else ()
            ),
        )


class Base(BaseInterface, DeclarativeBase):
    pass
