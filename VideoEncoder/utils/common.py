from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .. import LOGGER

HELP_TEXT = """<b>ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇʀ ʜᴇʟᴘ:</b>
<blockquote expandable>➼ ᴜꜱᴇ /ᴍᴇɴᴜ ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ ᴍᴀɪɴ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ.
➼ ᴀᴅᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ꜱᴛᴀʀᴛ ᴍᴀɴᴀɢɪɴɢ ᴛʜᴇᴍ.
➼ ʏᴏᴜ ᴄᴀɴ ᴄʀᴇᴀᴛᴇ ᴘᴏꜱᴛꜱ ᴡɪᴛʜ ᴄᴜꜱᴛᴏᴍ ʙᴜᴛᴛᴏɴꜱ ᴀɴᴅ ꜱᴄʜᴇᴅᴜʟᴇ ᴛʜᴇᴍ ᴛᴏ ʙᴇ ꜱᴇɴᴛ ʟᴀᴛᴇʀ.
➼ ᴜꜱᴇ ᴛʜᴇ ᴛᴀɢ-ʙᴀꜱᴇᴅ ꜱʏꜱᴛᴇᴍ (#ɢ, #ʀ, #ᴘ) ᴛᴏ ᴀᴅᴅ ᴄᴏʟᴏʀᴇᴅ ᴇᴍᴏᴊɪꜱ ᴛᴏ ʏᴏᴜʀ ʙᴜᴛᴛᴏɴꜱ.</blockquote>"""

output = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔙 Back to Home", callback_data="back_start"),
        InlineKeyboardButton("ᴄʟosᴇ", callback_data="close_btn")
    ]
])

start_but = InlineKeyboardMarkup([
    [InlineKeyboardButton("[ • ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ • ]", url="https://t.me/HellFire_Academy")],
    [
        InlineKeyboardButton("[ • ᴅᴇᴠᴇʟᴏᴘᴇʀ • ]", url="https://t.me/DoraShin_hlo"),
        InlineKeyboardButton("[ • ᴄʜᴀᴛ • ]", url="https://t.me/HellFire_Academy_Chat")
    ],
    [InlineKeyboardButton("[ • ᴍᴜɢɪᴡᴀʀᴀs ɴᴇᴛᴡᴏʀᴋ • ]", url="https://t.me/Mugiwaras_Network")]
])


async def edit_msg(message, text=None, **kwargs):
    try:
        if 'media' in kwargs:
            return await message.edit_media(**kwargs)
        if text:
            return await message.edit_text(text, **kwargs)
        if 'caption' in kwargs:
            return await message.edit_caption(**kwargs)
        return await message.edit(**kwargs)
    except Exception as e:
        LOGGER.error(f"Error in edit_msg: {e}")
