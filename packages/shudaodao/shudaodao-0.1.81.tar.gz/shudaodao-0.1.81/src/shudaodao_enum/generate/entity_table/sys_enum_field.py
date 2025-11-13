#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：Shudaodao Auto Generator
# @Software ：PyCharm
# @Desc     ：SQLModel classes for shudaodao_enum.sys_enum_field

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean

from shudaodao_core import Field, get_primary_id, Relationship
from shudaodao_core import SQLModel, BaseResponse
from ... import RegistryModel, get_table_schema, get_foreign_schema

if TYPE_CHECKING:
    from .sys_enum_schema import EnumSchema
    from .sys_enum_value import EnumValue


class EnumField(RegistryModel, table=True):
    """ 数据库对象模型 """
    __tablename__ = "sys_enum_field"
    __table_args__ = {"schema": get_table_schema(), "comment": "枚举字段表"}
    # 非数据库字段：仅用于内部处理
    __database_schema__ = "shudaodao_enum"
    # 数据库字段
    field_id: int = Field(
        default_factory=get_primary_id, primary_key=True, sa_type=BigInteger, description="主键"
    )
    schema_id: int = Field(
        sa_type=BigInteger, description="主键", foreign_key=f"{get_foreign_schema()}sys_enum_schema.schema_id"
    )
    field_label: str = Field(max_length=50, description="字段标签")
    field_name: str = Field(max_length=50, description="字段列名")
    description: Optional[str] = Field(default=None, max_length=500, nullable=True, description="描述")
    is_active: bool = Field(sa_type=Boolean, description="启用状态")
    sort_order: int = Field(default=10, description="排序权重")
    create_by: Optional[str] = Field(default=None, max_length=50, nullable=True, description="创建人")
    create_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now().replace(microsecond=0), nullable=True, description="创建日期"
    )
    update_by: Optional[str] = Field(default=None, max_length=50, nullable=True, description="修改人")
    update_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now().replace(microsecond=0), nullable=True, description="修改日期"
    )
    tenant_id: Optional[int] = Field(default=None, nullable=True, sa_type=BigInteger, description="主键")
    # 反向关系 -> 父对象
    Schema: "EnumSchema" = Relationship(back_populates="EnumFields")
    # 正向关系 -> 子对象
    EnumValues: list["EnumValue"] = Relationship(
        back_populates="Field", sa_relationship_kwargs={
            "order_by": "EnumValue.sort_order.asc()"
        }
    )


class EnumFieldBase(SQLModel):
    """ 创建、更新模型 共用字段 """
    schema_id: int = Field(sa_type=BigInteger, description="主键")
    field_label: str = Field(max_length=50, description="字段标签")
    field_name: str = Field(max_length=50, description="字段列名")
    description: Optional[str] = Field(default=None, max_length=500, description="描述")
    is_active: bool = Field(description="启用状态")
    sort_order: int = Field(default=10, description="排序权重")


class EnumFieldCreate(EnumFieldBase):
    """ 前端创建模型 - 用于接口请求 """
    ...


class EnumFieldUpdate(EnumFieldBase):
    """ 前端更新模型 - 用于接口请求 """
    ...


class EnumFieldResponse(BaseResponse):
    """ 前端响应模型 - 用于接口响应 """
    __database_schema__ = "shudaodao_enum"  # 仅用于内部处理

    field_id: int = Field(description="主键", sa_type=BigInteger)
    schema_id: int = Field(description="主键", sa_type=BigInteger)
    field_label: str = Field(description="字段标签")
    field_name: str = Field(description="字段列名")
    description: Optional[str] = Field(description="描述", default=None)
    is_active: bool = Field(description="启用状态")
    sort_order: int = Field(description="排序权重")
    create_by: Optional[str] = Field(description="创建人", default=None)
    create_at: Optional[datetime] = Field(description="创建日期", default=None)
    update_by: Optional[str] = Field(description="修改人", default=None)
    update_at: Optional[datetime] = Field(description="修改日期", default=None)
