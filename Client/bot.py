import asyncio
import logging
from pyrogram import Client
import config
from Client.database import Database
from Client.cache import USER_IDS_CACHE, GROUP_IDS_CACHE

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("BioLinkRemover")


class BioLinkBot(Client):
    def __init__(self):
        super().__init__(
            name="BioLinkRemover",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins={"root": "plugins"},
            workers=config.HANDLER_WORKERS,
            sleep_threshold=30,
        )
        self.db = None
        self.me = None

    async def start(self, *args, **kwargs):
        # Prepare MongoDB before accepting Telegram updates, preventing startup
        # races where a handler runs before client.db exists.
        self.db = Database(config.MONGO_DB, config.MONGODB_DB_NAME)
        try:
            await self.db.initialize()
            await super().start(*args, **kwargs)
            self.me = await self.get_me()

            user_ids, group_ids = await asyncio.gather(
                self.db.get_all_user_ids(), self.db.get_all_group_ids()
            )
            USER_IDS_CACHE.update(user_ids)
            GROUP_IDS_CACHE.update(group_ids)
            logger.info("Loaded %s users and %s groups into memory.", len(user_ids), len(group_ids))

            if config.LOGGER_GROUP:
                try:
                    await self.send_message(
                        config.LOGGER_GROUP,
                        "<tg-emoji emoji-id='6271537028307881531'>⚡</tg-emoji> <b>BioLinkRemover Bot has started successfully.</b>",
                    )
                except Exception:
                    logger.exception("Could not send startup log to LOGGER_GROUP")
            logger.info("BioLinkRemover started successfully.")
        except Exception:
            logger.exception("Bot startup failed")
            if self.db:
                await self.db.close()
                self.db = None
            raise

    async def stop(self, *args, **kwargs):
        logger.info("Stopping BioLinkRemover...")
        if config.LOGGER_GROUP and self.is_connected:
            try:
                await self.send_message(
                    config.LOGGER_GROUP,
                    "<tg-emoji emoji-id='5275969776668134187'>💤</tg-emoji> <b>BioLinkRemover Bot has been stopped.</b>",
                )
            except Exception:
                logger.debug("Could not send shutdown log", exc_info=True)
        await super().stop(*args, **kwargs)
        if self.db:
            await self.db.close()
            self.db = None
        logger.info("BioLinkRemover stopped.")
