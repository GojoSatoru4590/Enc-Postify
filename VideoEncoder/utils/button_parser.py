
import re
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .font_utils import apply_font

def parse_buttons(button_text, font_style="ꜱᴍᴀʟʟ ᴄᴀᴘꜱ"):
    if not button_text:
        return None

    # Handle row separators: && or New Line
    row_lines = re.split(r'&&|\n', button_text)

    rows = []
    for line in row_lines:
        line = line.strip()
        if not line:
            continue

        row = []
        # Handle same-row separator: |
        buttons = line.split("|")
        for btn in buttons:
            btn = btn.strip()
            if " - " in btn:
                text, url = btn.split(" - ", 1)
                text = text.strip()
                url = url.strip()

                # Apply font first so that color tags (emojis) are not mangled if they were somehow in the map
                text = apply_font(text, font_style)

                # Handle color tags (check for both original and styled versions)
                text = text.replace("#g", "🟢").replace("#G", "🟢")
                text = text.replace("#ɢ", "🟢")

                text = text.replace("#r", "🔴").replace("#R", "🔴")
                text = text.replace("#ʀ", "🔴")

                text = text.replace("#p", "🔵").replace("#P", "🔵")
                text = text.replace("#ᴘ", "🔵")

                text = text.strip()

                row.append(InlineKeyboardButton(text, url=url))
        if row:
            rows.append(row)

    return InlineKeyboardMarkup(rows) if rows else None
