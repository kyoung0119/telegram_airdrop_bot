import asyncio
from models import User
from typing import List
from config import Config
from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticCollection


class Database:

    def __init__(self):
        self.__client = AsyncIOMotorClient(Config.DB_URI)
        self.db = self.__client[Config.DB_NAME]
        self.col: AgnosticCollection = self.db.users

    async def is_user_exits(self, id):
        return await self.col.find_one({"id": id})

    async def add_user(self, user: User):
        await self.col.insert_one(user.model_dump())

    async def delete_user(self, id):
        await self.col.delete_one({"id": id})

    async def get_user(self, id):
        query = await self.col.find_one({"id": id})
        return User(**query) if query else None

    async def update_user(self, id, **kwargs):
        await self.col.update_one({"id": id}, {"$set": kwargs})

    async def get_users_list(self, sort: bool = True, **kwargs) -> List[User]:
        if sort:
            return [User(**i) async for i in self.col.find(kwargs).sort("balance", -1)]
        return [User(**i) async for i in self.col.find(kwargs)]

    async def users_count(self, **kwargs):
        return await self.col.count_documents(kwargs)

    async def add_invited(self, id, invited):
        await self.col.update_one({"id": id}, {"$push": {"invited_users": invited}})

    async def add_balance(self, id, amount):
        await self.col.update_one({"id": id}, {"$inc": {"balance": amount}})

    async def remove_balance(self, id, amount):
        await self.col.update_one({"id": id}, {"$inc": {"balance": -amount}})


db = Database()
