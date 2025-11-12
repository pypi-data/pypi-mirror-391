from typing import Literal, Type, overload, List
from ..schemas.parameter import (
    StandardParameterSchema,
    FullParameterSchema,
    AnyParameterSchemaType,
    ParameterHierarchySchema,
)
from ..enums.parameter import Granularity


@overload
def get_schema_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardParameterSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullParameterSchema]: ...
@overload
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnyParameterSchemaType: ...
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnyParameterSchemaType:
    if granularity is Granularity.STANDARD:
        return StandardParameterSchema
    elif granularity is Granularity.FULL:
        return FullParameterSchema


def create_parameter_hierarchy(parameters: List[StandardParameterSchema]) -> ParameterHierarchySchema:
    """
    Create hierarchical structure using specialized schema
    """
    from ..schemas.parameter import HierarchicalParameterSchema
    
    hierarchical_params = [
        HierarchicalParameterSchema.model_validate({**param.model_dump(), 'children': []})
        for param in parameters
    ]
    
    param_dict = {param.id: param for param in hierarchical_params}
    root_parameters = []
    
    for param in hierarchical_params:
        if param.parent_parameter_id and param.parent_parameter_id in param_dict:
            parent = param_dict[param.parent_parameter_id]
            parent.children.append(param)
        else:
            root_parameters.append(param)
    
    return ParameterHierarchySchema(
        root_parameters=root_parameters,
        total_count=len(parameters)
    )


def create_parameter_hierarchy_simple(parameters: List[StandardParameterSchema]) -> ParameterHierarchySchema:
    """
    Create hierarchical structure from flat list of parameters (simpler version)
    """
    parameter_dict = {param.id: param for param in parameters}
    root_parameters = []
    
    # First pass: identify root parameters
    for param in parameters:
        if not hasattr(param, 'parent_parameter_id') or not param.parent_parameter_id:
            root_parameters.append(param)
    
    return ParameterHierarchySchema(
        root_parameters=root_parameters,
        total_count=len(parameters)
    )