
import re
import json
import dateparser
import pytz
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    ChatMemberUpdated,
    InputMediaPhoto
)
from ..utils.database.channel_db import channel_db
from .. import owner, log as LOG_CHANNEL
from ..utils.helper import check_chat
from ..utils.font_utils import apply_font
from ..utils.button_parser import parse_buttons

def to_small_caps(text):
    return apply_font(text, "ꜱᴍᴀʟʟ ᴄᴀᴘꜱ")

# Images
IMG_STEP_1 = "https://graph.org/file/4b47117b95200ac2e751a-3e8f7112e398a80a59.jpg"
IMG_STEP_2 = "https://graph.org/file/e2c1e874a571f80b5f293-47e72b2fe344f6bf91.jpg"
IMG_STEP_3 = "https://graph.org/file/320f94e5a1a300f93ef48-8bb0005cc95073fd48.jpg"
IMG_STEP_4 = "https://graph.org/file/ed58bde604af394dde224-5b6eac77faffa3714b.jpg"
IMG_STEP_5 = "https://graph.org/file/7ed499c9b203e7cfecafc-12100e81e0e8a6793f.jpg"

# Quotes
QUOTE_STEP_1 = "ᴛʜᴇ ɢʀᴇᴀᴛᴇꜱᴛ ᴘᴏᴡᴇʀ ɪꜱ ᴛʜᴇ ᴘᴏᴡᴇʀ ᴛᴏ ᴄᴏɴᴛʀᴏʟ ʏᴏᴜʀ ᴏᴡɴ ᴅᴇꜱᴛɪɴʏ."
QUOTE_STEP_2 = "ᴄʀᴇᴀᴛɪᴠɪᴛʏ ɪꜱ ᴛʜᴇ ᴋᴇʏ ᴛᴏ ᴜɴʟᴏᴄᴋɪɴɢ ᴇɴᴅʟᴇꜱꜱ ᴘᴏꜱꜱɪʙɪʟɪᴛɪᴇꜱ."
QUOTE_STEP_3 = "ᴇᴠᴇʀʏ ɪᴍᴀɢᴇ ᴛᴇʟʟs ᴀ sᴛᴏʀʏ, ᴍᴀᴋᴇ ʏᴏᴜʀs ᴡᴏʀᴛʜ ᴛᴇʟʟɪɴɢ."
QUOTE_STEP_4 = "ʟᴏɢɪᴄ ᴡɪʟʟ ɢᴇᴛ ʏᴏᴜ ғʀᴏᴍ ᴀ ᴛᴏ ʙ, ʙᴜᴛ ɪᴍᴀɢɪɴᴀᴛɪᴏɴ ᴡɪʟʟ ᴛᴀᴋᴇ ʏᴏᴜ ᴇᴠᴇʀʏᴡʜᴇʀᴇ."
QUOTE_STEP_5 = "ᴛɪᴍᴇ ɪs ᴛʜᴇ sᴄᴀʀᴄᴇsᴛ ʀᴇsᴏᴜʀᴄᴇ, ᴍᴀɴᴀɢᴇ ɪᴛ ᴡɪsᴇʟʏ."

@Client.on_message(filters.command("menu") & filters.private)
async def menu_handler(bot: Client, message: Message):
    c = await check_chat(message, chat='Both')
    if not c:
        return
    await show_step_1(message)

async def show_step_1(message_or_query):
    user = message_or_query.from_user
    name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    link = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
    user_link = f"<a href='{link}'>{name}</a>"

    caption = f"<blockquote>{QUOTE_STEP_1}</blockquote>\n\n"
    caption += to_small_caps(f"👋🏻 ᴡᴇʟᴄᴏᴍᴇ {user_link} ᴛᴏ ᴄʜᴀɴɴᴇʟ ʜᴇʟᴘ!\n\n")
    caption += to_small_caps("• ꜱᴇɴᴅ ᴘᴏꜱᴛꜱ ᴡɪᴛʜ ʙᴜᴛᴛᴏɴꜱ ꜱɪᴍᴜʟᴛᴀɴᴇᴏᴜꜱʟʏ ɪɴ ᴍᴜʟᴛɪᴘʟᴇ ᴄʜᴀɴɴᴇʟꜱ\n")
    caption += to_small_caps("• ᴡᴇʟᴄᴏᴍᴇ ɴᴇᴡ ꜱᴜʙꜱᴄʀɪʙᴇʀꜱ\n")
    caption += to_small_caps("• ᴄʀᴇᴀᴛᴇ ᴘᴏꜱᴛꜱ ᴛʜᴀᴛ ꜱᴇɴᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴇᴠᴇʀʏ ᴍɪɴᴜᴛᴇ, ʜᴏᴜʀ, ᴏʀ ᴅᴀʏ\n")
    caption += to_small_caps("• ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ғʀᴏᴍ ᴜɴᴡᴀɴᴛᴇᴅ ᴜꜱᴇʀꜱ\n")
    caption += to_small_caps("• ᴀᴜᴛᴏ-ᴄᴏᴍᴘʟᴇᴛᴇ ғᴇᴀᴛᴜʀᴇꜱ... ᴀɴᴅ ᴍᴜᴄʜ ᴍᴏʀᴇ!")

    buttons = [
        [InlineKeyboardButton(to_small_caps("🔴 + ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ"), callback_data="cm_add_channel")],
        [
            InlineKeyboardButton(to_small_caps("🔵 ᴄʀᴇᴀᴛᴇ ᴘᴏꜱᴛꜱ"), callback_data="cm_step_2"),
            InlineKeyboardButton(to_small_caps("🔵 ʙᴀᴄᴋ"), callback_data="back_start")
        ],
        [
            InlineKeyboardButton(to_small_caps("📣 ᴄʜᴀɴɴᴇʟ"), url="https://t.me/Anime_Fury"),
            InlineKeyboardButton(to_small_caps("📄 ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ"), callback_data="cm_privacy")
        ]
    ]

    if isinstance(message_or_query, Message):
        await message_or_query.reply_photo(photo=IMG_STEP_1, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message_or_query.message.edit_media(media=InputMediaPhoto(IMG_STEP_1, caption=caption), reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.private & ~filters.command(["start", "menu", "help", "settings"]))
async def message_input_handler(bot: Client, message: Message):
    c = await check_chat(message, chat='Both')
    if not c:
        return

    user_id = message.from_user.id
    draft = await channel_db.get_draft(user_id)

    # Step 3 logic: Expecting media or text for the post
    if not draft or (not draft['message_text'] and not draft['media_file_id']):
        media_file_id = None
        media_type = None

        if message.photo:
            media_file_id = message.photo.file_id
            media_type = "photo"
        elif message.video:
            media_file_id = message.video.file_id
            media_type = "video"
        elif message.document:
            media_file_id = message.document.file_id
            media_type = "document"
        elif message.animation:
            media_file_id = message.animation.file_id
            media_type = "animation"
        elif message.sticker:
            media_file_id = message.sticker.file_id
            media_type = "sticker"
        elif message.voice:
            media_file_id = message.voice.file_id
            media_type = "voice"
        elif message.video_note:
            media_file_id = message.video_note.file_id
            media_type = "video_note"
        elif message.audio:
            media_file_id = message.audio.file_id
            media_type = "audio"

        await channel_db.save_draft(
            user_id,
            message_text=message.caption or message.text or " ",
            media_file_id=media_file_id,
            media_type=media_type
        )
        await message.reply_text(to_small_caps("✅ ᴘᴏꜱᴛ ᴄᴏɴᴛᴇɴᴛ ꜱᴀᴠᴇᴅ! ɴᴏᴡ ꜱᴇɴᴅ ʙᴜᴛᴛᴏɴ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ ᴏʀ ᴜꜱᴇ /ᴍᴇɴᴜ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ."),
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(to_small_caps("ɴᴇxᴛ (ꜱᴇᴛ ʙᴜᴛᴛᴏɴꜱ)"), callback_data="cm_step_4")]]))
        return

    # Handle scheduling input
    if draft and draft['buttons'] and (":" in (message.text or "") or "at" in (message.text or "").lower() or "tomorrow" in (message.text or "").lower()):
        return await schedule_input_handler(bot, message)

    # Handle font setting
    if draft and draft['buttons'] == "WAITING_FOR_FONT":
        if message.text in ["ꜱᴍᴀʟʟ ᴄᴀᴘꜱ", "𝐁𝐨𝐥𝐝", "𝖲𝖺𝗇𝗌"]:
            await channel_db.update_user_settings(message.from_user.id, font_style=message.text)
            await channel_db.save_draft(message.from_user.id, buttons=" ") # Reset buttons field
            return await cb_step_4(bot, message)
        else:
            return await message.reply_text(to_small_caps("❌ ɪɴᴠᴀʟɪᴅ ғᴏɴᴛ ꜱᴛʏʟᴇ! ᴘʟᴇᴀꜱᴇ ᴄʜᴏᴏꜱᴇ ғʀᴏᴍ ᴛʜᴇ ᴍᴇɴᴜ."))

    # Handle timezone setting
    if draft and draft['buttons'] == "WAITING_FOR_TZ":
        tz_input = message.text.strip().upper()
        # Basic validation with dateparser
        test_dt = dateparser.parse("now", settings={'TIMEZONE': tz_input})
        if test_dt:
            await channel_db.update_user_settings(message.from_user.id, timezone=tz_input)
            await channel_db.save_draft(message.from_user.id, buttons=" ") # Reset
            return await cb_step_5(bot, message)
        else:
            return await message.reply_text(to_small_caps("❌ ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇᴢᴏɴᴇ! ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴏɴᴇ (ᴇ.ɢ. ɪꜱᴛ, ᴇꜱᴛ, ᴜᴛᴄ)."))

    # Step 4 logic: Expecting button configuration
    if draft and (not draft['buttons'] or draft['buttons'] == " " or "|" in message.text or " - " in message.text):
        await channel_db.save_draft(message.from_user.id, buttons=message.text)
        await message.reply_text(to_small_caps("✅ ʙᴜᴛᴛᴏɴꜱ ꜱᴀᴠᴇᴅ!"),
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(to_small_caps("ɴᴇxᴛ (ꜱᴄʜᴇᴅᴜʟᴇ)"), callback_data="cm_step_5")]]))
        return

@Client.on_callback_query(filters.regex("^cm_step_1$"))
async def cb_step_1(bot, query):
    await show_step_1(query)

@Client.on_callback_query(filters.regex("^cm_step_2$"))
async def cb_step_2(bot, query):
    caption = f"<blockquote>{QUOTE_STEP_2}</blockquote>\n\n"
    caption += to_small_caps("📨 ᴄʀᴇᴀᴛᴇ ᴘᴏꜱᴛꜱ • ɢᴜɪᴅᴇ\n")
    caption += to_small_caps("ғʀᴏᴍ ᴛʜɪꜱ ᴍᴇɴᴜ ʏᴏᴜ ᴄᴀɴ ᴄʜᴏᴏꜱᴇ ᴛʜᴇ ᴘᴏꜱᴛ ꜱᴇᴛᴛɪɴɢꜱ.\n\n")
    caption += to_small_caps("• ᴘʀᴇꜱꜱ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ᴏɴ ᴛʜᴇ ʟᴇғᴛ ᴛᴏ ᴋɴᴏᴡ ʜᴏᴡ ꜱᴇᴛᴛɪɴɢꜱ ᴡᴏʀᴋ.\n")
    caption += to_small_caps("• ᴘʀᴇꜱꜱ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ᴏɴ ᴛʜᴇ ʀɪɢʜᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ꜱᴇᴛᴛɪɴɢꜱ.")

    buttons = [[InlineKeyboardButton(to_small_caps("🔵 ɴᴇxᴛ"), callback_data="cm_step_3")]]

    await query.message.edit_media(
        media=InputMediaPhoto(IMG_STEP_2, caption=caption),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^cm_step_3$"))
async def cb_step_3(bot, query):
    caption = f"<blockquote>{QUOTE_STEP_3}</blockquote>\n\n"
    caption += to_small_caps("ꜱᴇɴᴅ ᴛʜᴇ ᴘᴏꜱᴛ ᴍᴇssᴀɢᴇ ᴏʀ ᴍᴇᴅɪᴀ\n")
    caption += to_small_caps("ᴀʟʟᴏᴡᴇᴅ ᴍᴇᴅɪᴀ: ᴘʜᴏᴛᴏs, ᴠɪᴅᴇᴏs, ᴀʟʙᴜᴍs, ғɪʟᴇs, ɢɪғs.\n")
    caption += to_small_caps("💡 ᴛᴏ ᴀᴛᴛᴀᴄʜ ᴀ ᴍᴇᴅɪᴀ ᴜɴᴅᴇʀ ᴛʜᴇ ᴘᴏsᴛ, sᴇɴᴅ ɪᴛ ʜᴇʀᴇ.")

    buttons = [
        [
            InlineKeyboardButton(to_small_caps("🔵 ᴍᴇɴᴜ"), callback_data="cm_step_1"),
            InlineKeyboardButton(to_small_caps("🔵 ʙᴀᴄᴋ"), callback_data="cm_step_2")
        ]
    ]

    if isinstance(query, Message):
        await query.reply_photo(photo=IMG_STEP_3, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await query.message.edit_media(
            media=InputMediaPhoto(IMG_STEP_3, caption=caption),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Client.on_callback_query(filters.regex("^cm_step_4$"))
async def cb_step_4(bot, query):
    user_id = query.from_user.id
    settings = await channel_db.get_user_settings(user_id)
    font_style = settings['font_style']

    caption = f"<blockquote>{QUOTE_STEP_4}</blockquote>\n\n"
    caption += to_small_caps(f"⧗ sᴇᴛ ʙᴜᴛᴛᴏɴs ғᴏʀ ᴘᴏsᴛ\n")
    caption += to_small_caps(f"ᴄᴜʀʀᴇɴᴛ ғᴏɴᴛ: {font_style}\n\n")
    caption += to_small_caps("ғᴏʀᴍᴀᴛ: ᴛᴇxᴛ - {link}\n")
    caption += to_small_caps("ᴍᴜʟᴛɪᴘʟᴇ: ᴊᴏɪɴ - {link} | ɢʀᴏᴜᴘ - {link}\n")
    caption += to_small_caps("ᴄᴏʟᴏʀs: #ɢ (ɢʀᴇᴇɴ), #ʀ (ʀᴇᴅ), #ᴘ (ᴘʀɪᴍᴀʀʏ)")

    buttons = [
        [InlineKeyboardButton(to_small_caps("✒️ ᴄʜᴀɴɢᴇ ғᴏɴᴛ"), callback_data="cm_font_settings")],
        [InlineKeyboardButton(to_small_caps("🔵 ʙᴀᴄᴋ"), callback_data="cm_step_3")]
    ]

    if isinstance(query, Message):
        await query.reply_photo(photo=IMG_STEP_4, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await query.message.edit_media(
            media=InputMediaPhoto(IMG_STEP_4, caption=caption),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Client.on_callback_query(filters.regex("^cm_step_5$"))
async def cb_step_5(bot, query):
    user_id = query.from_user.id
    settings = await channel_db.get_user_settings(user_id)
    user_tz = settings['timezone']

    caption = f"<blockquote>{QUOTE_STEP_5}</blockquote>\n\n"
    caption += to_small_caps("ᴛʜʀᴏᴜɢʜ ᴛʜɪs ᴍᴇɴᴜ ʏᴏᴜ ᴄᴀɴ sᴀᴠᴇ ᴛʜᴇ ᴘᴏsᴛ ᴛᴏ sᴇɴᴅ ɪᴛ ʟᴀᴛᴇʀ ᴏʀ ᴄʜᴏᴏsᴇ ᴀᴅᴅɪᴛɪᴏɴᴀʟ sᴇᴛᴛɪɴɢs.\n")
    caption += to_small_caps(f"*(ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇᴢᴏɴᴇ: {user_tz})*")

    buttons = [
        [
            InlineKeyboardButton(to_small_caps("🔵 sᴇɴᴅ ᴘᴏsᴛ"), callback_data="cm_send_post"),
            InlineKeyboardButton(to_small_caps("🔵 sᴄʜᴇᴅᴜʟᴇ ᴘᴏsᴛ"), callback_data="cm_schedule_post")
        ],
        [
            InlineKeyboardButton(to_small_caps("🔵 sᴄʜᴇᴅᴜʟᴇ ᴅᴇʟᴇᴛɪᴏɴ"), callback_data="cm_schedule_del"),
            InlineKeyboardButton(to_small_caps("🔵 ᴘɪɴ ᴘᴏsᴛ"), callback_data="cm_pin_post")
        ],
        [
            InlineKeyboardButton(to_small_caps("🔵 sᴇᴛ ᴛɪᴍᴇᴢᴏɴᴇ"), callback_data="cm_set_tz"),
            InlineKeyboardButton(to_small_caps("🔵 ʙᴀᴄᴋ ᴘᴏsᴛ"), callback_data="cm_step_4")
        ]
    ]

    if isinstance(query, Message):
        await query.reply_photo(photo=IMG_STEP_5, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await query.message.edit_media(
            media=InputMediaPhoto(IMG_STEP_5, caption=caption),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Client.on_callback_query(filters.regex("^cm_font_settings$"))
async def cb_font_settings(bot, query):
    caption = to_small_caps("✨ ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴘʀᴇғᴇʀʀᴇᴅ ʙᴜᴛᴛᴏɴ ғᴏɴᴛ sᴛʏʟᴇ:")
    buttons = [
        [InlineKeyboardButton("ꜱᴍᴀʟʟ ᴄᴀᴘꜱ", callback_data="cm_set_font_ꜱᴍᴀʟʟ ᴄᴀᴘꜱ")],
        [InlineKeyboardButton("𝐁𝐨𝐥𝐝", callback_data="cm_set_font_𝐁𝐨𝐥𝐝")],
        [InlineKeyboardButton("𝖲𝖺𝗇𝗌", callback_data="cm_set_font_𝖲𝖺𝗇𝗌")],
        [InlineKeyboardButton(to_small_caps("🔵 ʙᴀᴄᴋ"), callback_data="cm_step_4")]
    ]
    await query.message.edit_caption(caption=caption, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^cm_set_font_"))
async def cb_set_font(bot, query):
    font_style = query.data.replace("cm_set_font_", "")
    await channel_db.update_user_settings(query.from_user.id, font_style=font_style)
    await query.answer(to_small_caps(f"✅ ғᴏɴᴛ sᴛʏʟᴇ sᴇᴛ ᴛᴏ {font_style}"), show_alert=True)
    await cb_step_4(bot, query)

@Client.on_callback_query(filters.regex("^cm_set_tz$"))
async def cb_set_tz_prompt(bot, query):
    await channel_db.save_draft(query.from_user.id, buttons="WAITING_FOR_TZ")
    await query.message.reply_text(to_small_caps("⌛ ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴛɪᴍᴇᴢᴏɴᴇ (ᴇ.ɢ. ɪsᴛ, ᴇsᴛ, ᴜᴛᴄ, ᴀsɪᴀ/ᴋᴏʟᴋᴀᴛᴀ)."))
    await query.answer()

@Client.on_callback_query(filters.regex("^cm_add_channel$"))
async def cb_add_channel(bot, query):
    await query.answer(to_small_caps("ᴛᴏ ᴀᴅᴅ ᴀ ᴄʜᴀɴɴᴇʟ, ᴊᴜꜱᴛ ᴀᴅᴅ ᴛʜᴇ ʙᴏᴛ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ!"), show_alert=True)

@Client.on_callback_query(filters.regex("^cm_privacy$"))
async def cb_privacy(bot, query):
    await query.answer(to_small_caps("ʏᴏᴜʀ ᴅᴀᴛᴀ ɪꜱ ꜱᴀғᴇ ᴡɪᴛʜ ᴜꜱ. ᴡᴇ ᴅᴏ ɴᴏᴛ ꜱʜᴀʀᴇ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴏʀ ᴘᴏꜱᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ."), show_alert=True)

@Client.on_callback_query(filters.regex("^back_start$"))
async def cb_back_start(bot, query):
    from .start import start_message
    await query.message.delete()
    await start_message(bot, query)

@Client.on_chat_member_updated()
async def admin_added_handler(bot: Client, update: ChatMemberUpdated):
    if not update.new_chat_member:
        return

    if update.new_chat_member.user.id == (await bot.get_me()).id:
        old_status = update.old_chat_member.status if update.old_chat_member else None
        new_status = update.new_chat_member.status

        if new_status in ["administrator", "creator"] and old_status not in ["administrator", "creator"]:
            chat = update.chat
            await channel_db.add_channel(chat.id, chat.title, chat.username)

            for admin_id in owner:
                try:
                    await bot.send_message(
                        admin_id,
                        to_small_caps(f"🤖 ɪ ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ ɪɴ {chat.title}!"),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(to_small_caps("ᴍᴇɴᴜ"), callback_data="cm_step_1")]])
                    )
                except Exception as e:
                    print(f"Error notifying admin {admin_id}: {e}")


@Client.on_callback_query(filters.regex("^cm_send_post$"))
async def cb_send_post(bot, query):
    user_id = query.from_user.id
    draft = await channel_db.get_draft(user_id)
    if not draft:
        return await query.answer(to_small_caps("❌ ɴᴏ ᴅʀᴀғᴛ ғᴏᴜɴᴅ!"), show_alert=True)

    channels = await channel_db.get_channels()
    if not channels:
        return await query.answer(to_small_caps("❌ ɴᴏ ᴄʜᴀɴɴᴇʟꜱ ᴀᴅᴅᴇᴅ!"), show_alert=True)

    settings = await channel_db.get_user_settings(user_id)
    reply_markup = parse_buttons(draft['buttons'], settings['font_style'])

    success = 0
    for channel in channels:
        try:
            if draft['media_type'] == "photo":
                await bot.send_photo(channel['chat_id'], draft['media_file_id'], caption=draft['message_text'], reply_markup=reply_markup)
            elif draft['media_type'] == "video":
                await bot.send_video(channel['chat_id'], draft['media_file_id'], caption=draft['message_text'], reply_markup=reply_markup)
            elif draft['media_type'] == "document":
                await bot.send_document(channel['chat_id'], draft['media_file_id'], caption=draft['message_text'], reply_markup=reply_markup)
            elif draft['media_type'] == "animation":
                await bot.send_animation(channel['chat_id'], draft['media_file_id'], caption=draft['message_text'], reply_markup=reply_markup)
            else:
                await bot.send_message(channel['chat_id'], draft['message_text'], reply_markup=reply_markup)
            success += 1
        except Exception as e:
            print(f"Error sending to {channel['chat_id']}: {e}")

    await query.message.edit_media(
        media=InputMediaPhoto(IMG_STEP_1, caption=to_small_caps(f"✅ ᴘᴏꜱᴛ ꜱᴇɴᴛ ᴛᴏ {success} ᴄʜᴀɴɴᴇʟꜱ!")),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(to_small_caps("🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ"), callback_data="cm_step_1")]])
    )
    await channel_db.delete_draft(query.from_user.id)

@Client.on_callback_query(filters.regex("^cm_schedule_post$"))
async def cb_schedule_prompt(bot, query):
    await query.message.reply_text(to_small_caps("ꜱᴇɴᴅɪɴɢ ꜱᴄʜᴇᴅᴜʟᴇ. ғᴏʀᴍᴀᴛ: ᴅᴅ/ᴍᴍ/ʏʏ ʜʜ:ᴍᴍ\nᴏʀ ᴜꜱᴇ ɴᴀᴛᴜʀᴀʟ ʟᴀɴɢᴜᴀɢᴇ ʟɪᴋᴇ 'ᴛᴏᴍᴏʀʀᴏᴡ ᴀᴛ 12:00'"))

@Client.on_message(filters.private & filters.text & filters.create(lambda _, __, m: ":" in (m.text or "") or "at" in (m.text or "").lower() or "tomorrow" in (m.text or "").lower()))
async def schedule_input_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    draft = await channel_db.get_draft(user_id)
    if not draft:
        return

    settings = await channel_db.get_user_settings(user_id)
    user_tz = settings['timezone']

    # Map IST to Asia/Kolkata
    tz_map = {"IST": "Asia/Kolkata"}
    tz_name = tz_map.get(user_tz, user_tz)

    try:
        user_timezone = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        user_timezone = pytz.UTC

    dt = dateparser.parse(message.text, settings={'TIMEZONE': user_tz})
    if not dt:
        return

    # Actually dateparser with TIMEZONE setting returns naive local time.
    # We need to localize it and then convert to UTC.
    localized_dt = user_timezone.localize(dt)
    utc_dt = localized_dt.astimezone(pytz.UTC)

    if utc_dt < datetime.now(pytz.UTC):
        return await message.reply_text(to_small_caps("❌ ꜱᴄʜᴇᴅᴜʟᴇᴅ ᴛɪᴍᴇ ᴍᴜꜱᴛ ʙᴇ ɪɴ ᴛʜᴇ ғᴜᴛᴜʀᴇ!"))

    channels = await channel_db.get_channels()
    chat_ids = [c['chat_id'] for c in channels]

    await channel_db.add_scheduled_post(
        user_id,
        chat_ids,
        draft['message_text'],
        draft['media_file_id'],
        draft['media_type'],
        draft['buttons'],
        utc_dt.isoformat()
    )

    await message.reply_text(
        to_small_caps(f"✅ ᴘᴏꜱᴛ ꜱᴄʜᴇᴅᴜʟᴇᴅ ғᴏʀ {dt.strftime('%d/%m/%y %H:%M')} ({user_tz})"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(to_small_caps("🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ"), callback_data="cm_step_1")]])
    )
    await channel_db.delete_draft(message.from_user.id)
