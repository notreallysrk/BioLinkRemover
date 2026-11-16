"""Async MongoDB access layer with bounded connection pooling and indexes."""
from datetime import datetime
import logging

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("BioLinkRemover.Database")


class Database:
    def __init__(self, uri: str, db_name: str):
        if not uri:
            raise ValueError("MONGO_DB is missing. Set your MongoDB connection URI.")
        self.client = AsyncIOMotorClient(
            uri,
            maxPoolSize=50,
            minPoolSize=2,
            maxIdleTimeMS=60000,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            retryWrites=True,
        )
        self.db = self.client[db_name]
        self.users = self.db["users"]
        self.groups = self.db["groups"]
        self.restrictions = self.db["newuser_restrictions"]

    async def initialize(self):
        """Create indexes once at startup, before handlers begin using the DB."""
        await self.client.admin.command("ping")
        # Non-unique indexes are backward-compatible with existing databases
        # that may already contain duplicate legacy records.
        await self.users.create_index("user_id", name="user_id_idx")
        await self.groups.create_index("chat_id", name="chat_id_idx")
        await self.restrictions.create_index(
            [("chat_id", 1), ("user_id", 1)], name="restriction_chat_user_idx"
        )
        await self.restrictions.create_index("expires_at", name="restriction_expiry")
        logger.info("MongoDB connected; indexes verified.")

    @staticmethod
    def _now():
        return datetime.utcnow()

    async def close(self):
        self.client.close()

    async def add_user(self, user_id: int, username: str = None):
        now = self._now()
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "last_seen": now},
             "$setOnInsert": {"date_joined": now}},
            upsert=True,
        )

    async def get_all_user_ids(self) -> list[int]:
        return [doc["user_id"] async for doc in self.users.find(
            {"user_id": {"$exists": True}}, {"_id": 0, "user_id": 1}
        ).batch_size(1000)]

    async def add_group(self, chat_id: int, title: str = None):
        now = self._now()
        await self.groups.update_one(
            {"chat_id": chat_id},
            {"$set": {"title": title, "last_active": now},
             "$setOnInsert": {"punishment_mode": "mute", "approved_users": [], "date_added": now}},
            upsert=True,
        )

    async def get_group_config(self, chat_id: int) -> str:
        doc = await self.groups.find_one({"chat_id": chat_id}, {"_id": 0, "punishment_mode": 1})
        return doc.get("punishment_mode", "mute") if doc else "mute"

    async def set_group_config(self, chat_id: int, mode: str):
        await self.groups.update_one({"chat_id": chat_id}, {"$set": {"punishment_mode": mode}}, upsert=True)

    async def get_approved_users(self, chat_id: int) -> list[int]:
        doc = await self.groups.find_one({"chat_id": chat_id}, {"_id": 0, "approved_users": 1})
        return doc.get("approved_users", []) if doc else []

    async def approve_user(self, chat_id: int, user_id: int):
        await self.groups.update_one({"chat_id": chat_id}, {"$addToSet": {"approved_users": user_id}}, upsert=True)

    async def unapprove_user(self, chat_id: int, user_id: int):
        await self.groups.update_one({"chat_id": chat_id}, {"$pull": {"approved_users": user_id}}, upsert=True)

    async def unapprove_all(self, chat_id: int):
        await self.groups.update_one({"chat_id": chat_id}, {"$set": {"approved_users": []}}, upsert=True)

    async def get_all_group_ids(self) -> list[int]:
        return [doc["chat_id"] async for doc in self.groups.find(
            {"chat_id": {"$exists": True}}, {"_id": 0, "chat_id": 1}
        ).batch_size(1000)]

    async def get_stats(self) -> tuple[int, int]:
        from asyncio import gather
        users_count, groups_count = await gather(
            self.users.count_documents({}), self.groups.count_documents({})
        )
        return users_count, groups_count

    async def get_newuser_config(self, chat_id: int) -> dict:
        doc = await self.groups.find_one(
            {"chat_id": chat_id}, {"_id": 0, "newuser_enabled": 1, "newuser_duration": 1}
        )
        return {
            "enabled": bool(doc.get("newuser_enabled", False)) if doc else False,
            "duration": int(doc.get("newuser_duration", 86400)) if doc else 86400,
        }

    async def set_newuser_config(self, chat_id: int, enabled=None, duration=None):
        update = {}
        if enabled is not None:
            update["newuser_enabled"] = bool(enabled)
        if duration is not None:
            update["newuser_duration"] = int(duration)
        if update:
            await self.groups.update_one({"chat_id": chat_id}, {"$set": update}, upsert=True)

    async def add_newuser_restriction(self, chat_id: int, user_id: int, expires_at):
        await self.restrictions.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"chat_id": chat_id, "user_id": user_id, "expires_at": expires_at}},
            upsert=True,
        )

    async def get_active_newuser_restrictions(self, chat_id: int, now=None) -> list[dict]:
        now = now or self._now()
        return [doc async for doc in self.restrictions.find(
            {"chat_id": chat_id, "expires_at": {"$gt": now}},
            {"_id": 0, "user_id": 1, "expires_at": 1},
        ).batch_size(500)]

    async def remove_newuser_restriction(self, chat_id: int, user_id: int):
        await self.restrictions.delete_one({"chat_id": chat_id, "user_id": user_id})

    async def cleanup_newuser_restrictions(self):
        await self.restrictions.delete_many({"expires_at": {"$lte": self._now()}})
