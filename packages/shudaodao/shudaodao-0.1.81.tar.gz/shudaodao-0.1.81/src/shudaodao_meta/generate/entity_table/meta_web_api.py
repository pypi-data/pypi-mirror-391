#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：Shudaodao Auto Generator
# @Software ：PyCharm
# @Desc     ：SQLModel classes for shudaodao_meta.meta_web_api

from typing import Optional, TYPE_CHECKING

from sqlalchemy import BigInteger

from shudaodao_core import SQLModel, BaseResponse, Field, Relationship, get_primary_id
from ...meta_config import MetaConfig

if TYPE_CHECKING:
    from .meta_table import MetaTable
    from .meta_view import MetaView


class MetaWebApi(MetaConfig.RegistryModel, table=True):
    """数据库对象模型"""

    __tablename__ = "meta_web_api"
    __table_args__ = {"schema": MetaConfig.SchemaTable, "comment": "API接口"}
    __database_schema__ = MetaConfig.SchemaName  # 仅用于内部处理

    meta_web_api_id: int = Field(default_factory=get_primary_id, primary_key=True, sa_type=BigInteger)
    meta_table_id: Optional[int] = Field(
        default=None,
        foreign_key=f"{MetaConfig.SchemaForeignKey}meta_table.meta_table_id",
        ondelete="CASCADE",
        sa_type=BigInteger,
        nullable=True,
    )
    meta_view_id: Optional[int] = Field(
        default=None,
        foreign_key=f"{MetaConfig.SchemaForeignKey}meta_view.meta_view_id",
        ondelete="CASCADE",
        sa_type=BigInteger,
        nullable=True,
    )
    web_api_name: Optional[str] = Field(default=None, nullable=True, max_length=128, description="接口名称")
    router_path: Optional[int] = Field(default=None, nullable=True, description="路由路径")
    # 反向关系 - 父对象
    MetaTable: "MetaTable" = Relationship(back_populates="MetaWebApis")
    # 反向关系 - 父对象
    MetaView: "MetaView" = Relationship(back_populates="MetaWebApis")


class MetaWebApiCreate(SQLModel):
    """前端创建模型 - 用于接口请求"""

    meta_table_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    meta_view_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    web_api_name: Optional[str] = Field(default=None, max_length=128, description="接口名称")
    router_path: Optional[int] = Field(default=None, description="路由路径")


class MetaWebApiUpdate(SQLModel):
    """前端更新模型 - 用于接口请求"""

    meta_web_api_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    meta_table_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    meta_view_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    web_api_name: Optional[str] = Field(default=None, max_length=128, description="接口名称")
    router_path: Optional[int] = Field(default=None, description="路由路径")


class MetaWebApiResponse(BaseResponse):
    """前端响应模型 - 用于接口响应"""

    __database_schema__ = MetaConfig.SchemaName  # 仅用于内部处理
    meta_web_api_id: int = Field(sa_type=BigInteger)
    meta_table_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    meta_view_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    web_api_name: Optional[str] = Field(description="接口名称", default=None)
    router_path: Optional[int] = Field(description="路由路径", default=None)
