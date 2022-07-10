from pyrogram import Client
from Codexun.tgcalls import client as USER
from pyrogram import filters
from pyrogram.types import Chat, Message, User
from Codexun.config import (
    BOT_USERNAME,
)

@USER.on_message(filters.text & filters.private & ~filters.me & ~filters.bot)
async def pmPermit(client: USER, message: Message):
  await USER.send_message(message.chat.id,"ʜᴇʏ 🍑 ɪ ᴀᴍ ᴛʜᴇ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴏꜰ ᴍᴜꜱɪᴄ ʙᴏᴛ, ᴅɪᴅɴ'ᴛ ʜᴀᴠᴇ ᴛɪᴍᴇ ᴛᴏ ᴛᴀʟᴋ ᴡɪᴛʜ ʏᴏᴜ 🙂 ᴋɪɴᴅʟʏ ᴊᴏɪɴ @official_lucky01 ꜰᴏʀ ɢᴇᴛᴛɪɴɢ ꜱᴜᴘᴘᴏʀᴛ\n\nᴘᴏᴡᴇʀᴇᴅ ʙʏ @TeraYaarHooMai")
  return
