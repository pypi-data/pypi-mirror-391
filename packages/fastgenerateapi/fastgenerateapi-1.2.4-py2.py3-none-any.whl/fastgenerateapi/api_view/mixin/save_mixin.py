from tortoise import Model

from fastgenerateapi.pydantic_utils.base_model import BaseModel


class SaveMixin:

    async def set_save_fields(self, data_dict: dict, request_data, *args, **kwargs) -> dict:
        """
        添加属性: data_dict['user_id'] = current_user.id
        kwargs 包含 request_data
        """

        return data_dict


