"""Chain Of Thought Service - Pre-configured AssetService for CRUD operations only"""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Optional
from ..asset_service import AssetService, CacheConfig
from ..collections.chain_of_thought_collection import ChainOfThoughtCollection
from ....models.company.assets.ai_agents_v2.chain_of_thought_in_chat import ChainOfThoughtInChat
from ....models.data_base.mongo_connection import MongoConnection
from ....models.utils.types.identifier import StrObjectId
from ....models.utils.types.serializer_type import SerializerType
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ChainOfThoughtService(AssetService[ChainOfThoughtInChat, ChainOfThoughtInChat]):
    """
    Pre-configured service for Chain Of Thought CRUD operations.

    For business logic operations (create for N8N, set as failed, etc.),
    use ChainOfThoughtsEditor instead.

    No events needed - this is execution state, not a business asset.
    """

    def __init__(
        self,
        connection: MongoConnection,
        cache_config: CacheConfig = CacheConfig(
            keep_items_always_in_memory=False,
            keep_previews_always_in_memory=False
        )
    ):
        collection = ChainOfThoughtCollection(connection)
        super().__init__(
            collection=collection,
            cache_config=cache_config
        )

    async def get_by_chat_id(self, chat_id: StrObjectId, skip: int = 0, limit: int = 10) -> List[ChainOfThoughtInChat]:
        """Get chain of thoughts by chat ID"""
        cot_docs = await self.collection.async_collection.find({"chat_id": chat_id}).sort("created_at", -1).skip(skip).limit(limit)
        return [self.collection.create_instance(cot_doc).model_dump_json(serializer=SerializerType.FRONTEND) for cot_doc in cot_docs]
