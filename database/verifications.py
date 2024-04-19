import asyncio
from models import Verification
from typing import List
from config import Config
from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticCollection


class Database:

    def __init__(self):
        self.__client = AsyncIOMotorClient(Config.DB_URI)
        self.db = self.__client[Config.DB_NAME]
        self.col: AgnosticCollection = self.db.verifications

    async def add_verification(self, verification: Verification):
        await self.col.insert_one(verification.model_dump())

    async def delete_verification(self, id):
        await self.col.delete_one({"id": id})

    async def get_verification(self, id):
        query = await self.col.find_one({"id": id})
        return Verification(**query) if query else None

    async def update_verification(self, id, **kwargs):
        await self.col.update_one({"id": id}, {"$set": kwargs})

    async def verifications_count(self, **kwargs):
        return await self.col.count_documents(kwargs)

    async def get_verifications_list(self, sort: bool = True, **kwargs) -> List[Verification]:
        if sort:
            return [Verification(**i) async for i in self.col.find(kwargs).sort("date", -1)]
        return [Verification(**i) async for i in self.col.find(kwargs)]


v = Database()
#  asyncio.get_event_loop().run_until_complete(v.col.drop())
