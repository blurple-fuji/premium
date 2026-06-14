from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, DB_NAME
from bson import ObjectId

class PicsDB:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.start_pics
        self._cache = []
        self._id_cache = {}
        self._cache_initialized = False

    async def _init_cache(self):
        if not self._cache_initialized:
            cursor = self.col.find({})
            self._cache = []
            self._id_cache = {}
            async for doc in cursor:
                self._cache.append(doc["file_id"])
                self._id_cache[str(doc["_id"])] = doc["file_id"]
            self._cache_initialized = True

    async def add_pic(self, file_id: str):
        await self._init_cache()
        if file_id not in self._cache:
            res = await self.col.insert_one({"file_id": file_id})
            self._cache.append(file_id)
            self._id_cache[str(res.inserted_id)] = file_id

    async def get_all_pics(self) -> list:
        await self._init_cache()
        return self._cache

    async def get_all_pics_with_id(self) -> dict:
        await self._init_cache()
        return self._id_cache

    async def remove_pic_by_object_id(self, object_id: str):
        await self._init_cache()
        if object_id in self._id_cache:
            file_id = self._id_cache[object_id]
            await self.col.delete_one({"_id": ObjectId(object_id)})
            self._cache.remove(file_id)
            del self._id_cache[object_id]

pics_db = PicsDB(DB_URI, DB_NAME)
