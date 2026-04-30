import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from .. import app

@app.on_callback_query()
async def main_callback_handler(bot: Client, cb: CallbackQuery):
    await cb.answer()

    data = cb.data
    from .. import LOGGER
    LOGGER.info(f"Executing logic for: {data}")

    try:
        if data == "back_start":
            from .start import START_MSG, START_PIC
            from ..utils.common import start_but, edit_msg
            user = cb.from_user
            name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
            link = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
            mention = f"<a href='{link}'>{name}</a>"
            try:
                await edit_msg(
                    cb.message,
                    media=InputMediaPhoto(START_PIC, caption=START_MSG.format(mention=mention), has_spoiler=True),
                    reply_markup=start_but
                )
            except Exception as e:
                LOGGER.error(f"Error in backToStart: {e}")
                await edit_msg(cb.message, caption=START_MSG.format(mention=mention), reply_markup=start_but)

        elif data in ["close_btn", "closeMeh"]:
            await cb.message.delete()

        elif data == "help_callback":
            from ..utils.common import HELP_TEXT, edit_msg
            from .start import START_PIC
            buttons = [
                [
                    InlineKeyboardButton("🔙 Back to Home", callback_data="back_start"),
                    InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="closeMeh")
                ]
            ]
            await edit_msg(cb.message, media=InputMediaPhoto(START_PIC, caption=HELP_TEXT, has_spoiler=True), reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        from VideoEncoder import LOGGER
        LOGGER.error(f"Error in main_callback_handler: {e}")
