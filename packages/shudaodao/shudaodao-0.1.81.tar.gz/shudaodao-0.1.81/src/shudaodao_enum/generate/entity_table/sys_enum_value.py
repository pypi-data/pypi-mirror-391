#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：Shudaodao Auto Generator
# @Software ：PyCharm
# @Desc     ：SQLModel classes for shudaodao_enum.sys_enum_value

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean

from shudaodao_core import Field, get_primary_id, Relationship
from shudaodao_core import SQLModel, BaseResponse
from ... import RegistryModel, get_table_schema, get_foreign_schema

if TYPE_CHECKING:
    from .sys_enum_field import EnumField


class EnumValue(RegistryModel, table=True):
    """ 数据库对象模型 """
    __tablename__ = "sys_enum_value"
    __table_args__ = {"schema": get_table_schema(), "comment": "枚举值表"}
    # 非数据库字段：仅用于内部处理
    __database_schema__ = "shudaodao_enum"
    # 数据库字段
    enum_id: int = Field(
        default_factory=get_primary_id, primary_key=True, sa_type=BigInteger, description="主键"
    )
    field_id: int = Field(
        sa_type=BigInteger, description="主键", foreign_key=f"{get_foreign_schema()}sys_enum_field.field_id"
    )
    enum_pid: int = Field(default=-1, sa_type=BigInteger, description="上级枚举")
    enum_label: str = Field(max_length=50, description="枚举名")
    enum_value: str = Field(max_length=50, description="枚举值")
    enum_disabled: bool = Field(sa_type=Boolean, description="可选状态")
    is_active: bool = Field(sa_type=Boolean, description="启用状态")
    sort_order: int = Field(default=10, description="排序权重")
    description: Optional[str] = Field(default=None, max_length=500, nullable=True, description="描述")
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
    Field: "EnumField" = Relationship(back_populates="EnumValues")


class EnumValueBase(SQLModel):
    """ 创建、更新模型 共用字段 """
    field_id: int = Field(sa_type=BigInteger, description="主键")
    enum_pid: int = Field(default=-1, sa_type=BigInteger, description="上级枚举")
    enum_label: str = Field(max_length=50, description="枚举名")
    enum_value: str = Field(max_length=50, description="枚举值")
    enum_disabled: bool = Field(description="可选状态")
    is_active: bool = Field(description="启用状态")
    sort_order: int = Field(default=10, description="排序权重")
    description: Optional[str] = Field(default=None, max_length=500, description="描述")


class EnumValueCreate(EnumValueBase):
    """ 前端创建模型 - 用于接口请求 """
    ...


class EnumValueUpdate(EnumValueBase):
    """ 前端更新模型 - 用于接口请求 """
    ...


class EnumValueResponse(BaseResponse):
    """ 前端响应模型 - 用于接口响应 """
    __database_schema__ = "shudaodao_enum"  # 仅用于内部处理

    enum_id: int = Field(description="主键", sa_type=BigInteger)
    field_id: int = Field(description="主键", sa_type=BigInteger)
    enum_pid: int = Field(description="上级枚举", sa_type=BigInteger)
    enum_label: str = Field(description="枚举名")
    enum_value: str = Field(description="枚举值")
    enum_disabled: bool = Field(description="可选状态")
    is_active: bool = Field(description="启用状态")
    sort_order: int = Field(description="排序权重")
    description: Optional[str] = Field(description="描述", default=None)
    create_by: Optional[str] = Field(description="创建人", default=None)
    create_at: Optional[datetime] = Field(description="创建日期", default=None)
    update_by: Optional[str] = Field(description="修改人", default=None)
    update_at: Optional[datetime] = Field(description="修改日期", default=None)
