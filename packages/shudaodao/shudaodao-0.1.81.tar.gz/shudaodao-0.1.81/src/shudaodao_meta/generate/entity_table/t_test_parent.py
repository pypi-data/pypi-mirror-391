#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：Shudaodao Auto Generator
# @Software ：PyCharm
# @Desc     ：SQLModel classes for shudaodao_meta.t_test_parent

from typing import Optional

from sqlalchemy import PrimaryKeyConstraint

from shudaodao_core import SQLModel, BaseResponse, Field, get_primary_id
from ...meta_config import MetaConfig


class TestParent(MetaConfig.RegistryModel, table=True):
    """数据库对象模型"""

    __tablename__ = "t_test_parent"
    __table_args__ = (
        PrimaryKeyConstraint("test_parent_id", "meta_schema_id"),
        {"schema": MetaConfig.SchemaTable},
    )
    __database_schema__ = MetaConfig.SchemaName  # 仅用于内部处理

    test_parent_id: int = Field(default_factory=get_primary_id, primary_key=True)
    meta_schema_id: int = Field(default_factory=get_primary_id, primary_key=True)
    test_parent_name: Optional[int] = Field(default=None, nullable=True)


class TestParentCreate(SQLModel):
    """前端创建模型 - 用于接口请求"""

    test_parent_name: Optional[int] = Field(default=None)


class TestParentUpdate(SQLModel):
    """前端更新模型 - 用于接口请求"""

    test_parent_id: Optional[int] = Field(default=None)
    meta_schema_id: Optional[int] = Field(default=None)
    test_parent_name: Optional[int] = Field(default=None)


class TestParentResponse(BaseResponse):
    """前端响应模型 - 用于接口响应"""

    __database_schema__ = MetaConfig.SchemaName  # 仅用于内部处理
    test_parent_id: int = Field()
    meta_schema_id: int = Field()
    test_parent_name: Optional[int] = Field(default=None)
