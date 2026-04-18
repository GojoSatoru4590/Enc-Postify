
import os
import asyncio
import google.generativeai as genai
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode
from .. import ASSETS_DIR, LOGGER, download_dir
from ..utils.database.add_user import AddUserToDatabase
from ..utils.helper import check_chat
from ..utils.uploads.telegram import upload_doc

# Setup Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# user_id: True if waiting for subtitle file
translator_sessions = {}

@Client.on_message(filters.command("translator") & filters.private)
async def translator_cmd(bot: Client, message: Message):
    c = await check_chat(message, chat='Both')
    if not c:
        return
    await AddUserToDatabase(bot, message)

    img_url = "https://graph.org/file/3b3e573290ea2f1ab272e-d0521dd8d5a1359e41.jpg"
    text = "🌐 𝖠𝖨 𝖲𝖴𝖳𝖨𝖳𝖫𝖤 𝖳𝖱𝖠𝖭𝖲𝖫𝖠𝖳𝖮𝖱\n<blockquote expandable>➤ ᴛʀᴀɴsʟᴀᴛᴇ ʏᴏᴜʀ ᴀɴɪᴍᴇ/ᴍᴀɴʜᴡᴀ sᴜʙᴛɪᴛʟᴇs ᴜsɪɴɢ ᴀᴅᴠᴀɴᴄᴇᴅ ɢᴇᴍɪɴɪ ᴀɪ. ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ sᴛᴀʀᴛ.</blockquote>"

    buttons = [
        [
            InlineKeyboardButton("ʜɪɴɢʟɪsʜ", callback_data="hinglish_trigger"),
            InlineKeyboardButton("ʜᴇʟᴘ", callback_data="translator_help")
        ],
        [
            InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="closeMeh")
        ]
    ]

    await message.reply_photo(
        photo=img_url,
        caption=text,
        has_spoiler=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.document & filters.private, group=-1)
async def translator_file_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in translator_sessions:
        return

    if not message.document or not (message.document.file_name.endswith(".ass") or message.document.file_name.endswith(".srt")):
        return

    message.stop_propagation()
    del translator_sessions[user_id]

    msg = await message.reply_text("<code>Processing AI Translation... ⏳</code>")

    file_path = await message.download(file_name=os.path.join(download_dir, message.document.file_name))

    try:
        if not model:
            await msg.edit("❌ <b>Gemini API Key not found!</b> Please set <code>GEMINI_API_KEY</code> in config.")
            return

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        await msg.edit("<code>Translating content with Gemini AI... 🤖</code>")

        is_srt = file_path.endswith(".srt")
        fmt = "SRT" if is_srt else "ASS"

        prompt = f"Translate the following {fmt} subtitle content to natural Hinglish for Anime/Manhwa fans. " \
                 f"Keep it cool and contextual. DO NOT change timestamps or indices. " \
                 f"Maintain the {fmt} format exactly. Return only the translated {fmt} content.\n\n" + content

        response = await asyncio.to_thread(model.generate_content, prompt)
        translated_content = response.text.strip()

        # Clean up Gemini markdown if present
        if translated_content.startswith("```"):
            lines = translated_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            translated_content = "\n".join(lines)

        output_filename = os.path.splitext(message.document.file_name)[0] + "_Hinglish.ass"
        output_path = os.path.join(download_dir, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(translated_content)

        await msg.edit("<code>Translation completed! Uploading... 🚀</code>")
        await upload_doc(message, msg, 0, output_filename, output_path)

    except Exception as e:
        LOGGER.error(f"Error during translation: {e}")
        await msg.edit(f"❌ <b>An error occurred during translation:</b>\n<code>{e}</code>")
    finally:
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass
        if 'output_path' in locals() and os.path.exists(output_path):
            try: os.remove(output_path)
            except: pass
