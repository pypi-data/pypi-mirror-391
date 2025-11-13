from ..generate.entity_table.sys_enum_field import (
    EnumField as EnumField,
    EnumFieldResponse as EnumFieldResponse,
)
from ..generate.entity_table.sys_enum_schema import EnumSchema as EnumSchema
from ..schema.enum import EnumQueryRequest as EnumQueryRequest
from shudaodao_core import AsyncSession as AsyncSession

class EnumQueryService:
    @classmethod
    async def query_schema(cls, *, schema_name, db: AsyncSession): ...
    @classmethod
    async def query_field(
        cls, *, db: AsyncSession, schema_name, quest_request: EnumQueryRequest
    ): ...
