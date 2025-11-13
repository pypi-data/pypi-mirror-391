#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技


from sqlalchemy.orm import registry
from sqlmodel import SQLModel

from shudaodao_core import DatabaseEngine, RunningConfig

shudaodao_enum_registry = registry()


class RegistryModel(SQLModel, registry=shudaodao_enum_registry):
    ...


# 用于 Controller 
def get_engine_name():
    return RunningConfig.get_engine_name("Enum", "shudaodao_enum")


# noinspection DuplicatedCode
setattr(shudaodao_enum_registry, "engine_name", get_engine_name())


# 用于 Controller 
def get_router_path():
    return RunningConfig.get_router_path("shudaodao_enum")


# 用于 Controller
def get_router_tags():
    return ["通用功能 - 枚举管理"]


# SQLModel 类: __table_args__ = {"schema": "用于这里"}
def get_table_schema():
    if DatabaseEngine().support_schema(name=get_engine_name()):
        return RunningConfig.get_sqlmodel_schema("shudaodao_enum")
    return None


# SQLModel 类: foreign_key= 用于这里 -> schema_name.t_table_name.field_id"
def get_foreign_schema():
    table_schema = get_table_schema()
    return table_schema + "." if table_schema else ""
