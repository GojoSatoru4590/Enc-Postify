import asyncio
import dns.resolver
from pyrogram import idle
from . import app, log

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

async def main():
    from .utils.database.channel_db import channel_db
    await channel_db.init()
    await app.start()

    # Send hosted successfully message
    try:
        await app.send_message(chat_id=log, text='<b>ʜᴏsᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ʙᴀʙᴇʏ ✅</b>')
    except Exception as e:
        print(f"Error sending startup message: {e}")

    from .utils.scheduler import scheduler_loop
    asyncio.create_task(scheduler_loop(app))

    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
