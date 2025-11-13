from ..meta.entity_class import EntityClass as EntityClass
from ..meta.service import GenericMetaService as GenericMetaService
from .generic_service import GenericService as GenericService

class GenericServiceV2(GenericService):
    @classmethod
    async def create(cls, create_models, entity_path, schema_path): ...
    @classmethod
    async def query(cls, *, schema_path, entity_path, query_request): ...
