import time
from typing import Type, Optional, Union, List

from pydantic.fields import FieldInfo
from tortoise import Model
from pydantic import create_model

from fastgenerateapi.data_type.data_type import T
from fastgenerateapi.pydantic_utils.base_model import model_config
from fastgenerateapi.schemas_factory.common_function import get_dict_from_model_fields, get_dict_from_pydanticmeta
from fastgenerateapi.settings.all_settings import settings


def hasattr_get_all_schema(model_class: Type[Model],):
    if not hasattr(model_class, "PydanticMeta"):
        return False
    if hasattr(model_class.PydanticMeta, "get_all_include") or hasattr(model_class.PydanticMeta, "get_all_exclude"):
        return True
    return False

def get_all_schema_factory(
        model_class: Type[Model],
        include: Union[list, tuple, set] = None,
        extra_include: Union[list, tuple, set] = None,
        exclude: Union[list, tuple, set] = None,
        name: Optional[str] = None,
) -> Optional[Type[T]]:
    """
    Is used to create a GetAllSchema
    固定排除 逻辑删除字段
    会默认添加模型下 PydanticMeta 设置的相关属性
    - include: 增改详情列表通用，指定包含字段，不指定默认包含所有字段
    - exclude： 增改详情列表通用，指定排除字段
    - get_include: 详情列表通用，额外添加字段
    - get_exclude: 详情列表通用，指定排除字段
    - get_all_include: 详情使用，额外添加字段
    - get_all_exclude: 详情使用，指定排除字段

    逻辑顺序：合并所有include和exclude，排除include下包含的exclude字段

    参数类型可选
    - include类型：
        - 字符串：【模型存在字段】自动生成，【模型不存在字段】默认字符串类型，无注释
        - 2个值：
            - (字符串, 类型int): 指定导出类型
            - (字符串, FieldInfo()):
            - (字符串1, 字符串2): 导出字段重命名。例如 ("name", "export_name")
        - 3个值：
            - (字符串1, 字符串2, 类型int):
            - (字符串, 字符串2, FieldInfo()):
            - (字符串, 类型int, FieldInfo()):
        - 4个值：
            - (字符串1, 字符串2, 类型int, FieldInfo()):
    - exclude类型：仅字符串

    示例：
    class model_class:
        ...

        PydanticMeta:
            include = []
            exclude = []
            get_include = [
                ("name", "export_name"),
                ("item_id_list", List[str], FieldInfo(description="多对多关联id列表")),
            ]
            get_exclude = ["hide_field"]
            get_all_include = [
                ("item_names", str, FieldInfo(description="多对多关联名称集合"))
            ]
            get_all_exclude = []
    """
    all_fields_info = get_dict_from_model_fields(model_class)

    include_fields = set()
    exclude_fields = set()
    if hasattr(model_class, "PydanticMeta"):
        if hasattr(model_class.PydanticMeta, "include"):
            include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.include)
            all_fields_info.update(include_fields_dict)
            include_fields.update(include_fields_dict.keys())
        else:
            include_fields.update(all_fields_info.keys())
        if hasattr(model_class.PydanticMeta, "exclude"):
            exclude_fields.update(model_class.PydanticMeta.exclude)

        if hasattr(model_class.PydanticMeta, "get_include"):
            get_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.get_include)
            all_fields_info.update(get_include_fields_dict)
            include_fields.update(get_include_fields_dict.keys())
        if hasattr(model_class.PydanticMeta, "get_exclude"):
            exclude_fields.update(model_class.PydanticMeta.get_exclude)

        # get_all_include
        if hasattr(model_class.PydanticMeta, "get_all_include"):
            get_all_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.get_all_include)
            all_fields_info.update(get_all_include_fields_dict)
            include_fields.update(get_all_include_fields_dict.keys())
        # get_all_exclude
        if hasattr(model_class.PydanticMeta, "get_all_exclude"):
            exclude_fields.update(model_class.PydanticMeta.get_all_exclude)
    else:
        include_fields.update(all_fields_info.keys())

    # 参数处理
    if include:
        include_fields_dict = get_dict_from_pydanticmeta(model_class, include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    if extra_include:
        include_fields_dict = get_dict_from_pydanticmeta(model_class, extra_include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    if exclude:
        exclude_fields.update(exclude)

    all_fields = include_fields.difference(exclude_fields)
    if settings.app_settings.GET_EXCLUDE_ACTIVE_VALUE:
        try:
            all_fields.remove(settings.app_settings.WHETHER_DELETE_FIELD)
        except Exception:
            ...

    schema_name = name if name else model_class.__name__ + "GetAllSchema"
    schema: Type[T] = create_model(
        schema_name, **{field: all_fields_info[field] for field in all_fields}, __config__=model_config)
    return schema


def get_list_schema_factory(schema_cls: Type[T] = None, name: str = "") -> Type[T]:
    if schema_cls:
        fields = {
            settings.app_settings.LIST_RESPONSE_FIELD: (Optional[List[schema_cls]], FieldInfo(default=[], description="数据返回")),
        }
        name = schema_cls.__name__ + name + "GetListSchema"
    else:
        fields = {
            settings.app_settings.LIST_RESPONSE_FIELD: (Optional[List], FieldInfo(default=[], description="数据返回")),
        }
        name = name + "GetListSchema"
    schema: Type[T] = create_model(name, **fields, __config__=model_config)
    return schema


def get_page_schema_factory(schema_cls: Type[T] = None, name: str = "") -> Type[T]:
    fields = {
        settings.app_settings.CURRENT_PAGE_FIELD: (Optional[int], FieldInfo(default=1, description="当前页")),
        settings.app_settings.PAGE_SIZE_FIELD: (Optional[int], FieldInfo(default=settings.app_settings.DEFAULT_PAGE_SIZE, description="每页数量")),
        settings.app_settings.TOTAL_SIZE_FIELD: (Optional[int], FieldInfo(default=0, description="数量总计")),
    }
    if schema_cls:
        fields.update({settings.app_settings.LIST_RESPONSE_FIELD: (Optional[List[schema_cls]], FieldInfo(default=[], description="数据返回"))})
        name = schema_cls.__name__ + name + "GetPageSchema"
    else:
        fields.update({settings.app_settings.LIST_RESPONSE_FIELD: (Optional[List], FieldInfo(default=[], description="数据返回"))})
        name = name + "GetPageSchema"
    schema: Type[T] = create_model(name, **fields, __config__=model_config)
    return schema






