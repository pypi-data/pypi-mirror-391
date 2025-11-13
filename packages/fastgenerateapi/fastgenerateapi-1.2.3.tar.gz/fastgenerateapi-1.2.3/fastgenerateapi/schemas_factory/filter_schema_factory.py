from typing import Type, Union, Optional

from fastapi import Query
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from fastgenerateapi.pydantic_utils.base_model import model_config
from fastgenerateapi.api_view.mixin.dbmodel_mixin import DBModelMixin
from fastgenerateapi.controller.filter_controller import BaseFilter
from tortoise import Model

from fastgenerateapi.schemas_factory.common_function import get_validate_dict


def filter_schema_factory(model_class: Type[Model], fields: list[str, tuple[str, Type], BaseFilter] = None):
    """
        generate filter schema
    """
    model_fields = {}

    for field_info in fields or []:
        if not isinstance(field_info, BaseFilter):
            field_info = BaseFilter(field_info)
        f = field_info.filter_field
        t = field_info.field_type
        description = DBModelMixin.get_field_description(model_class, field_info.model_field)
        model_fields.update({
            f: (
                Optional[t],
                FieldInfo(
                    title=f"{description}",
                    default=Query("", description=description),
                    description=f"{description}"
                ))
        })

    filter_params_model: Type[BaseModel] = create_model(
        model_class.__name__+"CommonFilterParams",
        **model_fields,
        __config__=model_config,
        __validators__=get_validate_dict(),
    )

    return filter_params_model



