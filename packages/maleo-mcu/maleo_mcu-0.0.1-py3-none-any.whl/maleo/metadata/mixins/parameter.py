from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeGuard
from uuid import UUID
from maleo.schemas.mixins.identity import Identifier
from maleo.types.float import OptFloat
from maleo.types.integer import OptInt
from maleo.types.string import OptStrT, OptStr
from ..enums.parameter import IdentifierType, ParameterGroup, ParameterType
from ..types.parameter import IdentifierValueType


class Key(BaseModel):
    key: str = Field(..., max_length=255, description="Parameter's key")


class Name(BaseModel, Generic[OptStrT]):
    name: OptStrT = Field(..., max_length=255, description="Parameter's name")


class Unit(BaseModel, Generic[OptStrT]):
    unit: OptStrT = Field(..., max_length=50, description="Parameter's unit")  # This should work now


class ParameterTypeMixin(BaseModel):
    parameter_type: ParameterType = Field(
        default=ParameterType.NUMERIC, description="Type of parameter"
    )


class ParameterGroupMixin(BaseModel):
    parameter_group: ParameterGroup = Field(
        ..., description="Group/category of parameter"
    )


class NormalRange(BaseModel):
    min_value: OptFloat = Field(None, description="Minimum normal value")
    max_value: OptFloat = Field(None, description="Maximum normal value")
    normal_text: OptStr = Field(None, description="Normal text value for categorical parameters")


class ParameterId(BaseModel):
    parameter_id: int = Field(..., ge=1, description="Parameter's id")


class ParentParameterId(BaseModel):
    parent_parameter_id: OptInt = Field(None, ge=1, description="Parent parameter's id")


class ParameterIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def column_and_value(self) -> tuple[str, IdentifierValueType]:
        return self.type.column, self.value


class IdParameterIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDParameterIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


class KeyParameterIdentifier(Identifier[Literal[IdentifierType.KEY], str]):
    type: Annotated[
        Literal[IdentifierType.KEY],
        Field(IdentifierType.KEY, description="Identifier's type"),
    ] = IdentifierType.KEY
    value: Annotated[str, Field(..., description="Identifier's value", max_length=255)]


class NameParameterIdentifier(Identifier[Literal[IdentifierType.NAME], str]):
    type: Annotated[
        Literal[IdentifierType.NAME],
        Field(IdentifierType.NAME, description="Identifier's type"),
    ] = IdentifierType.NAME
    value: Annotated[str, Field(..., description="Identifier's value", max_length=255)]


AnyParameterIdentifier = (
    ParameterIdentifier
    | IdParameterIdentifier
    | UUIDParameterIdentifier
    | KeyParameterIdentifier
    | NameParameterIdentifier
)


def is_id_identifier(
    identifier: AnyParameterIdentifier,
) -> TypeGuard[IdParameterIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyParameterIdentifier,
) -> TypeGuard[UUIDParameterIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)


def is_key_identifier(
    identifier: AnyParameterIdentifier,
) -> TypeGuard[KeyParameterIdentifier]:
    return identifier.type is IdentifierType.KEY and isinstance(identifier.value, str)


def is_name_identifier(
    identifier: AnyParameterIdentifier,
) -> TypeGuard[NameParameterIdentifier]:
    return identifier.type is IdentifierType.NAME and isinstance(identifier.value, str)