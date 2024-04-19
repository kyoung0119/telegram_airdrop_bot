import asyncio
from datetime import datetime
from pyrogram import filters
from pyromod import Client, types
from pyrogram.errors import MessageDeleteForbidden, UsernameInvalid, UsernameNotOccupied
from pyrogram.types import CallbackQuery
from database import db, v
from keyboards import *
from models import User, Verification
from datetime import datetime
from utils import listen, is_subscribed, get_share_link
from text import *
from contextlib import suppress

waiting = []


@Client.on_callback_query()
async def callback(c: Client, cb: CallbackQuery):
    data = cb.data
    user = cb.from_user
    m = cb.message
    chat = m.chat.id
    if not user:
        return

    if data != "check_sub":
        if not await is_subscribed(c, cb, [Config.UPDATES_CHANNEL, Config.UPDATES_GROUP]):
            return await m.reply_text(NOT_SUB, reply_markup=SUBSCRIBE)

    if data == "cancel":
        await c.stop_listening(chat_id=chat)
        await m.delete()

    elif data == "close":
        try:
            await m.delete()
        except MessageDeleteForbidden:
            await m.edit_text("Can't Close old message", reply_markup=CLOSE)

    elif data == "check_sub":
        if await is_subscribed(c, cb, [Config.UPDATES_CHANNEL, Config.UPDATES_GROUP]):
            await cb.answer("You are Subscribed 😾")
        else:
            await cb.answer("Hmm, no! You are not yet joined 😾", show_alert=True)
            return

        await c.send_message(chat, START_MESSAGE.format(user.mention), reply_markup=START)
        try:
            await m.delete()
        except MessageDeleteForbidden:
            pass

    elif data == "back":
        await m.edit_text(START_MESSAGE.format(user.mention), reply_markup=START,
                          disable_web_page_preview=True)

    elif data == "admin":
        await m.edit_text(f"hi, {user.mention}, how can i help you today?",
                          reply_markup=ADMIN)

    elif data == "add_admin":
        send = await m.reply_text("please send the admin username", reply_markup=CANCEL)
        d = await listen(send, filters.text)
        username = d.text
        await d.delete()
        try:
            get = await c.get_users(username)
        except (UsernameInvalid, UsernameNotOccupied):
            return await send.edit_text("שם המשתמש שהוזן שגוי... 🧐", reply_markup=CLOSE)
        await d.delete()
        if await db.is_user_exits(get.id):
            await db.update_user(get.id, is_admin=True)
        else:
            admin = User(id=get.id, name=get.first_name, username=get.username, date=datetime.utcnow(), is_admin=True)
            await db.add_user(admin)
        await send.edit_text("המנהל {} נוסף בהצלחה!".format(get.mention), reply_markup=CLOSE)
        await AdminsKeyboard(m)

    elif data == "admins":
        await AdminsKeyboard(m)

    elif data.startswith("remove_admin"):
        uid = int(data.split(":")[1])
        await db.update_user(uid, is_admin=False)
        await AdminsKeyboard(m)

    elif data == "balance":
        get = await db.get_user(user.id)
        await m.edit_text(BALANCE_TEXT.format(get.balance_text), reply_markup=BACK)

    elif data == "link":
        get = await db.get_user(user.id)
        if not get.is_approved:
            return await cb.answer("You are not approved yet or not finish your quests", show_alert=True)
        link = get_share_link(user.id)
        markup = share_link(link)
        await m.edit_text(LINK_TEXT.format(user.mention, link, Config.TOKENS_PER_INVITE), reply_markup=markup)

    elif data == "users":
        await MembersMarkup(m)

    elif data.startswith("users"):
        page = int(data.split(":")[1])
        await MembersMarkup(m, page=page)

    elif data.startswith("ban_status"):
        _, uid, page = data.split(":")
        uid = int(uid)
        page = int(page)
        get = await db.get_user(uid)
        await db.update_user(uid, is_banned=not get.is_banned)
        await MembersMarkup(m, page=page)

    elif data == "count":
        count = await db.users_count()
        await cb.answer(f"Users Count: {count}", show_alert=True)

    elif data == "pass":
        await cb.answer()

    elif data == "enter":
        get = await db.get_user(user.id)
        if get.is_approved:
            return await cb.answer("You are already in the Airdrop, click on Invite Link and share it!", show_alert=True)
        if user.id in waiting:
            return await cb.answer("You are already waiting for approval!", show_alert=True)

        d = await v.get_verifications_list(user_id=user.id)
        retires = len(d) + 1
        if retires > Config.MAX_VERIFICATION_RETRIES:
            return await cb.answer("You have reached the maximum number of retries, please contact support!",
                                   show_alert=True)

        s = await c.send_photo(chat, Config.QUESTS_SITE, caption=QUESTS_CAPTION.format(retires), reply_markup=CANCEL)
        pic = await listen(s, filters.photo, timeout=600)
        await s.delete()
        conf = await pic.copy(chat, "**Do you confirm?**\nClicking yes will send the image to our team for processing.",
                              reply_markup=YES_OR_NO)
        await pic.delete()
        ask = await listen(m, filters.regex("^(yes|no)$"), lt=types.ListenerTypes.CALLBACK_QUERY)
        if ask.data == "yes":
            await conf.edit_text("✅ Your request has been sent to our team for processing,"
                                 " we will notify you when it is approved.")
            waiting.append(user.id)
            count = await v.verifications_count()
            id = count + 1
            vr = Verification(id=id, picture=pic.photo.file_id, date=datetime.utcnow(),
                              user_id=user.id, status="pending")
            await v.add_verification(vr)
            await pic.copy(Config.TEAM_GROUP, f"**Verification id:** {id}\n**User info:**\n{user.mention}\n@{user.username or ''}",
                           reply_markup=team_group(user.id, conf.id, id))
            await asyncio.sleep(2)
            await c.send_message(user.id, START_MESSAGE.format(user.mention), reply_markup=START)
        else:
            await conf.edit_text("Ok, You canceled the request.")
            await asyncio.sleep(2)
            await c.send_message(user.id, START_MESSAGE.format(user.mention), reply_markup=START)

    elif data.startswith("approve"):
        uid, mid, id = map(int, data.split(":")[1:])
        with suppress(ValueError):  # ignore if user not in waiting list
            waiting.remove(uid)
        get = await db.get_user(uid)
        await db.update_user(uid, is_approved=True)
        await v.update_verification(id, status="approved")
        await db.add_balance(uid, Config.TOKENS_FOR_TASK)
        await m.edit_text(f"**Approved:** {get.mention} by {user.mention}")

        try:
            await c.send_message(uid, APPROVED, reply_markup=INVITE_LINK, reply_to_message_id=mid)
        except Exception as e:
            print(e)

    elif data.startswith("reject"):
        uid, mid, id = map(int, data.split(":")[1:])
        get = await db.get_user(uid)
        await m.edit_text(f"**Rejected:** {get.mention} by {user.mention}")
        await v.update_verification(id, status="rejected")
        with suppress(ValueError):  # ignore if user not in waiting list
            waiting.remove(uid)
        try:
            await c.send_message(uid, REJECTED, reply_markup=START, reply_to_message_id=mid)
        except Exception as e:
            print(e)

    elif data == "stats":
        users = await db.users_count()
        approved = await db.users_count(is_approved=True)
        total_tokens = f"{sum([i.balance for i in await db.get_users_list()]):,} $SCOT"
        pending = await v.verifications_count(status="pending")
        approved_v = await v.verifications_count(status="approved")
        rejected = await v.verifications_count(status="rejected")
        await m.reply_text(STATS.format(users, approved, total_tokens, pending, approved_v, rejected), reply_markup=CLOSE)

    elif data == "how_to":
        await m.edit_text(HELP, reply_markup=BACK, disable_web_page_preview=True)

    elif data == "withdraw":
        # TODO: Withdraw
        ...