from pydantic import BaseModel, Field
from typing import Generic, Literal, Sequence, Type, TypeVar, overload
from uuid import UUID
from maleo.enums.status import (
    DataStatus,
    ListOfDataStatuses,
    SimpleDataStatusMixin,
    FULL_DATA_STATUSES,
)
from maleo.schemas.mixins.filter import convert as convert_filter
from maleo.schemas.mixins.general import Codes, Order
from maleo.schemas.mixins.hierarchy import IsRoot, IsParent, IsChild, IsLeaf
from maleo.schemas.mixins.identity import (
    IdentifierMixin,
    DataIdentifier,
    Ids,
    UUIDs,
    ParentIds,
    Keys,
    Names,
)
from maleo.schemas.mixins.sort import convert as convert_sort
from maleo.schemas.mixins.timestamp import LifecycleTimestamp, DataTimestamp
from maleo.schemas.operation.enums import ResourceOperationStatusUpdateType
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from maleo.types.boolean import OptBool
from maleo.types.dict import StrToAnyDict
from maleo.types.float import OptFloat
from maleo.types.integer import OptInt, OptListOfInts
from maleo.types.string import OptListOfStrs, OptStr
from maleo.types.uuid import OptListOfUUIDs
from ..enums.parameter import IdentifierType, ParameterGroup, ParameterType
from ..mixins.parameter import (
    Key, Name, Unit, ParameterTypeMixin, ParameterGroupMixin, 
    NormalRange, ParentParameterId, ParameterIdentifier
)
from ..types.parameter import IdentifierValueType


class CreateData(
    Name[str],
    Key,
    Unit[str],
    ParameterTypeMixin,
    ParameterGroupMixin,
    NormalRange,
    Order[OptInt],
    ParentParameterId,
):
    description: OptStr = Field(None, max_length=1000, description="Parameter description")


class CreateDataMixin(BaseModel):
    data: CreateData = Field(..., description="Create data")


class CreateParameter(
    CreateDataMixin,
):
    pass


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    Names[OptListOfStrs],
    Keys[OptListOfStrs],
    Codes[OptListOfStrs],
    IsLeaf[OptBool],
    IsChild[OptBool],
    IsParent[OptBool],
    IsRoot[OptBool],
    ParentIds[OptListOfInts],
    UUIDs[OptListOfUUIDs],
    Ids[OptListOfInts],
):
    parameter_groups: list[ParameterGroup] | None = Field(
        None, description="Filter by parameter groups"
    )
    parameter_types: list[ParameterType] | None = Field(
        None, description="Filter by parameter types"
    )
    has_parent: OptBool = Field(None, description="Filter parameters that have parent")

    @property
    def _query_param_fields(self) -> set[str]:
        return {
            "ids",
            "uuids",
            "parent_ids",
            "is_root",
            "is_parent",
            "is_child",
            "is_leaf",
            "has_parent",
            "parameter_groups",
            "parameter_types",
            "statuses",
            "keys",
            "names",
            "search",
            "page",
            "limit",
            "granularity",
            "use_cache",
        }

    def to_query_params(self) -> StrToAnyDict:
        params = self.model_dump(
            mode="json", include=self._query_param_fields, exclude_none=True
        )
        params["filters"] = convert_filter(self.date_filters)
        params["sorts"] = convert_sort(self.sort_columns)
        params = {k: v for k, v in params.items()}
        return params


class ReadSingleParameter(BaseReadSingleParameter[ParameterIdentifier]):
    @classmethod
    def from_identifier(
        cls,
        identifier: ParameterIdentifier,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter":
        return cls(identifier=identifier, statuses=statuses, use_cache=use_cache)

    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.KEY, IdentifierType.NAME],
        identifier_value: str,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=ParameterIdentifier(
                type=identifier_type, value=identifier_value
            ),
            statuses=statuses,
            use_cache=use_cache,
        )

    def to_query_params(self) -> StrToAnyDict:
        return self.model_dump(
            mode="json", include={"statuses", "use_cache"}, exclude_none=True
        )


class FullUpdateData(
    Name[str],
    Unit[str],
    ParameterTypeMixin,
    ParameterGroupMixin,
    NormalRange,
    Order[OptInt],
    ParentParameterId,
):
    description: OptStr = Field(None, max_length=1000, description="Parameter description")


class PartialUpdateData(
    Name[OptStr],
    Unit[OptStr],
    Order[OptInt],
    ParentParameterId,
):
    parameter_type: ParameterType | None = Field(None, description="Type of parameter")
    parameter_group: ParameterGroup | None = Field(None, description="Group/category of parameter")
    min_value: OptFloat = Field(None, description="Minimum normal value")
    max_value: OptFloat = Field(None, description="Maximum normal value")
    normal_text: OptStr = Field(None, description="Normal text value")
    description: OptStr = Field(None, max_length=1000, description="Parameter description")


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    UpdateDataMixin[UpdateDataT],
    IdentifierMixin[ParameterIdentifier],
    Generic[UpdateDataT],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        data: UpdateDataT,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        data: UpdateDataT,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.KEY, IdentifierType.NAME],
        identifier_value: str,
        data: UpdateDataT,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
    ) -> "UpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
    ) -> "UpdateParameter":
        return cls(
            identifier=ParameterIdentifier(
                type=identifier_type, value=identifier_value
            ),
            data=data,
        )


class StatusUpdateParameter(
    BaseStatusUpdateParameter[ParameterIdentifier],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.KEY, IdentifierType.NAME],
        identifier_value: str,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter":
        return cls(
            identifier=ParameterIdentifier(
                type=identifier_type, value=identifier_value
            ),
            type=type,
        )


class DeleteSingleParameter(BaseDeleteSingleParameter[ParameterIdentifier]):
    @overload
    @classmethod
    def new(
        cls, identifier_type: Literal[IdentifierType.ID], identifier_value: int
    ) -> "DeleteSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls, identifier_type: Literal[IdentifierType.UUID], identifier_value: UUID
    ) -> "DeleteSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.KEY, IdentifierType.NAME],
        identifier_value: str,
    ) -> "DeleteSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls, identifier_type: IdentifierType, identifier_value: IdentifierValueType
    ) -> "DeleteSingleParameter": ...
    @classmethod
    def new(
        cls, identifier_type: IdentifierType, identifier_value: IdentifierValueType
    ) -> "DeleteSingleParameter":
        return cls(
            identifier=ParameterIdentifier(
                type=identifier_type, value=identifier_value
            )
        )


class BaseParameterSchema(
    Name[str],
    Key,
    Unit[str],
    ParameterTypeMixin,
    ParameterGroupMixin,
    NormalRange,
    Order[OptInt],
    ParentParameterId,
):
    description: OptStr = Field(None, max_length=1000, description="Parameter description")


class StandardParameterSchema(
    BaseParameterSchema,
    SimpleDataStatusMixin[DataStatus],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


OptStandardParameterSchema = StandardParameterSchema | None
ListOfStandardParameterSchemas = list[StandardParameterSchema]
SeqOfStandardParameterSchemas = Sequence[StandardParameterSchema]


class FullParameterSchema(
    BaseParameterSchema,
    SimpleDataStatusMixin[DataStatus],
    DataTimestamp,
    DataIdentifier,
):
    pass


OptFullParameterSchema = FullParameterSchema | None
ListOfFullParameterSchemas = list[FullParameterSchema]
SeqOfFullParameterSchemas = Sequence[FullParameterSchema]


AnyParameterSchemaType = Type[StandardParameterSchema] | Type[FullParameterSchema]


# Parameter Schemas
AnyParameterSchema = StandardParameterSchema | FullParameterSchema
ParameterSchemaT = TypeVar("ParameterSchemaT", bound=AnyParameterSchema)

OptAnyParameterSchema = AnyParameterSchema | None
# FIX: Define the missing type variable
OptParameterSchemaT = TypeVar("OptParameterSchemaT", bound=OptAnyParameterSchema)

ListOfAnyParameterSchemas = (
    ListOfStandardParameterSchemas | ListOfFullParameterSchemas
)
ListOfAnyParameterSchemasT = TypeVar(
    "ListOfAnyParameterSchemasT", bound=ListOfAnyParameterSchemas
)

OptListOfAnyParameterSchemas = ListOfAnyParameterSchemas | None
OptListOfAnyParameterSchemasT = TypeVar(
    "OptListOfAnyParameterSchemasT", bound=OptListOfAnyParameterSchemas
)


# FIX: Define the hierarchy schemas at the top level
class ChildParameterSchema(BaseModel):
    child: StandardParameterSchema = Field(..., description="Child parameter")


class ParentParameterSchema(BaseModel):
    parent: StandardParameterSchema = Field(..., description="Parent parameter")
    children: ListOfStandardParameterSchemas = Field(default=[], description="Child parameters")


class ParameterWithChildrenSchema(StandardParameterSchema):
    children: ListOfStandardParameterSchemas = Field(default=[], description="Child parameters")


class HierarchicalParameterSchema(StandardParameterSchema):
    """Extended schema specifically for hierarchical data"""
    children: ListOfStandardParameterSchemas = Field(
        default_factory=list, 
        description="Child parameters"
    )
    
class ParameterHierarchySchema(BaseModel):
    root_parameters: ListOfStandardParameterSchemas = Field(..., description="Root level parameters")
    total_count: int = Field(..., description="Total number of parameters")


# FIX: Correct the generic type parameters - use defined TypeVars
class SimpleParameterMixin(BaseModel, Generic[ParameterSchemaT]):
    parameter: ParameterSchemaT = Field(..., description="Parameter")


class FullParameterMixin(BaseModel, Generic[ParameterSchemaT]):
    parameter: ParameterSchemaT = Field(..., description="Parameter")


class SimpleParametersMixin(BaseModel, Generic[ListOfAnyParameterSchemasT]):
    parameters: ListOfAnyParameterSchemasT = Field(..., description="Parameters")


class FullParametersMixin(BaseModel, Generic[ListOfAnyParameterSchemasT]):
    parameters: ListOfAnyParameterSchemasT = Field(..., description="Parameters")
    

