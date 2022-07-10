import aiofiles
import ffmpeg
import asyncio
import os
import shutil
import psutil
import subprocess
import requests
import aiohttp
import yt_dlp
import aiohttp
import random

from os import path
from typing import Union
from asyncio import QueueEmpty
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from PIL import ImageGrab
from typing import Callable

from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import InputAudioStream

from youtube_search import YoutubeSearch

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    Voice,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden


from Codexun.tgcalls import calls, queues
from Codexun.tgcalls.youtube import download
from Codexun.tgcalls import convert as cconvert
from Codexun.tgcalls.calls import client as ASS_ACC
from Codexun.database.queue import (
    get_active_chats,
    is_active_chat,
    add_active_chat,
    remove_active_chat,
    music_on,
    is_music_playing,
    music_off,
)

from Codexun import BOT_NAME, BOT_USERNAME
from Codexun import app
import Codexun.tgcalls
from Codexun.tgcalls import youtube
from Codexun.config import (
    DURATION_LIMIT,
    que,
    SUDO_USERS,
    BOT_ID,
    ASSNAME,
    ASSUSERNAME,
    ASSID,
    START_IMG,
    SUPPORT,
    UPDATE,
    BOT_NAME,
    BOT_USERNAME,
)
from Codexun.utils.filters import command
from Codexun.utils.decorators import errors, sudo_users_only
from Codexun.utils.administrator import adminsOnly
from Codexun.utils.errors import DurationLimitError
from Codexun.utils.gets import get_url, get_file_name
from Codexun.modules.admins import member_permissions


def others_markup(videoid, user_id):
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"resumevc"),
            InlineKeyboardButton(text="II", callback_data=f"pausevc"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"skipvc"),
            InlineKeyboardButton(text="▢", callback_data=f"stopvc"),
        ],[
            InlineKeyboardButton(text="✰ ᴍᴀɴᴀɢᴇ ✰", callback_data=f"cls"),
        ],
        
    ]
    return buttons


fifth_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("➋0", callback_data="first"),
            InlineKeyboardButton("❺0%", callback_data="second"),
            
        ],[
            
            InlineKeyboardButton("➓0%", callback_data="third"),
            InlineKeyboardButton("➊❺0%", callback_data="fourth"),
            
        ],[
            
            InlineKeyboardButton("➋00% ♡", callback_data="fifth"),
            
        ],[
            InlineKeyboardButton(text="◁ ɢᴏ ʙᴀᴄᴋ ▷", callback_data=f"cbmenu"),
        ],
    ]
)

fourth_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("20%", callback_data="first"),
            InlineKeyboardButton("50%", callback_data="second"),
            
        ],[
            
            InlineKeyboardButton("100%", callback_data="third"),
            InlineKeyboardButton("150% ♡", callback_data="fourth"),
            
        ],[
            
            InlineKeyboardButton("200%", callback_data="fifth"),
            
        ],[
            InlineKeyboardButton(text="◁ ɢᴏ ʙᴀᴄᴋ ▷", callback_data=f"cbmenu"),
        ],
    ]
)

third_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("20%", callback_data="first"),
            InlineKeyboardButton("50%", callback_data="second"),
            
        ],[
            
            InlineKeyboardButton("100% ♡", callback_data="third"),
            InlineKeyboardButton("150%", callback_data="fourth"),
            
        ],[
            
            InlineKeyboardButton("200%", callback_data="fifth"),
            
        ],[
            InlineKeyboardButton(text="◁ ɢᴏ ʙᴀᴄᴋ ▷", callback_data=f"cbmenu"),
        ],
    ]
)

second_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("20%", callback_data="first"),
            InlineKeyboardButton("50% ♡", callback_data="second"),
            
        ],[
            
            InlineKeyboardButton("100%", callback_data="third"),
            InlineKeyboardButton("150%", callback_data="fourth"),
            
        ],[
            
            InlineKeyboardButton("200%", callback_data="fifth"),
            
        ],[
            InlineKeyboardButton(text="◁ ɢᴏ ʙᴀᴄᴋ ▷", callback_data=f"cbmenu"),
        ],
    ]
)

first_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("20% ♡", callback_data="first"),
            InlineKeyboardButton("50%", callback_data="second"),
            
        ],[
            
            InlineKeyboardButton("100%", callback_data="third"),
            InlineKeyboardButton("150%", callback_data="fourth"),
            
        ],[
            
            InlineKeyboardButton("200%", callback_data="fifth"),
            
        ],[
            InlineKeyboardButton(text="◁ ɢᴏ ʙᴀᴄᴋ ▷", callback_data=f"cbmenu"),
        ],
    ]
)
highquality_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("ʟᴏᴡ Qᴜᴀʟɪᴛʏ", callback_data="low"),],
         [   InlineKeyboardButton("ᴍᴇᴅɪᴜᴍ Qᴜᴀʟɪᴛʏ", callback_data="medium"),
            
        ],[   InlineKeyboardButton("ʜɪɢʜ Qᴜᴀʟɪᴛʏ", callback_data="high"),
            
        ],[
            InlineKeyboardButton(text="◁ ʙᴀᴄᴋ", callback_data=f"cbmenu"),
            InlineKeyboardButton(text="ᴄʟᴏꜱᴇ ☪", callback_data=f"cls"),
        ],
    ]
)
lowquality_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("ʟᴏᴡ Qᴜᴀʟɪᴛʏ ◉", callback_data="low"),],
         [   InlineKeyboardButton("ᴍᴇᴅɪᴜᴍ Qᴜᴀʟɪᴛʏ", callback_data="medium"),
            
        ],[   InlineKeyboardButton("ʜɪɢʜ Qᴜᴀʟɪᴛʏ", callback_data="high"),
            
        ],[
            InlineKeyboardButton(text="◁ ʙᴀᴄᴋ", callback_data=f"cbmenu"),
            InlineKeyboardButton(text="ᴄʟᴏꜱᴇ ☪", callback_data=f"cls"),
        ],
    ]
)
mediumquality_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("ʟᴏᴡ Qᴜᴀʟɪᴛʏ", callback_data="low"),],
         [   InlineKeyboardButton("ᴍᴇᴅɪᴜᴍ Qᴜᴀʟɪᴛʏ ◉", callback_data="medium"),
            
        ],[   InlineKeyboardButton("ʜɪɢʜ Qᴜᴀʟɪᴛʏ", callback_data="high"),
            
        ],[
            InlineKeyboardButton(text="◁ ʙᴀᴄᴋ", callback_data=f"cbmenu"),
            InlineKeyboardButton(text="ᴄʟᴏꜱᴇ ☪", callback_data=f"cls"),
        ],
    ]
)

dbclean_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("ʏᴇꜱ, ᴘʀᴏᴄᴇᴇᴅ !", callback_data="cleandb"),],
        [    InlineKeyboardButton("ɴᴏᴘᴇ, ᴄᴀɴᴄᴇʟ !", callback_data="cbmenu"),
            
        ],[
            InlineKeyboardButton(text="◁ ɢᴏ ʙᴀᴄᴋ ▷", callback_data=f"cbmenu"),
        ],
    ]
)
menu_keyboard = InlineKeyboardMarkup(
    [
        [
            
            InlineKeyboardButton("▷", callback_data="resumevc"),
            InlineKeyboardButton("II", callback_data="pausevc"),
            InlineKeyboardButton("‣‣I", callback_data="skipvc"),
            InlineKeyboardButton("▢", callback_data="stopvc"),
            
        ],[
            InlineKeyboardButton(text="🍑 ᴠᴏʟᴜᴍᴇ", callback_data=f"fifth"),
             InlineKeyboardButton(text="Qᴜᴀʟɪᴛʏ 🍑", callback_data=f"high"),
        ],[
            InlineKeyboardButton(text="🍹 ᴄʟᴇᴀɴ ᴅʙ", callback_data=f"dbconfirm"),
             InlineKeyboardButton(text="ᴀʙᴏᴜᴛ 🍹", callback_data=f"nonabout"),
        ],[
             InlineKeyboardButton(text="🍑 ᴄʟᴏꜱᴇ ᴍᴇɴᴜ 🍑", callback_data=f"cls"),
        ],
    ]
)


@Client.on_callback_query(filters.regex("skipvc"))
async def skipvc(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            """
ᴏɴʟʏ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴍᴀɴᴀɢᴇᴇ ᴠᴏɪᴄᴇᴇ ᴄʜᴀᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴄᴀɴ ᴅᴏ ᴛʜɪꜱ.
""",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    chat_title = CallbackQuery.message.chat.title
    if await is_active_chat(chat_id):
            user_id = CallbackQuery.from_user.id
            await remove_active_chat(chat_id)
            user_name = CallbackQuery.from_user.first_name
            rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
            await CallbackQuery.answer()
            await CallbackQuery.message.reply(
                f"""
**ꜱᴋɪᴘ ʙᴜᴛᴛᴏɴ ᴜꜱᴇᴅ ʙʏ** {rpk}
• ɴᴏ ᴍᴏʀᴇ ꜱᴏɴɢꜱ ɪɴ Qᴜᴇᴜᴇ
`ʟᴇᴀᴠɪɴɢ ᴠᴄ ʙʏᴇ ʙʏᴇ..`
"""
            )
            await calls.pytgcalls.leave_group_call(chat_id)
            return
            await CallbackQuery.answer("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜱᴋɪᴘ.!", show_alert=True)     

@Client.on_callback_query(filters.regex("pausevc"))
async def pausevc(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "ᴏɴʟʏ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴍᴀɴᴀɢᴇ ᴠᴄ ʀɪɢʜᴛꜱ ᴄᴀɴ ᴅᴏ ᴛʜɪꜱ.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
        if await is_music_playing(chat_id):
            await music_off(chat_id)
            await calls.pytgcalls.pause_stream(chat_id)
            await CallbackQuery.answer("ᴍᴜꜱɪᴄ ᴘᴀᴜꜱᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.", show_alert=True)
            
        else:
            await CallbackQuery.answer(f"ɴᴏᴛʜɪɴɢ ɪꜱ ᴘʟᴀʏɪɴɢ ᴏɴ ᴠᴄ ʙᴀʙʏ!", show_alert=True)
            return
    else:
        await CallbackQuery.answer(f"ɴᴏᴛʜɪɴɢ ɪꜱ ᴘʟᴀʏɪɴɢ ᴏɴ ᴠᴄ ʙᴀʙʏ!", show_alert=True)


@Client.on_callback_query(filters.regex("resumevc"))
async def resumevc(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            """
ᴏɴʟʏ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴍᴀɴᴀɢᴇ ᴠᴄ ʀɪɢʜᴛ ᴄᴀɴ ᴅᴏ ᴛʜɪꜱ.
""",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
        if await is_music_playing(chat_id):
            await CallbackQuery.answer(
                "Nothing is paused in the voice chat.",
                show_alert=True,
            )
            return
        else:
            await music_on(chat_id)
            await calls.pytgcalls.resume_stream(chat_id)
            await CallbackQuery.answer("ᴍᴜꜱɪᴄ ʀᴇꜱᴜᴍᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.", show_alert=True)
            
    else:
        await CallbackQuery.answer(f"ɴᴏᴛʜɪɴɢ ɪꜱ ᴘʟᴀʏɪɴɢ.", show_alert=True)


@Client.on_callback_query(filters.regex("stopvc"))
async def stopvc(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "ᴏɴʟʏ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴍᴀɴᴀɢᴇ ᴠᴄ ʀɪɢʜᴛ ᴄᴀɴ ᴅᴏ ᴛʜɪꜱ.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
        
        try:
            await calls.pytgcalls.leave_group_call(chat_id)
        except Exception:
            pass
        await remove_active_chat(chat_id)
        await CallbackQuery.answer("ᴍᴜꜱɪᴄ ꜱᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ.", show_alert=True)
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
        rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
        await CallbackQuery.message.reply(f"**• ᴍᴜꜱɪᴄ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴛᴏᴘᴇᴅ ʙʏ {rpk}.**")
    else:
        await CallbackQuery.answer(f"ɴᴏᴛʜɪɴɢ ɪꜱꜱ ᴘʟᴀʏɪɴɢ ᴏɴ ᴠᴄ.", show_alert=True)

@Client.on_callback_query(filters.regex("cleandb"))
async def cleandb(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "ᴏɴʟʏ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴍᴀɴᴀɢᴇᴇ ᴠᴄ ʀɪɢʜᴛ ᴄᴀᴀɴ ᴅᴏ ᴛʜɪꜱ.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
        
        try:
            await calls.pytgcalls.leave_group_call(chat_id)
        except Exception:
            pass
        await remove_active_chat(chat_id)
        await CallbackQuery.answer("ᴅʙ ᴄʟᴇᴀɴᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!", show_alert=True)
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
        rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
        await CallbackQuery.edit_message_text(
        f"✅ __Erased queues successfully__\n│\n╰ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʟᴇᴀɴᴇᴅ ʙʏ {rpk}",
        reply_markup=InlineKeyboardMarkup(
            [
            [InlineKeyboardButton("🍑 ᴄʟᴏꜱᴇ 🍑", callback_data="cls")]])
        
    )
    else:
        await CallbackQuery.answer(f"ɴᴏᴛʜɪɴɢ ɪꜱ ᴘʟᴀʏɪɴɢ ᴏɴ ᴠᴄ ʙᴀʙʏ.", show_alert=True)


@Client.on_callback_query(filters.regex("cbcmnds"))
async def cbcmnds(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""**{BOT_NAME} ᴄᴏᴍᴍᴀɴᴅꜱ 🍒**

• /play (song name) 
- ꜰᴏʀ ᴘʟᴀʏɪɴɢ ᴍᴜꜱɪᴄ

• /pause 
- ꜰᴏʀ ᴘᴀᴜꜱɪɴɢ ᴍᴜꜱɪᴄ

• /resume 
- ꜰᴏʀʀ ʀᴇꜱᴜᴍɪɴɢ ᴍᴜꜱɪᴄ

• /skip 
- ꜰᴏʀʀ ꜱᴋɪᴘᴘɪɴɢ ᴄᴜʀʀᴇɴᴛ ꜱᴏɴɢ

• /search (song name) 
- ꜰᴏʀ ꜱᴇᴀʀᴄʜɪɴɢ ᴍᴜꜱɪᴄ

• /song 
- ꜰᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴜꜱɪᴄ

ᴘᴏᴡᴇʀᴇ ʙʏ **@{UPDATE}** !""",
        reply_markup=InlineKeyboardMarkup(
            [
              [
                    InlineKeyboardButton(
                        "🍒 ᴍᴇɴᴜ", callback_data="cbstgs"),
                    InlineKeyboardButton(
                        "ꜱᴜᴅᴏ 🍒", callback_data="cbowncmnds")
                ],
              [InlineKeyboardButton("🍑 ʙᴀᴄᴋ ʜᴏᴍᴇ 🍑", callback_data="cbhome")]]
        ),
    )
@Client.on_callback_query(filters.regex("cbowncmnds"))
async def cbowncmnds(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""**🍒 ꜱᴜᴅᴏ ᴄᴏᴍᴍᴀɴᴅꜱ 🍒**

• /broadcast (massage)
- ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴍꜱɢ ʙʏ ᴛʜᴇ ʙᴏᴛ

• /gcast (massage) 
- ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴍꜱɢ ᴡɪᴛʜ ᴘɪɴ

• /restart 
- ʀᴇꜱᴛᴀʀᴛ ʙᴏᴛ ꜰʀᴏᴍ ꜱᴇʀᴠᴇʀ

• /exec
- ᴇxᴇᴄᴜᴛᴇ ᴀɴʏ ᴄᴍᴅ

• /stats
- ɢᴇᴛ ʙᴏᴛ ꜱᴛᴀᴛꜱ

• /ping 
- ᴘɪɴɢɪɴɢ ᴜᴘᴛɪᴍᴇ

• /update
- ᴜᴘᴅᴀᴛᴇ ʙᴏᴛ ᴡɪᴛʜ ʟᴀᴛᴇꜱᴛ ᴠᴇʀꜱɪᴏɴ

• /gban ᴏʀ /ungban
- ɢʟᴏʙᴀʟ ʙᴀɴ ꜱʏꜱᴛᴇᴍ

• /leaveall 
- ʟᴇᴀᴠɪɴɢ ᴀꜱꜱɪꜱᴛᴀɴᴛ ꜰʀᴏᴍ ᴀʟʟ ᴄʜᴀᴛꜱ

Pᴘᴏᴡᴇʀᴇᴅ ʙʏ **@{UPDATE}** !""",
        reply_markup=InlineKeyboardMarkup(
            [
              
              [InlineKeyboardButton("🍎 ʙᴀᴄᴋ ʜᴏᴍᴇ 🍎", callback_data="cbcmnds")]]
        ),
    )

@Client.on_callback_query(filters.regex("cbabout"))
async def cbabout(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""**ᴀʙᴏᴜᴛ {BOT_NAME} ʙᴏᴛ 🍒**

**[{BOT_NAME}](https://t.me/{BOT_USERNAME})** ɪꜱ ᴛʜᴇ ʙᴏᴛ ᴅᴇꜱɪɢɴᴇᴅ ʙʏ **@{UPDATE}** ꜰᴏʀ ᴘʟᴀʏɪɴɢ ʜɪɢʜ Qᴜᴀʟɪᴛʏ ᴀɴᴅ ᴜɴʙʀᴇᴀᴋᴀʙʟᴇ ᴍᴜꜱɪᴄ ɪɴ ᴜʀ ɢʀᴏᴜᴘꜱ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.

ᴛʜɪꜱ ʙᴏᴛ ʜᴇʟᴘꜱ ʏᴏᴜ ᴛᴏ ᴘʟᴀʏ ᴍᴜꜱɪᴄ, ᴛᴏ ꜱᴇᴀʀᴄʜ ᴍᴜꜱɪᴄ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ᴀɴᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴜꜱɪᴄ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ꜱᴇʀᴠᴇʀ ᴀɴᴅ ᴍᴀɴʏ ᴍᴏʀᴇ ꜰᴇᴀᴛᴜʀᴇꜱ ʀᴇʟᴀᴛᴇᴅ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ᴠᴏɪᴄᴇᴇ ᴄʜᴀᴛ ꜰᴇᴀᴛᴜʀᴇ.

**ᴀꜱꜱɪꜱᴛᴀɴᴛ :- @{ASSUSERNAME}**""",
        reply_markup=InlineKeyboardMarkup(
            [
              [
                    InlineKeyboardButton("🍒 ꜱᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT}"),
                    InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇꜱ 🍒", url=f"https://t.me/{UPDATE}")
                ],
            [InlineKeyboardButton("🍑 ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ", callback_data="cbtuto")],
            [InlineKeyboardButton("ʙᴀᴄᴋ ʜᴏᴍᴇ 🍑", callback_data="cbhome")]]
        ),
    )


@Client.on_callback_query(filters.regex("cbstgs"))
async def cbstgs(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""**ᴀʙᴏᴜᴛ ᴍᴡɴᴜ ʙᴜᴛᴛᴏɴꜱ 🍒**

ᴀꜰᴛᴇʀ ʏᴏᴜ ᴘʟᴀʏᴇᴅ ʏᴏᴜʀ ꜱᴏɴɢ ꜱᴏᴍᴇ ᴍᴇɴᴜ ʙᴜᴛᴛᴏɴꜱ ᴡɪʟʟ ᴄᴏᴍᴇꜱ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴍᴜꜱɪᴄ ᴘʟᴀʏɪɴɢ ᴏɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ. ᴛʜᴇʏ ᴀʀᴇ ᴀꜱ ꜰᴏʟʟᴏᴡꜱ :

• ▷ 
- ʀᴇꜱᴜᴍᴇ ᴍᴜꜱɪᴄ
• II 
- ᴘᴀᴜꜱᴇ ᴍᴜꜱɪᴄ
• ▢  
- ᴇɴᴅ ᴍᴜꜱɪᴄ
• ‣‣ 
- ꜱᴋɪᴘ ᴍᴜꜱɪᴄ

ʏᴏᴜ ᴄᴀɴ ᴀʟꜱᴏ ᴛʜɪꜱ ᴍᴇɴᴜ ᴛʜʀᴏᴜɢʜ /menu ᴀɴᴅ /settings ᴄᴏᴍᴍᴀɴᴅ.

**ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ**""",
        reply_markup=InlineKeyboardMarkup(
            [
            [InlineKeyboardButton("🍒 ʙᴀᴄᴋ ʜᴏᴍᴇ 🍒", callback_data="cbcmnds")]]
        ),
    )


@Client.on_callback_query(filters.regex("cbguide"))
async def cbguide(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""**ʀᴇᴀᴅ ʙᴀꜱɪᴄ ɢᴜɪᴅᴇ ᴄᴀʀᴇꜰᴜʟʟʏ**

• ꜰɪʀꜱᴛ ᴀᴅᴅ ᴛʜɪꜱ ʙᴏᴛ ɪɴ ᴜʀ ɢʀᴘ

• ᴍᴀᴋᴇ ᴀ ʙᴏᴛ ᴀᴅᴍɪɴ

• ɢɪᴠᴇᴇ ɴᴇᴇᴅᴇᴅ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪꜱꜱɪᴏɴ

• ᴛʏᴘᴇ /reload ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ

• ꜱᴛᴀʀᴛ ʏᴏᴜʀʀ ɢʀᴏᴜᴘꜱ ᴠᴏɪᴄᴇᴇ ᴄʜᴀᴛ

• ɴᴏᴡ ᴘʟᴀʏɪɴɢ ᴜʀʀ ꜱᴏɴɢ ᴀɴᴅᴅ ᴇɴᴊᴏʏ !""",
        reply_markup=InlineKeyboardMarkup(
            [[
              InlineKeyboardButton("ᴄᴏᴍᴍᴜɴ ᴇʀʀᴏʀ", callback_data="cberror")],
              [InlineKeyboardButton("ʙᴀᴄᴋ ʜᴏᴍᴇ", callback_data="cbhome")]]
        ),
    )


@Client.on_callback_query(filters.regex("cberror"))
async def cberror(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""**ᴍᴏꜱᴛʟʏ ꜰᴀᴄᴇᴅ ᴇʀʀᴏʀꜱ 🍒**

ᴍᴏꜱᴛʟʏ, ᴛʜᴇʀᴇ ᴡɪʟʟ ʙᴇᴇ ᴛʜᴇ ᴍᴀɪɴ ᴇʀʀᴏʀ ᴀʙᴏᴜᴛ ᴛᴏ ᴍᴜꜱɪᴄ ᴀꜱꜱɪꜱᴛᴀɴᴛ. ɪꜰ ʏᴏᴜ ᴀʀᴇ ꜰᴀᴄɪɴɢ ᴀɴʏ ᴛʏᴘᴇ ᴏꜰ ᴇʀʀᴏʀ ɪɴ ᴜʀ ɢʀᴘ ᴛʜᴇɴ ᴛʜᴀᴛ ᴛɪᴍᴇ ꜰɪʀꜱᴛ ᴛɪᴍᴇᴇ ᴍᴀᴋᴇᴇ ꜱᴜʀᴇ @{ASSUSERNAME} ɪꜱ ᴀᴡᴀɪʟᴀʙʟᴇ ɪɴ ᴜʀʀ ɢʀᴘ. ɪꜰ ɴᴏᴛ ᴛʜᴇɴ ᴀᴅᴅ ɪᴛ ᴀɴᴅ ʙᴇꜰᴏʀᴇ ᴛʜᴀᴛ ᴍᴀᴋᴇ ꜱᴜʀᴇᴇ ᴀʟꜱᴏ ɪᴛ ɪꜱꜱ ɴᴏᴛ ʙᴀɴɴᴇᴅᴅ ɪɴ ᴜʀ ᴄʜᴀᴛ.\n\n**Aꜱꜱɪꜱᴛᴀɴᴛ :- @{ASSUSERNAME}**\n\n**ᴛʜᴀɴᴋꜱ !**""",
        reply_markup=InlineKeyboardMarkup(
            [
            [
                    InlineKeyboardButton("ᴀꜱꜱɪꜱᴛᴀɴᴛ", url=f"https://t.me/{ASSUSERNAME}")
                ],
              [InlineKeyboardButton("ʙᴀᴄᴋ ʜᴏᴍᴇ", callback_data="cbguide")]]
        ),
    )


@Client.on_callback_query(filters.regex("cbtuto"))
async def cbtuto(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""**ʜᴇʀᴇ ɪꜱ ᴛʜᴇ ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ᴏꜰ ᴛʜᴇ ʟᴜᴄᴋʏ ᴍᴜꜱɪᴄ ʙᴏᴛ**

ɢᴜᴅ ɴᴇᴡꜱ ! ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴀʟʟᴏᴡ ᴛᴏ ʏᴏᴜʀ ᴏᴡɴ ᴍᴜꜱɪᴄ ʙᴏᴛ ʟɪᴋᴇ ᴛᴏ ᴛʜɪꜱ ᴏɴᴇ. ʏᴏᴜ ᴡɪʟʟ ʙᴇ ɢᴇᴛ ʀᴇᴘᴏ ʟɪɴᴋ ʙᴇʟᴏᴡ ᴊᴜꜱᴛ ᴄʟɪᴄᴋ ᴏɴ ɪᴛ ᴀɴᴅ ꜰᴏʟʟᴏᴡ ꜱᴛᴇᴘꜱ!

ɪꜰ ᴜʜʜ ᴅɪᴅ'ᴛ ᴋɴᴏᴡ ʜᴏᴡᴡ ᴛᴏ ᴍᴀᴋᴇ ʏᴏᴜʀ ᴏᴡɴ ʙᴏᴛ ᴛʜᴇɴ ᴄᴏɴᴛᴀᴄᴛ ᴜꜱ ᴀᴛ @TeraYaarHooMai ᴀɴᴅ ɢᴇᴛ ʜᴇʟᴘ ꜰʀᴏᴍ ᴜꜱ.

**🍒 ʀᴇᴘᴏ ʟɪɴᴋ : https://github.com/mrluckyxd/fortest**

**ᴛʜᴀɴᴋꜱ !""",
       reply_markup=InlineKeyboardMarkup(
            [[
                    InlineKeyboardButton("🍑 ɢᴇᴛ ʀᴇᴘᴏ 🍑", url=f"https://github.com/PavanMagar/CodexunMusicBot")
                ],
              [InlineKeyboardButton("🍒 ʙᴀᴄᴋ ʜᴏᴍᴇ 🍒", callback_data="cbabout")]]
        ),
    )

@Client.on_callback_query(filters.regex("cbhome"))
async def cbhome(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""**Welcome [{query.message.chat.first_name}](tg://user?id={query.message.chat.id})** 👋

This is the **[{BOT_NAME}](https://t.me/{BOT_USERNAME}) bot,** a bot for playing high quality and unbreakable music in your groups voice chat.

Just add me to your group & make as a admin with needed admin permissions to perform a right actions, now let's enjoy your music!

Use the given buttons for more 📍""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Commands", callback_data="cbcmnds"),
                    InlineKeyboardButton(
                        "About", callback_data="cbabout")
                ],
                [
                    InlineKeyboardButton(
                        "Basic Guide", callback_data="cbguide")
                ],
                [
                    InlineKeyboardButton(
                        "✚ Add Bot in Your Group ✚", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
                ]
                
           ]
        ),
    )

@Client.on_callback_query(filters.regex(pattern=r"^(cls)$"))
async def closed(_, query: CallbackQuery):
    from_user = query.from_user
    permissions = await member_permissions(query.message.chat.id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await query.answer(
            "You don't have enough permissions to perform this action.",
            show_alert=True,
        )
    await query.message.delete()

@Client.on_callback_query(filters.regex("cbmenu"))
async def cbmenu(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("you're an Anonymous Admin !\n\n» revert back to user account from admin rights.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("Only admins cam use this..!", show_alert=True)
    chat_id = query.message.chat.id
    if is_music_playing(chat_id):
          await query.edit_message_text(
              f"**🍒 {BOT_NAME} ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ**\n\n🍎 ɢʀᴏᴜᴘ : {query.message.chat.title}.\n🍹 ɢʀᴘ ɪᴅ : {query.message.chat.id}\n\n**ᴍᴀɴᴀɢᴇᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ ᴍᴜꜱɪᴄ ꜱʏꜱᴛᴇᴍ ʙʏ ᴘʀᴇꜱꜱɪɴɢ ʙᴜᴛᴛᴏɴꜱ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ 🍒**",

              reply_markup=menu_keyboard
         )
    else:
        await query.answer("ɴᴏᴛʜɪɴɢ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ꜱᴛʀᴇᴀᴍɪɴɢ", show_alert=True)



@Client.on_callback_query(filters.regex("high"))
async def high(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "Only admin with manage voice chat permission can do this.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
            
        await CallbackQuery.answer("Now streaming in high quality!", show_alert=True)
        await CallbackQuery.edit_message_text(
        f"**ᴍᴀɴᴀɢᴇᴇ ᴀᴜᴅɪᴏ Qᴜᴀʟɪᴛʏ 🔊**\n\nᴄʜᴏᴏꜱᴇ ʏᴏᴜʀ ᴏᴘᴛɪᴏɴ ꜰʀᴏᴍ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀᴜᴅɪᴏ Qᴜᴀʟɪᴛʏ.",
        reply_markup=highquality_keyboard
    )
    else:
        await CallbackQuery.answer(f"ɴᴏᴛʜɪɴɢ ɪꜱ ᴘʟᴀʏɪɴɢ ʙᴀʙʏ.", show_alert=True)


@Client.on_callback_query(filters.regex("low"))
async def low(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "Only admin with manage voice chat permission can do this.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
            
        await CallbackQuery.answer("Now streaming in low quality!", show_alert=True)
        await CallbackQuery.edit_message_text(
        f"**ᴍᴀɴᴀɢᴇ ᴀᴜᴅɪᴏ Qᴜᴀʟɪᴛʏ 🔊**\n\nᴄʜᴏᴏꜱᴇᴇ ʏᴏᴜʀ ᴏᴘᴛɪᴏɴ ꜰʀᴏᴍ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀᴜᴅɪᴏ Qᴜᴀʟɪᴛʏ.",
        reply_markup=lowquality_keyboard
    )
    else:
        await CallbackQuery.answer(f"ɴᴏᴛʜɪɴɢ ɪꜱꜱ ᴘʟᴀʏɪɴɢ ʙᴀʙʏ.", show_alert=True)

@Client.on_callback_query(filters.regex("medium"))
async def medium(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "Only admin with manage voice chat permission can do this.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
            
        await CallbackQuery.answer("Now streaming in medium quality!", show_alert=True)
        await CallbackQuery.edit_message_text(
        f"**ᴍᴀɴᴀɢᴇᴇ ᴀᴜᴅɪᴏ Qᴜᴀʟɪᴛʏ🔊**\n\nᴄʜᴏᴏꜱᴇᴇ ʏᴏᴜʀ ᴏᴘᴛɪᴏɴɴ ꜰʀᴏᴍ ɢɪᴠᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀᴜᴅɪᴏ Qᴜᴀʟɪᴛʏ .",
        reply_markup=mediumquality_keyboard
    )
    else:
        await CallbackQuery.answer(f"ɴᴏᴛʜɪɴɢ ɪꜱ ᴘʟᴀʏɪɴɢ ʙᴀʙʏ.", show_alert=True)

@Client.on_callback_query(filters.regex("fifth"))
async def fifth(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "Only admin with manage voice chat permission can do this.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
            
        await CallbackQuery.answer("Now streaming in 200% volume!", show_alert=True)
        await CallbackQuery.edit_message_text(
        f"**Manage Audio Volume 🔊**\n\nIf you want to manage volume through buttons then make a assistant Admin first.",
        reply_markup=fifth_keyboard
    )
    else:
        await CallbackQuery.answer(f"Nothing is playing on voice chat.", show_alert=True)

@Client.on_callback_query(filters.regex("fourth"))
async def fourth(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "Only admin with manage voice chat permission can do this.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
            
        await CallbackQuery.answer("Now streaming 150 volume!", show_alert=True)
        await CallbackQuery.edit_message_text(
        f"**Manage Audio Volume 🔊**\n\nIf you want to manage volume through buttons then make a assistant Admin first.",
        reply_markup=fourth_keyboard
    )
    else:
        await CallbackQuery.answer(f"Nothing is playing on voice chat.", show_alert=True)

@Client.on_callback_query(filters.regex("third"))
async def third(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "Only admin with manage voice chat permission can do this.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
            
        await CallbackQuery.answer("Now streaming in 100% volume!", show_alert=True)
        await CallbackQuery.edit_message_text(
        f"**Manage Audio Volume 🔊**\n\nIf you want to manage volume through buttons then make a assistant Admin first.",
        reply_markup=third_keyboard
    )
    else:
        await CallbackQuery.answer(f"Nothing is playing on voice chat.", show_alert=True)


@Client.on_callback_query(filters.regex("second"))
async def second(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "Only admin with manage voice chat permission can do this.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
            
        await CallbackQuery.answer("Now streaming in 50% volume!", show_alert=True)
        await CallbackQuery.edit_message_text(
        f"**Manage Audio Volume 🔊**\n\nIf you want to manage volume through buttons then make a assistant Admin first.",
        reply_markup=second_keyboard
    )
    else:
        await CallbackQuery.answer(f"Nothing is playing on voice chat.", show_alert=True)


@Client.on_callback_query(filters.regex("first"))
async def first(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "Only admin with manage voice chat permission can do this.",
            show_alert=True,
        )
    CallbackQuery.from_user.first_name
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
            
        await CallbackQuery.answer("Now streaming in 20% volume!", show_alert=True)
        await CallbackQuery.edit_message_text(
        f"**Manage Audio Volume 🔊**\n\nIf you want to manage volume through buttons then make a assistant Admin first.",
        reply_markup=first_keyboard
    )
    else:
        await CallbackQuery.answer(f"Nothing is playing on voice chat.", show_alert=True)

@Client.on_callback_query(filters.regex("nonabout"))
async def nonabout(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""**Here is the some basic information about to {BOT_NAME},From here you can simply contact us and can join us!**""",
        reply_markup=InlineKeyboardMarkup(
            [
              [
                    InlineKeyboardButton("🍒 ꜱᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT}"),
                    InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇꜱ 🍒", url=f"https://t.me/{UPDATE}")
                ],
              [InlineKeyboardButton("🍑 ʙᴀᴄᴋ ᴍᴇɴᴜ 🍑", callback_data="cbmenu")]]
        ),
    )


@Client.on_callback_query(filters.regex("dbconfirm"))
async def dbconfirm(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("you're an Anonymous Admin !\n\n» revert back to user account from admin rights.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("Only admins cam use this..!", show_alert=True)
    chat_id = query.message.chat.id
    if is_music_playing(chat_id):
          await query.edit_message_text(
              f"**Confirmation ⚠️**\n\nAre you sure want to end stream in {query.message.chat.title} and clean all Queued songs in db ?**",

              reply_markup=dbclean_keyboard
         )
    else:
        await query.answer("nothing is currently streaming", show_alert=True)

