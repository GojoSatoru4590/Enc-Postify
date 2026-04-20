import os
import asyncio
import re
import httpx
from p2d_deepseek import DeepSeekClient
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from .. import LOGGER, download_dir
from ..utils.uploads.telegram import upload_doc
from ..utils.database.access_db import db

SYSTEM_PROMPT = "Strictly translate English text into natural Hinglish (Hindi + English). Rule: Do not change any tags, timing, or symbols. Maintain the original line-by-line structure. Only return the translated content without any explanations."

TRANSLATE_PIC = "https://graph.org/file/600586a9a49029c2e98f1-90c27ea7986142ea7a.jpg"
TRANSLATE_TEXT = "✨ ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴛʀᴀɴsʟᴀᴛɪᴏɴ ᴇɴɢɪɴᴇ ✨\nᴘʟᴇᴀsᴇ sᴇʟᴇᴄᴛ ᴀ ᴍᴏᴅᴇʟ ᴛᴏ sᴛᴀʀᴛ ʜɪɴɢʟɪsʜ ᴛʀᴀɴsʟᴀᴛɪᴏɴ."

# Temporary storage for file metadata linked to message ID
translation_data = {}

SETUP_GUIDE_TEXT = (
    "✨ ʜᴏᴡ ᴛᴏ sᴇᴛ ᴜᴘ ʏᴏᴜʀ ᴛʀᴀɴsʟᴀᴛɪᴏɴ ᴇɴɢɪɴᴇ ✨\n"
    "🚀 ᴅᴇᴇᴘsᴇᴇᴋ ɪs ғʀᴇᴇ ᴀɴᴅ ʀᴇǫᴜɪʀᴇs ɴᴏ ᴋᴇʏ!\n\n"
    "𝟷️⃣ [ᴄʟɪᴄᴋ ʜᴇʀᴇ ғᴏʀ ɢʀᴏǫ ᴋᴇʏ](https://console.groq.com/keys)\n"
    "👉 sᴇɴᴅ ʏᴏᴜʀ ᴋᴇʏ ᴜsɪɴɢ /set_groq ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ɢʀᴏǫ."
)

SETUP_GUIDE_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close_translator")]
])

TRANSLATE_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("ᴅᴇᴇᴘsᴇᴇᴋ ᴇxᴘᴇʀᴛ 🧠", callback_data="trans_deepseek_free")
    ],
    [
        InlineKeyboardButton("ʟʟᴀᴍᴀ 𝟹.𝟹 (ɢʀᴏǫ) 🚀", callback_data="trans_llama3_groq"),
        InlineKeyboardButton("ᴍɪxᴛʀᴀʟ (ɢʀᴏǫ) 🌀", callback_data="trans_mixtral_groq")
    ],
    [
        InlineKeyboardButton("ʟʟᴀᴍᴀ 𝟹.𝟷 𝟾ʙ (ɢʀᴏǫ) ⚡", callback_data="trans_llama31_groq"),
        InlineKeyboardButton("ʜᴏᴡ ᴛᴏ ᴛʀᴀɴsʟᴀᴛᴇ? ❓", callback_data="how_to_translate")
    ]
])

def parse_srt(content):
    blocks = re.split(r'\n\s*\n', content.strip())
    parsed = []
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            parsed.append({
                'index': lines[0],
                'timestamp': lines[1],
                'text': '\n'.join(lines[2:])
            })
        else:
            parsed.append({'raw': block})
    return parsed

async def translate_deepseek(chunk_text):
    if not chunk_text.strip():
        return chunk_text

    try:
        client = DeepSeekClient()
        prompt = f"{SYSTEM_PROMPT}\n\nCONTENT TO TRANSLATE:\n{chunk_text}"

        # Enable thinking and use expert model as requested
        response = await client.chat(
            prompt=prompt,
            thinking=True,
            model="expert"
        )

        if response:
            translated_text = response.strip()
            translated_text = re.sub(r'```[a-z]*\n|```', '', translated_text)
            return translated_text
        return "❌ DeepSeek Error: Empty response."
    except Exception as e:
        return f"❌ DeepSeek Error: {str(e)}"

def parse_ass(content):
    lines = content.splitlines()
    header = []
    events = []
    in_events = False
    for line in lines:
        if line.strip().lower().startswith('[events]'):
            in_events = True
            header.append(line)
            continue
        if not in_events:
            header.append(line)
        else:
            if line.strip().startswith('Dialogue:'):
                parts = line.split(',', 9)
                if len(parts) == 10:
                    events.append({'prefix': parts[0:9], 'text': parts[9]})
                else:
                    events.append({'raw': line})
            else:
                events.append({'raw': line})
    return header, events


async def translate_groq(chunk_text, api_key, model_name):
    if not chunk_text.strip():
        return chunk_text

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": chunk_text}
        ],
        "temperature": 0.2
    }

    async with httpx.AsyncClient() as client:
        for attempt in range(2):
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=60.0)
                if response.status_code == 200:
                    data = response.json()
                    translated_text = data['choices'][0]['message']['content'].strip()
                    translated_text = re.sub(r'```[a-z]*\n|```', '', translated_text)
                    return translated_text
                else:
                    return f"❌ Groq Error: {response.status_code} - {response.text}"
            except Exception as e:
                if attempt == 0:
                    await asyncio.sleep(2)
                    continue
                return f"❌ Groq Error: {str(e)}"

@Client.on_message(filters.command("translate") & filters.private)
async def translate_cmd_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    if not message.reply_to_message:
        await message.reply_text("❌ Please reply to a .ass or .srt file with /translate")
        return

    replied = message.reply_to_message
    if not (replied.document and replied.document.file_name and replied.document.file_name.lower().endswith((".ass", ".srt"))):
        await message.reply_text("❌ Please reply to a valid .ass or .srt file.")
        return

    # Check for API Keys - only if we want to enforce it, but DeepSeek is free.
    # Let's show the translate options directly.

    sent_msg = await message.reply_photo(
        photo=TRANSLATE_PIC,
        caption=TRANSLATE_TEXT,
        reply_markup=TRANSLATE_BUTTONS,
        has_spoiler=True
    )

    # Store file metadata indexed by a unique chat_message key to prevent collisions
    unique_key = f"{replied.chat.id}_{sent_msg.id}"
    translation_data[unique_key] = {
        'file_id': replied.document.file_id,
        'file_name': replied.document.file_name,
        'chat_id': replied.chat.id,
        'message_id': replied.id,
        'user_id': user_id
    }

@Client.on_message(filters.command("set_groq") & filters.private)
async def set_groq_handler(bot: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /set_groq YOUR_KEY_HERE")
        return
    api_key = message.command[1]
    await db.set_groq_api_key(message.from_user.id, api_key)
    await message.reply_text("✅ Groq API Key saved successfully!")

@Client.on_message(filters.command("clear_api") & filters.private)
async def clear_api_handler(bot: Client, message: Message):
    await db.set_groq_api_key(message.from_user.id, None)
    await message.reply_text("✅ API Key cleared successfully!")

async def process_translation(bot, cb, model_type, model_name):
    # This will be called from callbacks_.py
    user_id = cb.from_user.id

    if model_type == "groq":
        api_key = await db.get_groq_api_key(user_id)
        translate_func = translate_groq
        if not api_key:
            await cb.answer(f"❌ {model_type.capitalize()} API Key Missing!", show_alert=True)
            return
    elif model_type == "deepseek":
        api_key = None
        translate_func = lambda chunk, k, m: translate_deepseek(chunk)
    else:
        await cb.answer("❌ Invalid model type!", show_alert=True)
        return

    # 1. Try to get file info from temporary storage (Fixes "File Not Found")
    unique_key = f"{cb.message.chat.id}_{cb.message.id}"
    file_data = translation_data.get(unique_key)
    replied = None

    if file_data:
        file_id = file_data['file_id']
        file_name = file_data['file_name']
        try:
            replied = await bot.get_messages(file_data['chat_id'], file_data['message_id'])
        except Exception as e:
            LOGGER.error(f"Error fetching message from translation_data: {e}")
            replied = None
    else:
        # 2. Fallback to reply-chain logic
        cmd_msg = cb.message.reply_to_message
        if cmd_msg and cmd_msg.reply_to_message:
            replied = cmd_msg.reply_to_message
            if replied.document and replied.document.file_name and replied.document.file_name.lower().endswith((".ass", ".srt")):
                file_id = replied.document.file_id
                file_name = replied.document.file_name
            else:
                await cb.answer("❌ Please reply to a valid .ass or .srt file.", show_alert=True)
                return
        else:
            await cb.answer("❌ Original file not found. Please try /translate again.", show_alert=True)
            return

    await cb.message.delete()
    status_msg = await bot.send_message(user_id, "⏳ [𝐀𝐈 𝐏𝐫𝐨𝐜ᴇ𝐬𝐬ɪɴ𝐠] : 𝐑𝐞𝐚𝐝𝐢𝐧𝐠 𝐟𝐢𝐥𝐞 𝐚𝐧𝐝 𝐬𝐭ᴀ𝐫ᴛɪ𝐧𝐠 ᴛ𝐫𝐚𝐧𝐬𝐥𝐚𝐭𝐢𝐨𝐧...")

    file_path = await bot.download_media(
        message=file_id,
        file_name=os.path.join(download_dir, file_name)
    )

    # Clean up storage
    if unique_key in translation_data:
        del translation_data[unique_key]

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        is_srt = file_path.lower().endswith(".srt")
        translated_content = ""

        if is_srt:
            blocks = re.split(r'\n\s*\n', content.strip())
            # Micro-chunks: 5 lines/blocks to stay within 300-400 tokens
            chunk_size = 5
            total_chunks = (len(blocks) + chunk_size - 1) // chunk_size
            translated_blocks = []
            for i in range(0, len(blocks), chunk_size):
                await status_msg.edit(f"⏳ [𝐀𝐈 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠] : Translating chunk {(i//chunk_size)+1}/{total_chunks}...")
                chunk = "\n\n".join(blocks[i : i + chunk_size])

                try:
                    res = await translate_func(chunk, api_key, model_name)
                except Exception as e:
                    res = f"❌ Error: {e}"

                if res.startswith("❌"):
                    await status_msg.edit(res)
                    return

                translated_blocks.append(res)
                if model_type == "groq":
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(1) # Small breather for deepseek free
            translated_content = "\n\n".join(translated_blocks)
        else:
            header, events = parse_ass(content)

            # Subtitle Rendering Fixes: Force PlayResX: 1920, PlayResY: 1080 and Fontsize: 60
            new_header = []
            script_info_found = False
            playresx_found = False
            playresy_found = False

            for line in header:
                if line.strip().lower().startswith('[script info]'):
                    script_info_found = True
                    new_header.append(line)
                    continue

                if line.strip().startswith('PlayResX:'):
                    new_header.append('PlayResX: 1920')
                    playresx_found = True
                    continue

                if line.strip().startswith('PlayResY:'):
                    new_header.append('PlayResY: 1080')
                    playresy_found = True
                    continue

                if line.strip().startswith('Style:'):
                    # Style: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
                    parts = line.split(',', 2)
                    if len(parts) >= 3:
                        # parts[0] is 'Style: Name'
                        # parts[1] is ' Fontname'
                        # parts[2] is everything else
                        remaining = parts[2].split(',', 1)
                        if len(remaining) >= 2:
                            # remaining[0] is ' Fontsize'
                            # remaining[1] is the rest
                            new_style = f"{parts[0]},Arial,60,{remaining[1]}"
                            new_header.append(new_style)
                        else:
                            new_header.append(line)
                    else:
                        new_header.append(line)
                    continue

                new_header.append(line)

            if script_info_found:
                # Insert missing PlayRes after [Script Info]
                idx = -1
                for i, line in enumerate(new_header):
                    if line.strip().lower().startswith('[script info]'):
                        idx = i
                        break
                if idx != -1:
                    if not playresy_found:
                        new_header.insert(idx + 1, 'PlayResY: 1080')
                    if not playresx_found:
                        new_header.insert(idx + 1, 'PlayResX: 1920')

            header = new_header

            # Micro-chunks: 5 lines/events to stay within 300-400 tokens
            chunk_size = 5
            total_chunks = (len(events) + chunk_size - 1) // chunk_size
            final_events = []
            for i in range(0, len(events), chunk_size):
                await status_msg.edit(f"⏳ [𝐀𝐈 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠] : Translating chunk {(i//chunk_size)+1}/{total_chunks}...")
                chunk_lines = []
                for item in events[i : i + chunk_size]:
                    if 'text' in item:
                        chunk_lines.append(",".join(item['prefix']) + "," + item['text'])
                    else:
                        chunk_lines.append(item['raw'])

                chunk_text = "\n".join(chunk_lines)
                try:
                    res = await translate_func(chunk_text, api_key, model_name)
                except Exception as e:
                    res = f"❌ Error: {e}"

                if res.startswith("❌"):
                    await status_msg.edit(res)
                    return

                final_events.append(res)
                if model_type == "groq":
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(1) # Small breather for deepseek free
            translated_content = "\n".join(header) + "\n" + "\n".join(final_events)

        output_filename = os.path.splitext(file_name)[0] + "_Hinglish" + os.path.splitext(file_name)[1]
        output_path = os.path.join(download_dir, output_filename)
        with open(output_path, "w", encoding="utf-8-sig") as f:
            f.write(translated_content)

        caption = f"✅ Translated by AI (Hinglish)\nFile: <code>{output_filename}</code>"
        # If replied is still None (fallback failed), use cb.message as a last resort to send the file
        target_msg = replied if replied else cb.message
        await upload_doc(target_msg, status_msg, 0, output_filename, output_path, caption=caption)
    except Exception as e:
        LOGGER.error(f"Translation Error: {e}")
        await status_msg.edit(f"❌ Error: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)
        if 'output_path' in locals() and os.path.exists(output_path): os.remove(output_path)
