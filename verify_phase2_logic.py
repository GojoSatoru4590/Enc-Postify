
import sys
import os
from datetime import datetime
import pytz

# Add current directory to path
sys.path.append(os.getcwd())

from VideoEncoder.utils.font_utils import apply_font
from VideoEncoder.utils.button_parser import parse_buttons

def test_fonts():
    print("Testing Fonts...")
    text = "Hello World 123"
    print(f"Original: {text}")
    print(f"Small Caps: {apply_font(text, 'ꜱᴍᴀʟʟ ᴄᴀᴘꜱ')}")
    print(f"Bold: {apply_font(text, '𝐁𝐨𝐥𝐝')}")
    print(f"Sans: {apply_font(text, '𝖲𝖺𝗇𝗌')}")

    assert apply_font("ABC", "ꜱᴍᴀʟʟ ᴄᴀᴘꜱ") == "ᴀʙᴄ"
    print("Fonts test passed!")

def test_button_parser():
    print("\nTesting Button Parser...")
    btn_text = "Google #g - https://google.com | Red #r - https://red.com && Primary #p - https://p.com"
    markup = parse_buttons(btn_text, "ꜱᴍᴀʟʟ ᴄᴀᴘꜱ")

    # Check rows
    assert len(markup.inline_keyboard) == 2
    # Check first row buttons
    assert len(markup.inline_keyboard[0]) == 2
    assert markup.inline_keyboard[0][0].text == "ɢᴏᴏɢʟᴇ 🟢"
    assert markup.inline_keyboard[0][1].text == "ʀᴇᴅ 🔴"
    # Check second row
    assert len(markup.inline_keyboard[1]) == 1
    assert markup.inline_keyboard[1][0].text == "ᴘʀɪᴍᴀʀʏ 🔵"

    print("Button parser test passed!")

def test_timezone_logic():
    print("\nTesting Timezone Logic...")
    import dateparser

    user_tz = "IST" # UTC+5:30
    input_time = "tomorrow 2:00 PM"

    # Simulate schedule_input_handler logic
    import pytz
    try:
        user_timezone = pytz.timezone(user_tz)
    except:
        # IST might need manual mapping if not in pytz common
        if user_tz == "IST":
            user_timezone = pytz.timezone("Asia/Kolkata")
        else:
            user_timezone = pytz.UTC

    dt = dateparser.parse(input_time, settings={'TIMEZONE': user_tz})
    print(f"Input: {input_time} ({user_tz})")
    print(f"Parsed Local: {dt}")

    localized_dt = user_timezone.localize(dt)
    utc_dt = localized_dt.astimezone(pytz.UTC)
    print(f"UTC DT: {utc_dt}")

    # Difference should be 5.5 hours
    diff = localized_dt.utcoffset().total_seconds() / 3600
    assert diff == 5.5

    print("Timezone logic test passed!")

if __name__ == "__main__":
    try:
        test_fonts()
        test_button_parser()
        test_timezone_logic()
        print("\nAll Phase 2 logic tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
