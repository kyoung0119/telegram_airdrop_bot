from datetime import datetime
from typing import Union
from pyrogram import Client
from pyrogram.filters import Filter
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message, CallbackQuery
from pyromod.types import ListenerTypes
from pyromod.exceptions import ListenerTimeout, ListenerStopped
from pyrogram.types import InlineKeyboardMarkup as mk, InlineKeyboardButton as kb
from config import Config

CLOSE = mk([[kb("סגירה", "close")]])


async def listen(
        ms: Message,
        fts: Filter,
        lt: ListenerTypes = ListenerTypes.MESSAGE,
        timeout: int = 300
) -> Union[CallbackQuery, Message]:
    try:
        result = await ms.chat.listen(filters=fts, listener_type=lt, timeout=timeout)
    except ListenerTimeout:
        try:
            await ms.edit_text("**Timeout**\nplease /start me again!", reply_markup=CLOSE)
        except Exception as e:
            print(e)
        finally:
            return await ms.stop_propagation()
    except ListenerStopped:
        await ms.delete()
        return await ms.stop_propagation()
    except Exception as e:
        print(e)
        return await ms.stop_propagation()
    return result


async def is_subscribed(c: Client, event: Union[CallbackQuery, Message], chat_id: Union[int, list]):
    if not event.from_user:
        return False

    if isinstance(chat_id, list):
        joined_chats = []
        for chat in chat_id:
            try:
                user = await c.get_chat_member(chat, event.from_user.id)
            except UserNotParticipant:
                return False
            except Exception as e:
                print(e)
                return False
            if user.status != ChatMemberStatus.BANNED:
                joined_chats.append(chat)
        if joined_chats == chat_id:
            return True
        return False
    try:
        user = await c.get_chat_member(chat_id, event.from_user.id)
    except UserNotParticipant:
        return False
    except Exception as e:
        print(e)
        return False
    if user.status != ChatMemberStatus.BANNED:
        return True
    return False


def encrypt_user_id(user_id: int):
    return user_id * 2 + 5


def decrypt_user_id(uid: int):
    return (uid - 5) // 2


def get_share_link(user_id: int):
    return f"https://t.me/{Config.BOT_USERNAME}?start={encrypt_user_id(user_id)}"
