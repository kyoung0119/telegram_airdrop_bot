import asyncio
from datetime import datetime
from pyrogram.raw.all import layer
from pyrogram import __version__
from pyrogram.types import BotCommand, BotCommandScopeAllPrivateChats
import betterlogging as bl
from config import Config
from database import db
from models import User
from pyromod import Client
from functools import partial

logger = bl.getLogger("airdrop")
bl.basic_colorized_config(level=bl.INFO, format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s")
bl.getLogger("pyrogram").setLevel(bl.WARNING)


class Bot(Client):

    def __init__(self):
        super().__init__(
            "airdrop",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.TOKEN,
            plugins=dict(root="plugins"),
            workers=100,
            sleep_threshold=30)
        self.send_message = partial(self.send_message, disable_web_page_preview=True) #  disable web page preview for all messages

    async def start(self):
        await super().start()
        logger.info("setting admins...")
        for user in Config.ADMINS:
            try:
                gu = await self.get_users(user)
                await asyncio.sleep(0.5)
                if not await db.is_user_exits(gu.id):
                    us = User(id=gu.id, name=gu.first_name, username=gu.username,
                              date=datetime.utcnow(), is_admin=True, is_approved=True)
                    await db.add_user(us)
                    logger.info(f"user [{gu.first_name} - {gu.id}] set as admin")
            except Exception as e:
                logger.error(f"cannot add {user} as admin. error - {e}")
                continue
        await self.set_bot_commands(
            [BotCommand("start", "start the bot ⚡ ")],
            BotCommandScopeAllPrivateChats()
        )
        me = await self.get_me()
        logger.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{me.username}")

    async def stop(self, block: bool = True):
        await super().stop(block)
        logger.info("Bot stopped. Bye.")


app = Bot()
app.run()
