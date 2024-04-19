from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardMarkup as mk, InlineKeyboardButton as kb, Message
from config import Config
from database import db


CLOSE = mk([[kb("Close", "close")]])
CANCEL = mk([[kb("Cancel", "cancel")]])
BACK = mk([[kb("back 🔙", "back")]])

INVITE_LINK = mk([
    [kb("Invite Now 📤", "link")],
])

START = mk([
    [kb("My Balance 💰", "balance")],
    [kb("Invite Link 🔗", "link")],
    [kb("How To Submit Task Proof ❓", "how_to")],
    [kb("Submit your tasks 🚀", "enter")],
])

ADMIN = mk([
    [kb("Users List 📃", "users")],
    [kb("Broadcast 📢", "broadcast")],
    [kb("Users Count 📊", "count")],
    [kb("Stats 📈", "stats")],
    [kb("Admins List 🛡", "admins")],
    [kb("Claim Button", "claim_button")],
])

YES_OR_NO = mk([
    [kb("Yes ✅", "yes"), kb("No ❌", "no")],
])

SUBSCRIBE = mk([
    [kb("$SCOT Channel 🚀", url="https://t.me/scottishtg")],
    [kb("$SCOT Group 👥", url="https://t.me/Scottishtalking")],
    [kb("I joined 🔄", "check_sub")],
])


def team_group(user_id: int, message_id: int, id: int):
    return mk([
        [kb("✅ Approve", f"approve:{user_id}:{message_id}:{id}")],
        [kb("❌ Reject", f"reject:{user_id}:{message_id}:{id}")],
    ])


async def adding_pagination(buttons: list, page: int, elements_number: int, button_data: str):
    current_page_button = kb(f'• {page + 1} •', 'pass')

    pagination_button = list()
    if page > 0:
        if page > 1:
            page_minus_10 = page - 10 if page - 10 >= 0 else 0
            pagination_button.append(kb(f'«« {page_minus_10 + 1}', button_data.format(page_minus_10)))
        pagination_button.append(kb(f'« {page}', button_data.format(page - 1)))
        pagination_button.append(current_page_button)

    if elements_number > Config.ELEMENTS_PER_PAGE:
        if page <= 0:
            pagination_button.append(current_page_button)
        pagination_button.append(kb(f'{page + 2} »', button_data.format(page + 1)))

        if elements_number > Config.ELEMENTS_PER_PAGE * 2:
            elements_left = elements_number - Config.ELEMENTS_PER_PAGE
            last_page = elements_left // Config.ELEMENTS_PER_PAGE if elements_left % Config.ELEMENTS_PER_PAGE == 0 else \
                (elements_left // Config.ELEMENTS_PER_PAGE) + 1
            page_plus_10 = page + 10 if last_page >= 10 else page + last_page

            pagination_button.append(kb(f'{page_plus_10 + 1} »»', button_data.format(page_plus_10)))

    if pagination_button:
        buttons.append(pagination_button)


def share_link(link: str):
    return mk([
        [kb("Share Now 📤", url=f"https://t.me/share/url?url={link}")],
        [kb("Back 🔙", "back")],
    ])


async def AdminsKeyboard(m: Message):
    bts = []
    for user in await db.get_users_list(is_admin=True):
        bts.append([kb(user.name, "pass"), kb("❌", f"remove_admin:{user.id}")])

    bts.append([kb("Add admin 👨‍💼", "add_admin")])
    bts.append([kb("Back 🔙", "admin")])

    try:
        await m.edit_text("👈 **Admins List:**", reply_markup=mk(bts))
    except MessageNotModified:
        pass


async def MembersMarkup(m: Message, page: int = 0):
    users = await db.get_users_list()
    index_by_page = page * Config.ELEMENTS_PER_PAGE
    elements_number = len(users[index_by_page:])
    users = users[index_by_page:index_by_page + Config.ELEMENTS_PER_PAGE]
    markup = []

    for user in users:
        bts = [kb(f"{user.name} ({user.balance})", "pass"),
               kb("{}".format("🟢" if not user.is_banned else "🔴"), f"ban_status:{user.id}:{page}")]
        markup.append(bts)

    await adding_pagination(markup, page, elements_number, "users:{}")
    markup.append([kb("back", "admin")])
    try:
        await m.edit_text("**Users List:**", reply_markup=mk(markup))
    except MessageNotModified:
        pass
