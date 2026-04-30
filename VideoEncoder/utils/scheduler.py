
import asyncio
from pyrogram import Client
from ..utils.database.channel_db import channel_db
from datetime import datetime
import json
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

SMALL_CAPS_MAP = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
)

def to_small_caps(text):
    return text.translate(SMALL_CAPS_MAP)

async def scheduler_loop(bot: Client):
    while True:
        try:
            pending_posts = await channel_db.get_pending_posts()
            for post in pending_posts:
                chat_ids = json.loads(post['chat_ids'])

                # Parse buttons
                reply_markup = None
                if post['buttons']:
                    rows = []
                    for line in post['buttons'].split("|"):
                        row = []
                        buttons = line.split(";") if ";" in line else [line]
                        for btn in buttons:
                            if " - " in btn:
                                text, url = btn.split(" - ", 1)
                                text = text.strip()
                                url = url.strip()
                                if "#g" in text: text = text.replace("#g", "✅").strip()
                                elif "#r" in text: text = text.replace("#r", "🔴").strip()
                                elif "#p" in text: text = text.replace("#p", "🔵").strip()
                                row.append(InlineKeyboardButton(to_small_caps(text), url=url))
                        if row: rows.append(row)
                    if rows: reply_markup = InlineKeyboardMarkup(rows)

                for chat_id in chat_ids:
                    try:
                        if post['media_type'] == "photo":
                            await bot.send_photo(chat_id, post['media_file_id'], caption=post['message_text'], reply_markup=reply_markup)
                        elif post['media_type'] == "video":
                            await bot.send_video(chat_id, post['media_file_id'], caption=post['message_text'], reply_markup=reply_markup)
                        elif post['media_type'] == "document":
                            await bot.send_document(chat_id, post['media_file_id'], caption=post['message_text'], reply_markup=reply_markup)
                        elif post['media_type'] == "animation":
                            await bot.send_animation(chat_id, post['media_file_id'], caption=post['message_text'], reply_markup=reply_markup)
                        else:
                            await bot.send_message(chat_id, post['message_text'], reply_markup=reply_markup)
                    except Exception as e:
                        print(f"Error sending scheduled post {post['id']} to {chat_id}: {e}")

                await channel_db.update_post_status(post['id'], 'sent')

        except Exception as e:
            print(f"Error in scheduler loop: {e}")

        await asyncio.sleep(60) # Check every minute
