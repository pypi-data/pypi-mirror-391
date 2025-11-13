#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/11/9 下午8:38
# @Desc     ：

from typing import Optional

from fastapi import Path

from shudaodao_auth import AuthRouter
from shudaodao_meta.meta_config import MetaConfig
from ..services.generic_service_v1 import GenericServiceV1

generic_router = AuthRouter(
    prefix=f"/v1",
    db_config_name=MetaConfig.EngineName,
    tags=["通用接口 - 增删改查 v1 - 兼容 java 接口"],
)


@generic_router.post(path="/{schema_path}/{entity_path}", summary="创建 schema - table/view 的数据")
async def create_route(
        create_model: dict,
        schema_path: str = Path(description="数据库模式名称/别名"),
        entity_path: str = Path(description="数据库实体名称/别名"),
):
    return await GenericServiceV1.create(
        schema_path=schema_path, entity_path=entity_path,
        create_models=create_model,
    )


@generic_router.delete(
    path="/{schema_path}/{entity_path}/{primary_id}", summary="获取 schema - table/view 的数据")
async def delete_route(
        primary_id: Optional[int] = Path(description="主键ID值]"),
        schema_path: str = Path(description="数据库模式名称/别名"),
        entity_path: str = Path(description="数据库实体名称/别名"),
):
    return await GenericServiceV1.delete(
        schema_path=schema_path, entity_path=entity_path,
        primary_id=primary_id,
    )


@generic_router.put(
    path="/{schema_path}/{entity_path}/{primary_id}", summary="更新 schema - table/view 的数据")
@generic_router.patch(
    path="/{schema_path}/{entity_path}/{primary_id}", summary="更新 schema - table/view 的数据")
async def update_route(
        update_models: dict,
        primary_id: Optional[int] = Path(description="主键ID值,int或List[int]"),
        schema_path: str = Path(description="数据库模式名称/别名"),
        entity_path: str = Path(description="数据库实体名称/别名"),
):
    return await GenericServiceV1.update(
        schema_path=schema_path, entity_path=entity_path,
        primary_id=primary_id, update_models=update_models
    )


@generic_router.get(
    path="/{schema_path}/{entity_path}/{primary_id}", summary="获取 schema - table/view 的数据")
async def read_route(
        primary_id: Optional[int] = Path(description="主键ID值]"),
        schema_path: str = Path(description="数据库模式名称/别名"),
        entity_path: str = Path(description="数据库实体名称/别名"),
):
    return await GenericServiceV1.read(
        schema_path=schema_path, entity_path=entity_path,
        primary_id=primary_id
    )
