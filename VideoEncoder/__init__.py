
from os import getenv
import logging
import os

# Force Absolute Path for Assets
BASE_DIR = os.getcwd()
ASSETS_DIR = os.path.join(BASE_DIR, 'Assets')
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR, exist_ok=True)

import time
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from pyrogram import Client

botStartTime = time.time()

if os.path.exists('config.env'):
    load_dotenv('config.env')

# Variables
api_id = int(getenv("API_ID"))
api_hash = getenv("API_HASH")
bot_token = getenv("BOT_TOKEN")

owner = list(set(int(x) for x in getenv("OWNER_ID").split()))
sudo_users = list(set(int(x) for x in getenv("SUDO_USERS", "").split()) if getenv("SUDO_USERS") else [])
everyone = list(set(int(x) for x in getenv("EVERYONE_CHATS", "").split()) if getenv("EVERYONE_CHATS") else [])
all_users = everyone + sudo_users + owner

try:
    log = int(getenv("LOG_CHANNEL"))
except:
    log = owner[0] if owner else None
    print('Fill log or give user/channel/group id atleast!')

# the logging things
if not os.path.isdir('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            'logs/logs.txt',
            backupCount=20,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

# Client
app = Client(
    "ChannelManagerBot",
    bot_token=bot_token,
    api_id=api_id,
    api_hash=api_hash,
    plugins={'root': os.path.join(__package__, 'plugins')},
    sleep_threshold=30,
    max_concurrent_transmissions=16,
    workers=32,
    ipv6=False)
