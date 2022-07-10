import asyncio

from pyrogram import Client, filters, __version__ as pyrover
from pyrogram.errors import FloodWait, UserNotParticipant
from pytgcalls import (__version__ as pytover)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest
from Codexun.utils.filters import command

from Codexun import BOT_NAME, BOT_USERNAME
from Codexun.config import BOT_USERNAME 
from Codexun.config import BOT_NAME
from Codexun.config import START_IMG

@Client.on_message(command("start") & filters.private & ~filters.edited)
async def start_(client: Client, message: Message):
    await message.reply_photo(
        photo=f"{START_IMG}",
        caption=f"""**ʜᴇʏ ʙᴀʙʏ, 🖤
   ᴛʜɪs ɪs [{BOT_NAME}](https://t.me/{BOT_USERNAME}) 🥀
 ᴀ ᴩᴏᴡᴇʀғᴜʟ ᴍᴜsɪᴄ ᴩʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ᴀɴᴅ ᴜsᴇғᴜʟ ғᴇᴀᴛᴜʀᴇs.

ᴀʟʟ ᴏғ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ʟɪsᴛᴇᴅ ɪɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ.**""",
    reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🍒 ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="cbcmnds"),
                    InlineKeyboardButton(
                        "ᴀʙᴏᴜᴛ 🍒", callback_data="cbabout")
                ],
                [
                    InlineKeyboardButton(
                        "✘ ʙᴀꜱɪᴄ ɢᴜɪᴅᴇ ✘", callback_data="cbguide")
                ],
                [
                    InlineKeyboardButton(
                        "🥺 ᴋɪᴅɴᴀᴘ ᴍᴇ ʙᴀʙᴜ 🥺", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
                ]
           ]
        ),
    )
