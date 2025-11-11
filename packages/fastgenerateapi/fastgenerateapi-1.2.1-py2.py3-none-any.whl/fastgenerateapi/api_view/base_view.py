import time
import uuid
from copy import copy
from typing import Optional, Type, List, Union, Sequence, Dict
from urllib.parse import parse_qs

from fastapi import params
from tortoise.queryset import QuerySet

from pydantic import create_model, BaseModel
from starlette.requests import Request
from tortoise import Model

from fastgenerateapi.api_view.mixin.base_mixin import BaseMixin
from fastgenerateapi.api_view.mixin.dbmodel_mixin import DBModelMixin
from fastgenerateapi.api_view.mixin.response_mixin import ResponseMixin
from fastgenerateapi.api_view.mixin.tool_mixin import ToolMixin
from fastgenerateapi.schemas_factory import get_one_schema_factory, response_factory
from fastgenerateapi.settings.all_settings import settings
from fastgenerateapi.utils.exception import NOT_FOUND


class BaseView(BaseMixin, ResponseMixin, ToolMixin, DBModelMixin):

    prefix: Optional[str] = None  # 路由追加后缀
    model_class: Optional[Type[Model]] = None  # 数据库模型
    prefetch_related_fields: Union[None, dict] = None
    is_with_prefetch: Optional[bool] = False
    schema: Optional[Type[BaseModel]] = None  # 返回序列化[未使用]
    dependencies: Optional[Sequence[params.Depends]] = None
    tags: Optional[List[str]] = None  # swagger标签
    router_args: Dict[str, any] = None

    """
    # 增加外键字段显示
    prefetch_related_fields = {
          "avatar": None,           # 外键内容对应字典的形式
          "avatar": ["id", ("url", "avatar_url")]   # 增加 avatar_id,avatar_url2个字段
    }
    is_with_prefetch: 是否带有列表的prefetch_related_fields

    # router_args: List[Union[str, tuple, BaseRouterSummary]] = None
    # 给函数设置路由以及其他参数
    # key为方法名，例如："get_one", "view_get_data"
    router_args = {
        "get_one": {
            "response_model": CommonResponse;
            "summary": "备注",
            "dependencies": ["依赖函数"],
        }
        // 或者 "get_one": CommonResponse,
        // 或者 "get_one": "备注",
        // 或者 "get_one": ["依赖函数"],
    }
    """

    @property
    def queryset(self) -> QuerySet:
        if not self.model_class:
            return self.error(msg="model_class not allow None")

        return self.get_active_queryset(self.model_class)

    @staticmethod
    def get_active_queryset(model_class: Union[Type[Model], QuerySet, None] = None) -> QuerySet:
        if not model_class:
            raise ResponseMixin.error(f"model_class not allow None")
        delete_filter_dict = {settings.app_settings.WHETHER_DELETE_FIELD: True}
        if settings.app_settings.DELETE_FIELD_TYPE == "time":
            delete_filter_dict = {settings.app_settings.WHETHER_DELETE_FIELD: 0}
        queryset = model_class.filter(**delete_filter_dict)

        return queryset

    @property
    def relation_queryset(self) -> QuerySet:
        if not self.relation_model_class:
            return self.error(msg="relation_model_class not allow None")
        return self.get_active_queryset(self.relation_model_class)

    @classmethod
    async def get_object(cls, pk, model_class, is_with_prefetch=False):
        queryset = cls.get_active_queryset(model_class).filter(id=pk)
        if is_with_prefetch:
            queryset = queryset.prefetch_related(*cls.prefetch_related_fields.keys())
        model = await queryset.first()
        if model:
            return model
        else:
            raise NOT_FOUND

    @staticmethod
    def _delete_value():
        result = False
        if settings.app_settings.DELETE_FIELD_TYPE == "time":
            result = int(time.time() * 1000)
        return result

    @staticmethod
    async def delete_queryset(queryset: QuerySet):
        """
        考虑到不一定会集成已有的模型，删除根据是否存在字段来判断
        :param queryset:
        :return:
        """
        if settings.app_settings.WHETHER_DELETE_FIELD in queryset.fields:
            await queryset.update(**{
                settings.app_settings.WHETHER_DELETE_FIELD: BaseView._delete_value()
            })
        else:
            await queryset.delete()

    @staticmethod
    async def setattr_model(model: Model, prefetch_related_fields, *args, **kwargs) -> Model:
        for key, value_list in prefetch_related_fields.items():
            if value_list is None:
                continue
            if isinstance(value_list, str):
                value_list = [value_list]
            key_list = key.split("__")
            attr_model = copy(model)
            for attr_key in key_list:
                attr_model = getattr(attr_model, attr_key, None)

            if attr_model:
                if settings.app_settings.SCHEMAS_UNDERLINE_WHETHER_DOUBLE_TO_SINGLE:
                    key = key.replace("__", "_")
                for value in value_list:
                    if type(value) == str:
                        setattr(model, key + "_" + value, getattr(attr_model, value, None) if attr_model else None)
                    elif type(value) == tuple and len(value) == 2:
                        setattr(model, value[1], getattr(attr_model, value[0], None) if attr_model else None)
        return model

    @staticmethod
    async def getattr_model(model: Model, fields: List[Union[str, tuple]]) -> BaseModel:
        model_dict = {}
        model_fields = {}
        for field in fields:
            if type(field) == str:
                key_list = field.split("__")
                attr_model = copy(model)
                for attr_key in key_list:
                    attr_model = getattr(attr_model, attr_key, None)
                model_dict[field] = attr_model
                model_fields[field] = (type(attr_model), ...)
            if type(field) == tuple and len(field) == 2:
                key_list = field[0].split("__")
                attr_model = copy(model)
                for attr_key in key_list:
                    attr_model = getattr(attr_model, attr_key, None)
                model_dict[field[1]] = attr_model
                model_fields[field[1]] = (type(attr_model), ...)
        schema = create_model(
            f"{Model.__name__}{uuid.uuid4()}",
            **model_fields
        )
        return schema.model_validate(model_dict)

    @classmethod
    async def check_unique_field(
            cls,
            data_dict: dict,
            model_class: Type[Model],
            model: Union[Model, None] = None
    ):
        """
        校验模型中设置了 唯一索引和联合唯一索引 的字段
        :param data_dict: 修改或创建的数据字典
        :param model_class: 数据库模型
        :param model: 修改前的数据，用于判断是否修改了字段，当唯一字段与数据data_dict一致时，不会做校验
        :return:
        """
        check_unique_fields = cls._get_unique_fields(model_class)
        check_unique_together_fields = cls._get_unique_together_fields(model_class)
        for unique_field in check_unique_fields:
            if unique_field in data_dict:
                unique_field_value = data_dict.get(unique_field)
                if model and unique_field_value == getattr(model, unique_field):
                    continue
                if await model_class.filter(**{unique_field: unique_field_value}).first():
                    return cls.error(msg=f"{cls.get_field_description(model_class, unique_field)}已存在相同值：{unique_field_value}")
        for unique_together_fields in check_unique_together_fields:
            filter_fields = {}
            is_equal = True
            description_fields = []
            for unique_together_field in unique_together_fields:
                has_unique_together_field = unique_together_field in data_dict
                unique_together_field_value = data_dict.get(unique_together_field)
                if model:
                    if has_unique_together_field:
                        filter_fields[unique_together_field] = unique_together_field_value
                        if unique_together_field_value != getattr(model, unique_together_field):
                            is_equal = False
                            description_fields.append(unique_together_field)
                    else:
                        filter_fields[unique_together_field] = getattr(model, unique_together_field)
                else:
                    if has_unique_together_field:
                        is_equal = False
                        description_fields.append(unique_together_field)
                        filter_fields[unique_together_field] = unique_together_field_value
            if is_equal:
                continue

            if await model_class.filter(**filter_fields).first():
                if settings.app_settings.WHETHER_DELETE_FIELD in description_fields:
                    description_fields.remove(settings.app_settings.WHETHER_DELETE_FIELD)
                return cls.error(
                    msg=f"{cls.get_field_description(model_class, description_fields)}已存在相同值：{[filter_fields.get(field) for field in description_fields]}"
                )

    # @staticmethod
    # async def setattr_model_rpc(
    #         rpc_class,
    #         model: Model,
    #         rpc_param: Union[Dict[str, Dict[str, List[Union[str, tuple]]]], Type[RPCParam]],
    #         *args, **kwargs
    # ) -> Model:
    #     if rpc_class is None or not model or not rpc_param:
    #         return model
    #     if not isinstance(rpc_param, RPCParam):
    #         rpc_param = RPCParam(rpc_param, model)
    #     rpc_obj = rpc_class(**rpc_param.request_param)
    #     await rpc_obj.get_data()
    #     for base_rpc_param in rpc_param.data:
    #         setattr(
    #             model,
    #             base_rpc_param.response_field_alias_name,
    #             rpc_obj.filter(base_rpc_param.model_field_value).get(base_rpc_param.response_field_name))
    #     return model

    @staticmethod
    async def get_params(request: Request) -> dict:
        result = {}
        data = parse_qs(str(request.query_params), keep_blank_values=False)
        for key, val in data.items():
            result[key] = val[0]
        return result

    def gen_get_one_response_schema(self):
        if not hasattr(self, "get_one_schema") or not self.get_one_schema:
            get_one_schema_include = []
            if hasattr(self, "is_with_prefetch") and self.is_with_prefetch and self.prefetch_related_fields:
                for key, value in self.prefetch_related_fields.items():
                    if value and type(value) in [list, tuple, set]:
                        for val in value:
                            val_str = val
                            if type(val) in [list, tuple, set]:
                                val_str = val[0]
                            get_one_schema_include.append(key + "__" + val_str)
            self.get_one_schema = get_one_schema_factory(model_class=self.model_class, include=get_one_schema_include)

        return self.get_one_schema

    def gen_get_one_response_schema_factory(self):
        """
        如果get_one_response_schema不存在，则生成
        :return:
        """
        self.gen_get_one_response_schema()
        self.get_one_response_schema_factory = response_factory(self.get_one_schema, name="GetOne")

        return self.get_one_response_schema_factory



