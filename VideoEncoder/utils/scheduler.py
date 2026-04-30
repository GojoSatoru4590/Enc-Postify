
import asyncio
from pyrogram import Client
from ..utils.database.channel_db import channel_db
from datetime import datetime
import json
import pytz
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .button_parser import parse_buttons

async def scheduler_loop(bot: Client):
    while True:
        try:
            # get_pending_posts currently uses datetime.now().isoformat() which is local.
            # We should probably change it to UTC in DB or handle it here.
            # Since we saved in UTC isoformat, we need to compare in UTC.

            async def get_pending_posts_utc():
                current_time = datetime.now(pytz.UTC).isoformat()
                return await channel_db._run_query('SELECT * FROM scheduled_posts WHERE status = "pending" AND scheduled_time <= ?', (current_time,), fetch=True)

            pending_posts = await get_pending_posts_utc()
            for post in pending_posts:
                chat_ids = json.loads(post['chat_ids'])
                user_id = post['user_id']
                settings = await channel_db.get_user_settings(user_id)

                # Parse buttons
                reply_markup = parse_buttons(post['buttons'], settings['font_style'])

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
