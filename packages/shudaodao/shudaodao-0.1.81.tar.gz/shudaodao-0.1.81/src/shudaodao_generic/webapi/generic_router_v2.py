#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/11/9 下午8:38
# @Desc     ：

from typing import Union, List

from fastapi import Path

from shudaodao_auth import AuthRouter
from shudaodao_core import QueryRequest
from shudaodao_meta.meta_config import MetaConfig
from ..services.generic_service_v2 import GenericServiceV2

generic_router = AuthRouter(
    prefix=f"/v2",
    db_config_name=MetaConfig.EngineName,
    tags=["通用接口 - 增删改查 v2 - 只支持 python"],
)


@generic_router.post(path="/{schema_path}/{entity_path}", summary="创建 schema - table/view 的数据，支持list")
async def create_route(
        create_models: Union[dict, List[dict]],
        schema_path: str = Path(description="数据库模式名称/别名"),
        entity_path: str = Path(description="数据库实体名称/别名"),
):
    return await GenericServiceV2.create(
        schema_path=schema_path, entity_path=entity_path,
        create_models=create_models,
    )


# @generic_router.patch(
#     path="/{schema_path}/{entity_path}", summary="更新 schema - table/view 的数据 支持list")
# async def update_route(
#         update_models: Union[dict, List[dict]],
#         schema_path: str = Path( description="数据库模式名称/别名"),
#         entity_path: str = Path( description="数据库实体名称/别名"),
# ):
#     entity_class: EntityClass = GenericMetaService().get_metadata(schema_path, entity_path)
#     update_model_list = await get_model_list(update_models, entity_class.update_class)
#     update_result = []
#     async with AsyncSessionService().get_session(entity_class.engine_name) as db:
#         for update_model in update_model_list:
#             update_result.append(await DataService.update(
#                 db,
#                 primary_id=getattr(update_model, entity_class.model_class.__primary_key__),
#                 model_class=entity_class.model_class,
#                 update_model=update_model,
#                 response_class=entity_class.response_class,
#             ))
#         result_len = len(update_result)
#         return ResponseUtil.success(
#             data=update_result[0] if result_len == 1 else update_result,
#             message="更新成功" if result_len == 1 else f"更新成功, 共{result_len}条"
#         )


@generic_router.post(path="/{schema_path}/{entity_path}/query", summary="查询 schema - table/view 的数据，支持关系查询")
async def query_route(
        query_request: QueryRequest,
        schema_path: str = Path(description="数据库模式名称/别名"),
        entity_path: str = Path(description="数据库实体名称/别名"),
):
    return await GenericServiceV2.query(
        schema_path=schema_path, entity_path=entity_path,
        query_request=query_request,
    )
