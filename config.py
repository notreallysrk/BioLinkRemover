#This code was published by @MightyAyush on github.com/mightyayush
import os
from dotenv import load_dotenv

load_dotenv()

def get_env_int(key, default=None):
    val = os.getenv(key)
    try:
        return int(val.strip()) if val and val.strip() else default
    except (TypeError, ValueError):
        return default

def get_env_list(key, default=None):
    if default is None:
        default = []
    val = os.getenv(key)
    if not val:
        return default
    
    val = val.strip()
    if val.startswith('[') and val.endswith(']'):
        val = val[1:-1]
        
    res = []
    for x in val.split(','):
        x_clean = x.strip()
        if x_clean.replace("-", "").isdigit():
            res.append(int(x_clean))
    return res

API_ID = get_env_int("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = get_env_int("OWNER_ID")
SUDO_USERS = list(dict.fromkeys(([OWNER_ID] if OWNER_ID else []) + get_env_list("SUDO_USERS")))

MONGO_DB = os.getenv("MONGO_DB")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "BioLinkRemover")

LOGGER_GROUP = get_env_int("LOGGER_GROUP")
DATABASE_CHANNEL = LOGGER_GROUP

DIRTY_WORDS = [
    "pussy", "porn", "xxx", "sex", "crypto double", "earn free btc", 
    "free money", "scam", "investment", "invest here", "easy money", 
    "casino", "gamble", "onlyfans", "sugar daddy", "sugar mommy"
]

DIRTY_SITES = [
    "bit.ly", "tinyurl.com", "t.co", "shorturl.at", "cutt.ly", "linktr.ee"
]

# Runtime tuning (safe defaults for a single Heroku worker).
HANDLER_WORKERS = max(4, min(get_env_int("HANDLER_WORKERS", 16), 64))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
