import os
import logging
from logging.handlers import RotatingFileHandler

# Bot Configuration
LOG_FILE_NAME = "bot.log"
PORT = '5010'
OWNER_ID = 6891095964

MSG_EFFECT = 5046509860389126442

SHORT_URL = "vplink.in" # shortner url 
SHORT_API = "b4c55b5464676e8a7bbf9e8903b00a289debbec3" 
SHORT_TUT = "https://t.me/HowToDownloadSnap/2"
VERIFY_COOLDOWN = int(os.environ.get("VERIFY_COOLDOWN", "30"))
VERIFY_REDIRECT_DELAY = int(os.environ.get("VERIFY_REDIRECT_DELAY", "5"))
VERIFY_LOG_CHANNEL = int(os.environ.get("VERIFY_LOG_CHANNEL", "0"))
VERIFY_ACCESS_HOURS = int(os.environ.get("VERIFY_ACCESS_HOURS", "4"))
SERVICE_URL = os.environ.get("SERVICE_URL", "")

# Bot Configuration
SESSION = "SnapXPagluBot"
TOKEN = os.environ.get("TOKEN", "")
API_ID = os.environ.get("API_ID", "")
API_HASH = os.environ.get("API_HASH", "")
WORKERS = 5

DB_URI = os.environ.get("DB_URI", "")
DB_NAME = "yato"

FSUBS = [[-1003759386278, True, 10]] # Force Subscription Channels [channel_id, request_enabled, timer_in_minutes]
# Database Channel (Primary)
DB_CHANNEL = -1003542287615   # just put channel id dont add ""
# Multiple Database Channels (can be set via bot settings)
# DB_CHANNELS = {
#     "-1002595092736": {"name": "Primary DB", "is_primary": True, "is_active": True},
#     "-1001234567890": {"name": "Secondary DB", "is_primary": False, "is_active": True}
# }
# Auto Delete Timer (seconds)
AUTO_DEL = 300
# Admin IDs
ADMINS = [6891095964]
# Bot Settings
DISABLE_BTN = True
PROTECT = True

# Messages Configuration
MESSAGES = {
    "START": "<b>›› ʜᴇʏ!!, {first} ~ <blockquote>ʟᴏᴠᴇ ᴘᴏʀɴʜᴡᴀ? ɪ ᴀᴍ ᴍᴀᴅᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ғɪɴᴅ ᴡʜᴀᴛ ʏᴏᴜ aʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ.</blockquote></b>",
    "FSUB": "<b><blockquote>›› ʜᴇʏ ×</blockquote>\n  ʏᴏᴜʀ ғɪʟᴇ ɪs ʀᴇᴀᴅʏ ‼️ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴜʙsᴄʀɪʙᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, sᴜʙsᴄʀɪʙᴇ ɴᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ғɪʟᴇs</b>",
    "ABOUT": "<b>›› ғᴏʀ ᴍᴏʀᴇ: @TuneBots \n <blockquote expandable>›› ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ: <a href='https://t.me/Snap_Lover8'>Cʟɪᴄᴋ ʜᴇʀᴇ</a> \n›› Nᴇᴡs Rᴏᴏᴍ: <a href='https://t.me/+NbpXnldC3AI2NTU1'>Cʟɪᴄᴋ ʜᴇʀᴇ</a> \n›› sɴᴀᴘ ʟᴏᴠᴇʀ: <a href='https://t.me/+5000jEnshVVmYzg1'>Cʟɪᴄᴋ ʜᴇʀᴇ</a> \n›› Dɪsᴋᴡᴀʟᴀ: <a href='https://t.me/+GHL_Gg64eBZlMTVl'>Cʟɪᴄᴋ ʜᴇʀᴇ</a> \n›› Tᴇʀᴀʙᴏx: <a href='https://t.me/+VoZbnEAO9CxhZWE1'>Cʟɪᴄᴋ ʜᴇʀᴇ</a> \n›› ᴅᴇᴠᴇʟᴏᴘᴇʀ: @SnapLoverXBot</b></blockquote>",
    "REPLY": "<b>For More Join - @Snap_Lover8</b>",
    "SHORT_MSG": "<b>📊 ʜᴇʏ {first}, \n\n‼️ ɢᴇᴛ ᴀʟʟ ꜰɪʟᴇꜱ ɪɴ ᴀ ꜱɪɴɢʟᴇ ʟɪɴᴋ ‼️\n\n ⌯ ʏᴏᴜʀ ʟɪɴᴋ ɪꜱ ʀᴇᴀᴅʏ, ᴋɪɴᴅʟʏ ᴄʟɪᴄᴋ ᴏɴ ᴏᴘᴇɴ ʟɪɴᴋ ʙᴜᴛᴛᴏɴ..</b>",
    "START_PHOTO": "https://graph.org/file/510affa3d4b6c911c12e3.jpg",
    "FSUB_PHOTO": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "SHORT_PIC": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "VERIFY_WARN_PHOTO": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "VERIFY_WARN_MSG": "<b>⚠️ Verification bypass detected!\nPlease wait {seconds} seconds and use your new verify link.\nAttempt: {attempt}/2</b>",
    "CHANNEL_LINK_PHOTO": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "CHANNEL_LINK_MSG": "<b>📢 Channel access link ready for <i>{channel_name}</i>.\n⏳ This join-request link will expire in {expire_minutes} minutes.\n👇 Tap button below to join.</b>",
    "REFER_PHOTO": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "REFER_MSG": "<b>🎁 Refer & Earn Program!\nInvite your friends and after successful join, both of you get 1 day premium.</b>\n\n🔗 {invite_link}",
    "DEFAULT_PROFILE_PIC": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "SHORT": "https://telegra.ph/file/8aaf4df8c138c6685dcee-05d3b183d4978ec347.jpg"
}

def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )
    file_handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
