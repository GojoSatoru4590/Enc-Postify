
import os
import time

from pyrogram.enums import ParseMode
from ... import app, download_dir, log, LOGGER, ASSETS_DIR


async def upload_to_tg(new_file, message, msg, caption=None, reply_markup=None):
    from ..database.access_db import db
    from ..encoding import get_duration, get_width_height, take_screenshot, compress_image
    # Variables
    c_time = time.time()
    filename = os.path.basename(new_file)
    duration = get_duration(new_file)

    # Thumbnail Logic
    user_id = message.from_user.id
    thumb = os.path.abspath(os.path.join(ASSETS_DIR, f'thumb_{user_id}.jpg'))
    is_fallback = False

    if not os.path.exists(thumb) or os.path.getsize(thumb) == 0:
        # Fallback to screenshot
        thumb = os.path.join(os.path.dirname(new_file), f"thumb_{user_id}.jpg")
        thumb = await take_screenshot(new_file, thumb)
        is_fallback = True

    # Ensure thumbnail is under 200KB for Telegram API
    if thumb:
        thumb = await compress_image(thumb)

    width, height = get_width_height(new_file)
    # Handle Upload
    try:
        if await db.get_upload_as_doc(message.from_user.id) is True:
            link = await upload_doc(message, msg, c_time, filename, new_file, thumb, caption, reply_markup)
        else:
            link = await upload_video(message, msg, new_file, filename,
                                      c_time, thumb, duration, width, height, caption, reply_markup)
    finally:
        # Cleanup fallback thumbnail
        if is_fallback and thumb and os.path.exists(thumb):
            try: os.remove(thumb)
            except: pass

    return link


async def upload_video(message, msg, new_file, filename, c_time, thumb, duration, width, height, caption=None, reply_markup=None):
    from ..display_progress import progress_for_pyrogram
    try:
        if thumb:
            print(f"DEBUG: Does file exist? {os.path.exists(thumb)}")
            print(f"DEBUG: Full path is: {thumb}")
        resp = await message.reply_video(
            new_file,
            supports_streaming=True,
            parse_mode=ParseMode.HTML,
            caption=caption or filename,
            thumb=thumb,
            duration=duration,
            width=width,
            height=height,
            reply_markup=reply_markup,
            progress=progress_for_pyrogram,
            progress_args=("Uploading ...", msg, c_time)
        )
        if resp:
            if thumb:
                print(f"DEBUG: Does file exist? {os.path.exists(thumb)}")
                print(f"DEBUG: Full path is: {thumb}")
            await app.send_video(log, resp.video.file_id, thumb=thumb,
                                 caption=caption or filename, duration=duration,
                                 width=width, height=height, parse_mode=ParseMode.HTML)

        return resp.link
    except Exception as e:
        LOGGER.error(f"Upload failed for {new_file} with thumb {thumb}. Error: {e}")
        return None


async def upload_doc(message, msg, c_time, filename, new_file, thumb=None, caption=None, reply_markup=None):
    from ..display_progress import progress_for_pyrogram
    try:
        if thumb:
            print(f"DEBUG: Does file exist? {os.path.exists(thumb)}")
            print(f"DEBUG: Full path is: {thumb}")
        resp = await message.reply_document(
            new_file,
            caption=caption or filename,
            thumb=thumb,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            progress=progress_for_pyrogram,
            progress_args=("Uploading ...", msg, c_time)
        )

        if resp:
            if thumb:
                print(f"DEBUG: Does file exist? {os.path.exists(thumb)}")
                print(f"DEBUG: Full path is: {thumb}")
            await app.send_document(log, resp.document.file_id, thumb=thumb, caption=caption or filename, parse_mode=ParseMode.HTML)

        return resp.link
    except Exception as e:
        LOGGER.error(f"Upload failed for {new_file} with thumb {thumb}. Error: {e}")
        return None
