#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：Shudaodao Auto Generator
# @Software ：PyCharm
# @Desc     ：controller classes for shudaodao_enum.sys_enum_schema

"""
本模块通过 AuthController 工厂方法，为数据库表 `sys_enum_schema` 自动生成一套完整的、带权限控制的
restful CRUD+Q（创建、读取、更新、删除、查询）API 接口。
"""

from shudaodao_core import AuthController
from ..entity_table.sys_enum_schema import (
    EnumSchema, EnumSchemaResponse,
    EnumSchemaCreate, EnumSchemaUpdate
)
from ... import get_router_path, get_router_tags, get_engine_name

EnumSchema_Router = AuthController.create(
    # prefix=f"/v1/{get_router_path()}/sys_enum_schema",
    tags=get_router_tags(),
    db_config_name=get_engine_name(),  # 配置文件中的数据库连接名称
    router_path=get_router_path(),
    schema_name="shudaodao_enum",
    table_name="sys_enum_schema",
    # 模型设置: 数据库模型、创建模型、更新模型、响应模型
    model_class=EnumSchema,
    create_schema=EnumSchemaCreate,
    update_schema=EnumSchemaUpdate,
    response_schema=EnumSchemaResponse,
)
