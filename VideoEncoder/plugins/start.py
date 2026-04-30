from VideoEncoder import LOGGER


import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from .. import botStartTime
from ..utils.display_progress import TimeFormatter
from ..utils.common import start_but

START_PIC = "https://graph.org/file/a43e51fdee6998d7074e0-c9255fe3e80803a9a9.jpg"
FORCE_PIC = "https://graph.org/file/a0947a8895736ff574666-422dfa95e7395c7142.jpg"
START_MSG = "<b>ʜᴇʏ!!, {mention} ~\n\nᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴀᴅᴠᴀɴᴄᴇᴅ ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇʀ ʙᴏᴛ! <blockquote expandable>ɪ ᴄᴀɴ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ, ꜱᴄʜᴇᴅᴜʟᴇ ᴘᴏꜱᴛꜱ, ᴀɴᴅ ᴍᴏʀᴇ ᴡɪᴛʜ ᴇᴀꜱᴇ. ᴜꜱᴇ /ᴍᴇɴᴜ ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴇᴀᴛᴜʀᴇꜱ.</blockquote></b>"


def uptime():
    """ returns uptime """
    return TimeFormatter(time.time() - botStartTime)


@Client.on_message(filters.command('start'))
async def start_message(app, message):
    from ..utils.helper import check_chat
    c = await check_chat(message, chat='Both')
    if not c:
        return await message.reply_photo(photo=FORCE_PIC, caption="<b>You are not authorized to use this bot!</b>", has_spoiler=True)

    user = message.from_user
    name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    link = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
    mention = f"<a href='{link}'>{name}</a>"
    await message.reply_photo(photo=START_PIC, caption=START_MSG.format(mention=mention), reply_markup=start_but, has_spoiler=True)


@Client.on_message(filters.command('help'))
async def help_message(app, message):
    from ..utils.common import HELP_TEXT
    from ..utils.helper import check_chat
    c = await check_chat(message, chat='Both')
    if not c:
        return

    buttons = [
        [
            InlineKeyboardButton("🔙 Back to Home", callback_data="back_start"),
            InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="closeMeh")
        ]
    ]

    await message.reply_photo(photo=START_PIC, caption=HELP_TEXT, reply_markup=InlineKeyboardMarkup(buttons), has_spoiler=True)


@Client.on_message(filters.command('stats'))
async def show_status_count(_, message: Message):
    from ..utils.helper import check_chat
    c = await check_chat(message, chat='Both')
    if not c:
        return

    currentTime = TimeFormatter(time.time() - botStartTime)
    text = f"<b>Uptime:</b> {currentTime}"
    await message.reply_text(text)
