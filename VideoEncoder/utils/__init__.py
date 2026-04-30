from pyrogram import Client, filters
from .. import LOGGER

LOGGER.info('Imported Utils!')

sauce = '''<b>Advanced Channel Manager & Postify Pro</b>
This bot is designed for efficient channel management and post scheduling.'''


@Client.on_message(filters.command('source'))
async def g_s(_, message):
    from .common import output
    try:
        await message.reply(text=sauce, reply_markup=output, disable_web_page_preview=True)
    except Exception:
        pass
