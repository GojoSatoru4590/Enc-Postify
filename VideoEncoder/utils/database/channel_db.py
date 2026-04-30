
import aiosqlite
import os
import json
from datetime import datetime

class ChannelDB:
    def __init__(self, db_path='channel_manager.db'):
        self.db_path = db_path

    async def _run_query(self, query, params=(), fetch=False):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                if fetch:
                    return await cursor.fetchall()
                await db.commit()

    async def init(self, clean=False):
        async with aiosqlite.connect(self.db_path) as db:
            if clean:
                await db.execute('DROP TABLE IF EXISTS channels')
                await db.execute('DROP TABLE IF EXISTS scheduled_posts')
                await db.execute('DROP TABLE IF EXISTS draft_posts')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    chat_id INTEGER PRIMARY KEY,
                    chat_title TEXT,
                    chat_username TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chat_ids TEXT,
                    message_text TEXT,
                    media_file_id TEXT,
                    media_type TEXT,
                    buttons TEXT,
                    scheduled_time TIMESTAMP,
                    interval TEXT,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS draft_posts (
                    user_id INTEGER PRIMARY KEY,
                    message_text TEXT,
                    media_file_id TEXT,
                    media_type TEXT,
                    buttons TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    font_style TEXT DEFAULT 'ꜱᴍᴀʟʟ ᴄᴀᴘꜱ',
                    timezone TEXT DEFAULT 'UTC'
                )
            ''')
            await db.commit()

    async def get_user_settings(self, user_id):
        res = await self._run_query('SELECT * FROM user_settings WHERE user_id = ?', (user_id,), fetch=True)
        if res:
            return dict(res[0])
        # Default settings if not found
        return {'user_id': user_id, 'font_style': 'ꜱᴍᴀʟʟ ᴄᴀᴘꜱ', 'timezone': 'UTC'}

    async def update_user_settings(self, user_id, **kwargs):
        if not kwargs:
            return

        columns = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]

        async with aiosqlite.connect(self.db_path) as db:
            # Try to insert first to ensure user exists
            await db.execute('INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)', (user_id,))
            await db.execute(f'UPDATE user_settings SET {columns} WHERE user_id = ?', values)
            await db.commit()

    async def add_channel(self, chat_id, title, username):
        await self._run_query('INSERT OR REPLACE INTO channels (chat_id, chat_title, chat_username) VALUES (?, ?, ?)', (chat_id, title, username))

    async def get_channels(self):
        return await self._run_query('SELECT * FROM channels', fetch=True)

    async def remove_channel(self, chat_id):
        await self._run_query('DELETE FROM channels WHERE chat_id = ?', (chat_id,))

    async def save_draft(self, user_id, message_text=None, media_file_id=None, media_type=None, buttons=None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO draft_posts (user_id, message_text, media_file_id, media_type, buttons)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    message_text = COALESCE(?, message_text),
                    media_file_id = COALESCE(?, media_file_id),
                    media_type = COALESCE(?, media_type),
                    buttons = COALESCE(?, buttons)
            ''', (user_id, message_text, media_file_id, media_type, buttons, message_text, media_file_id, media_type, buttons))
            await db.commit()

    async def get_draft(self, user_id):
        res = await self._run_query('SELECT * FROM draft_posts WHERE user_id = ?', (user_id,), fetch=True)
        return res[0] if res else None

    async def delete_draft(self, user_id):
        await self._run_query('DELETE FROM draft_posts WHERE user_id = ?', (user_id,))

    async def add_scheduled_post(self, user_id, chat_ids, message_text, media_file_id, media_type, buttons, scheduled_time, interval=None):
        await self._run_query('''
            INSERT INTO scheduled_posts (user_id, chat_ids, message_text, media_file_id, media_type, buttons, scheduled_time, interval)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, json.dumps(chat_ids), message_text, media_file_id, media_type, buttons, scheduled_time, interval))

    async def get_pending_posts(self):
        current_time = datetime.now().isoformat()
        return await self._run_query('SELECT * FROM scheduled_posts WHERE status = "pending" AND scheduled_time <= ?', (current_time,), fetch=True)

    async def update_post_status(self, post_id, status):
        await self._run_query('UPDATE scheduled_posts SET status = ? WHERE id = ?', (status, post_id))

    async def update_scheduled_time(self, post_id, next_time):
         await self._run_query('UPDATE scheduled_posts SET scheduled_time = ? WHERE id = ?', (next_time, post_id))

channel_db = ChannelDB()
