from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from config import Config
from models import User
from datetime import datetime
from text import START_MESSAGE, NEW_REFERRED
from utils import decrypt_user_id
from keyboards import START, ADMIN


@Client.on_message(filters.incoming & filters.private, group=-1)
async def checks(_, m: Message):
    user = m.from_user.id
    get = await db.get_user(user)
    if get:
        if get.is_banned:
            await m.reply_text("You've been banned from using the bot")
            return await m.stop_propagation()
    return await m.continue_propagation()


@Client.on_message(filters.command("start") & filters.private)
async def start(c: Client, m: Message):
    user = m.from_user
    get = await db.get_user(user.id)
    if not get:
        await c.send_message(user.id, START_MESSAGE.format(user.mention), reply_markup=START)
        send = await c.send_message(
            Config.LOG_CHANNEL,
            f"**New user started:**\n\n"
            f"**Name:** {user.mention}\n"
            f"**id:** `{user.id}`\n"
            f"**Username:** @{user.username or ''}"
        )
        u = User(id=user.id, name=user.first_name, username=user.username, date=datetime.utcnow())
        await db.add_user(u)
        if len(m.command) == 2:
            try:
                invited_by = decrypt_user_id(int(m.command[1]))
            except Exception as e:
                print(e)
                return
            inviter = await db.get_user(invited_by)
            if inviter:
                await db.add_balance(invited_by, Config.TOKENS_PER_INVITE)
                await db.add_invited(invited_by, user.id)
                await c.send_message(invited_by, NEW_REFERRED, reply_markup=START)
                await send.edit_text(send.text.markdown + f"\n**Invited by:** {inviter.mention}")
                await db.update_user(user.id, invited_by=invited_by)

    else:
        await c.send_message(user.id, START_MESSAGE.format(user.mention), reply_markup=START)


@Client.on_message(filters.command("admin") & filters.private)
async def admin(_, m: Message):
    get = await db.get_user(m.from_user.id)
    if not get.is_admin:
        return await m.reply_text("You're not allowed to use this command 😅")
    await m.reply_text(f"hi, {m.from_user.mention}, how can i help you today?", reply_markup=ADMIN)
