from pyrogram import Client
from pyrogram.enums import ChatMembersFilter
import config
import logging
import time
from Client.cache import GROUP_CONFIG_CACHE, APPROVED_USERS_CACHE, GROUP_ADMINS_CACHE

logger = logging.getLogger("BioLinkRemover.Helpers")
ADMIN_CACHE_TTL = 300


async def get_group_config(client: Client, chat_id: int) -> str:
    if chat_id not in GROUP_CONFIG_CACHE:
        try:
            GROUP_CONFIG_CACHE[chat_id] = await client.db.get_group_config(chat_id)
        except Exception:
            logger.exception("Could not load punishment mode for %s", chat_id)
            return "mute"
    return GROUP_CONFIG_CACHE[chat_id]


async def get_approved_users(client: Client, chat_id: int) -> set[int]:
    if chat_id not in APPROVED_USERS_CACHE:
        try:
            APPROVED_USERS_CACHE[chat_id] = set(await client.db.get_approved_users(chat_id))
        except Exception:
            logger.exception("Could not load approved users for %s", chat_id)
            return set()
    return APPROVED_USERS_CACHE[chat_id]


async def is_user_admin(client: Client, chat_id: int, user_id: int) -> bool:
    if user_id in config.SUDO_USERS:
        return True

    now = time.monotonic()
    cached = GROUP_ADMINS_CACHE.get(chat_id)
    if cached and now - cached[1] < ADMIN_CACHE_TTL:
        return user_id in cached[0]

    try:
        admins = {
            member.user.id
            async for member in client.get_chat_members(
                chat_id, filter=ChatMembersFilter.ADMINISTRATORS
            ) if member.user
        }
        GROUP_ADMINS_CACHE[chat_id] = (admins, now)
        return user_id in admins
    except Exception:
        logger.exception("Could not refresh admin cache for %s", chat_id)
        # Fail closed for privileged actions: API failure must not grant admin access.
        return False
