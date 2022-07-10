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


from Codexun import BOT_NAME, BOT_USERNAME
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
    SUPPORT,
    UPDATE,
    BOT_NAME,
    START_IMG,
    BOT_USERNAME,
)
from Codexun.utils.filters import command
from Codexun.utils.decorators import errors, sudo_users_only
from Codexun.utils.administrator import adminsOnly
from Codexun.utils.errors import DurationLimitError
from Codexun.utils.gets import get_url, get_file_name
from Codexun.modules.admins import member_permissions


# plus
chat_id = None
DISABLED_GROUPS = []
useer = "NaN"
flex = {}


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 27:        
            text1 += " " + i
        elif len(text2) + len(i) < 25:        
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1,text2]

# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image = Image.open(f"./background.png")
    black = Image.open("etc/black.jpg")
    img = Image.open("etc/CodexunSq.png")
    image5 = changeImageSize(1280, 720, img)
    image1 = changeImageSize(1280, 720, image)
    image1 = image1.filter(ImageFilter.BoxBlur(10))
    image11 = changeImageSize(1280, 720, image)
    image1 = image11.filter(ImageFilter.BoxBlur(10))
    image2 = Image.blend(image1,black,0.6)

    # Cropping circle from thubnail
    image3 = image11.crop((280,0,1000,720))
    #lum_img = Image.new('L', [720,720] , 0)
   # draw = ImageDraw.Draw(lum_img)
   # draw.pieslice([(0,0), (720,720)], 0, 360, fill = 255, outline = "white")
   # img_arr =np.array(image3)
    #lum_img_arr =np.array(lum_img)
    #final_img_arr = np.dstack((img_arr,lum_img_arr))
    #image3 = Image.fromarray(final_img_arr)
    image3 = image3.resize((500,500))
    

    image2.paste(image3, (100,115))
    image2.paste(image5, mask = image5)

    # fonts
    font1 = ImageFont.truetype(r'etc/Codexun.otf', 30)
    font2 = ImageFont.truetype(r'etc/Codexun.otf', 60)
    font3 = ImageFont.truetype(r'etc/Codexun.otf', 49)
    font4 = ImageFont.truetype(r'etc/Mukta-ExtraBold.ttf', 35)

    image4 = ImageDraw.Draw(image2)

    # title
    title1 = truncate(title)
    image4.text((670, 280), text=title1[0], fill="white", font = font3, align ="left") 
    image4.text((670, 332), text=title1[1], fill="white", font = font3, align ="left") 

    # description
    views = f"Views : {views}"
    duration = f"Duration : {duration} minutes"
    channel = f"Request : LUCKY MUSICS BOT"

    image4.text((670, 410), text=views, fill="white", font = font4, align ="left") 
    image4.text((670, 460), text=duration, fill="white", font = font4, align ="left") 
    image4.text((670, 510), text=channel, fill="white", font = font4, align ="left")

    
    image2.save(f"final.png")
    os.remove(f"background.png")
    final = f"temp.png"
    return final
     



# play
@Client.on_message(
    command(["play", f"play@{BOT_USERNAME}"])
    & filters.group
    & ~filters.edited
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    global que
    global useer
    user_id = message.from_user.id
    if message.sender_chat:
        return await message.reply_text(
            "ʏᴏᴜ ᴀʀᴇ ᴀɴ **ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ**!__\n│\n╰ ʀᴇᴠᴇʀᴛ ʙᴀᴄᴋ ᴛᴏ ᴜʀ ᴀᴄᴄᴏᴜɴᴛ ꜰʀᴏᴍ ᴀᴅᴍɪɴ ʀɪɢʜᴛꜱ."
        )

    if message.chat.id in DISABLED_GROUPS:
        await message.reply(
            "**ᴍᴜꜱɪᴄ ᴘʟᴀʏᴇʀ ɪꜱ ᴛᴜʀɴᴇᴅ ᴏꜰꜰ, ᴀꜱᴋ ᴛʜᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴛᴜʀɴ ɪᴛ ᴏɴ!**__"
        )
      

        return
    lel = await message.reply("**ᴘʀᴏᴄᴄᴇꜱꜱɪɴɢ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ʙᴀʙʏ...✰**")

    chid = message.chat.id

    c = await app.get_chat_member(message.chat.id, BOT_ID)
    if c.status != "administrator":
        await lel.edit(
            f"**ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ꜰɪʀꜱᴛ !**"
        )
        return
    if not c.can_manage_voice_chats:
        await lel.edit(
            "**ɢɪᴠᴇ ᴍᴇ** ᴍᴀɴᴀɢᴇᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ **ᴀᴅᴍɪɴ ᴘᴇʀᴍɪꜱꜱɪᴏɴ.**"
        )
        return
    if not c.can_delete_messages:
        await lel.edit(
            "**ɢɪᴠᴇ ᴍᴇ** ᴅᴇʟᴇᴛᴇ ᴍꜱɢ **ᴀᴅᴍɪɴ ᴘᴇʀᴍɪꜱꜱɪᴏɴ.**"
        )
        return
    if not c.can_invite_users:
        await lel.edit(
            "**ɢɪᴠᴇ ᴍᴇ** ɪɴᴠɪᴛᴇ ᴜꜱᴇʀꜱ **ᴀᴅᴍɪɴ ʀɪɢʜᴛꜱ.**"
        )
        return
    if not c.can_restrict_members:
        await lel.edit(
            "**ɢɪʙ ᴍᴇ** ʙᴀɴ ᴜꜱᴇʀꜱ **ᴀᴅᴍɪɴ ʀɪɢʜᴛꜱ.**"
        )
        return

    try:
        b = await app.get_chat_member(message.chat.id, ASSID)
        if b.status == "kicked":
            await message.reply_text(
                f"🔴 {ASSNAME} (@{ASSUSERNAME}) ɪꜱ ʙᴀɴɴᴇᴅ ɪɴ ᴜʀ ᴄʜᴀᴛ **{message.chat.title}**\n\nᴜɴʙᴀɴ ɪᴛ ꜰɪʀꜱᴛ ᴛᴏ ᴜꜱᴇ ᴍᴜꜱɪᴄ"
            )
            return
    except UserNotParticipant:
        if message.chat.username:
            try:
                await ASS_ACC.join_chat(f"{message.chat.username}")
                await message.reply(
                    f"**@{ASSUSERNAME} ᴊᴏɪɴᴇᴅ !**",
                )
                await remove_active_chat(chat_id)
            except Exception as e:
                await message.reply_text(
                    f"**@{ASSUSERNAME} ꜰᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ** ᴀᴅᴅ @{ASSUSERNAME} ᴍᴀɴᴜᴀʟʟʏ ɪɴ ᴜʀ ɢʀᴏᴜᴘ.\n\n**ʀᴇᴀꜱᴏɴ**:{e}"
                )
                return
        else:
            try:
                invite_link = await message.chat.export_invite_link()
                if "+" in invite_link:
                    kontol = (invite_link.replace("+", "")).split("t.me/")[1]
                    link_bokep = f"https://t.me/joinchat/{kontol}"
                await ASS_ACC.join_chat(link_bokep)
                await message.reply(
                    f"**@{ASSUSERNAME} ᴊᴏɪɴᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ**",
                )
                await remove_active_chat(message.chat.id)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await message.reply_text(
                    f"**@{ASSUSERNAME} ꜰᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ** ᴀᴅᴅ @{ASSUSERNAME} ᴍᴀɴᴜᴀʟʟʏ ɪɴ ᴜʀ ɢʀᴏᴜᴘ.\n\n**ʀᴇᴀꜱᴏɴ**:{e}"
                )

    await message.delete()
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❄️ ᴠɪᴅᴇᴏꜱ ʟᴏɴɢᴇʀʀ ᴛʜᴇɴ {DURATION_LIMIT} ᴍɪɴᴜᴛᴇꜱ ᴀʀᴇ'ᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴘʟᴀʏ!"
            )

        file_name = get_file_name(audio)
        url = f"https://t.me/{UPDATE}"
        title = audio.title
        thumb_name = "https://telegra.ph/file/a7adee6cf365d74734c5d.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
    [
        
       [
            InlineKeyboardButton("✪ ᴄᴘᴀɴᴇʟ", callback_data="cbmenu"),
            InlineKeyboardButton("ᴀʙᴏᴜᴛ ✪", callback_data="nonabout"),
        ],[
            InlineKeyboardButton("✪ ᴄʟᴏꜱᴇ ᴍᴇɴᴜ ✪", callback_data="cls"),
        ],
        
    ]
)

        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await cconvert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            keyboard = InlineKeyboardMarkup(
    [
        
       [
            InlineKeyboardButton("✰ ᴄᴘᴀɴᴇʟ", callback_data="cbmenu"),
            InlineKeyboardButton("ᴀʙᴏᴜᴛ ✰", callback_data="nonabout"),
        ],[
            InlineKeyboardButton("✰ ᴄʟᴏꜱᴇ ✰", callback_data="cls"),
        ],
        
    ]
)

        except Exception as e:
            title = "NaN"
            thumb_name = "https://telegra.ph/file/a7adee6cf365d74734c5d.png"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="✰ ʏᴏᴜᴛᴜʙᴇ ✰", url="https://youtube.com")]]
            )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"💡 Videos longer than {DURATION_LIMIT} minutes aren't allowed to play!"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)

        def my_hook(d):
            if d["status"] == "downloading":
                percentage = d["_percent_str"]
                per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
                per = int(per)
                eta = d["eta"]
                speed = d["_speed_str"]
                size = d["_total_bytes_str"]
                bytesx = d["total_bytes"]
                if str(bytesx) in flex:
                    pass
                else:
                    flex[str(bytesx)] = 1
                if flex[str(bytesx)] == 1:
                    flex[str(bytesx)] += 1
                    try:
                        if eta > 2:
                            lel.edit(
                                f"ᴘʀᴏᴄᴄᴇꜱꜱɪɴɢ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ʙᴀʙʏ..✰"
                            )
                    except Exception as e:
                        pass
                if per > 250:
                    if flex[str(bytesx)] == 2:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"ᴘʀᴏᴄᴄᴇꜱꜱɪɴɢ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ʙᴀʙʏ..✰"
                            )
                        print(
                            f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
                if per > 500:
                    if flex[str(bytesx)] == 3:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"ᴘʀᴏᴄᴄᴇꜱꜱɪɴɢ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ʙᴀʙʏ..✰"
                            )
                        print(
                            f"ᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ ʙᴀʙʏ..✰"
                        )
                if per > 800:
                    if flex[str(bytesx)] == 4:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"ᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ ʙᴀʙʏ..✰"
                            )
                        print(
                            f"ᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ ʙᴀʙʏ..✰"
                        )
            if d["status"] == "finished":
                try:
                    taken = d["_elapsed_str"]
                except Exception as e:
                    taken = "00:00"
                size = d["_total_bytes_str"]
                lel.edit(
                    f"ᴏᴋᴋ ʙᴀʙʏʏ ɴᴏᴡ ᴘʟᴀʏɪɴɢ..✰"
                )
                print(f"ɴᴏᴡ ᴘʟᴀʏɪɴɢ ᴜʀ ꜱᴏɴɢ ʙᴀʙʏ..✰")

        loop = asyncio.get_event_loop()
        x = await loop.run_in_executor(None, download, url, my_hook)
        file_path = await cconvert(x)
    else:
        if len(message.command) < 2:
            return await lel.edit(
                "**ᴅᴏɴᴛ ʙᴇ ᴄʀᴀᴢʏ ✰ ɢɪᴠᴇ ᴍᴇ ᴀ ꜱᴏɴɢ ɴᴀᴍᴇ ᴛᴏ ᴘʟᴀʏ!\n\nꜰᴏʀ ᴇxᴀᴍᴘʟᴇ \n/play ᴛᴇʀɪ ɢᴀʟʟɪʏᴀ**"
            )
        await lel.edit("**✰ | ꜰɪɴᴅɪɴɢ...**")
        query = message.text.split(None, 1)[1]
        # print(query)
        await lel.edit("**✰ | ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...**")
        try:
            results = YoutubeSearch(query, max_results=5).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            await lel.edit(
                "• **ᴡᴛꜰ ꜱᴏɴɢ ɴᴏᴛ ꜰᴏᴜɴᴅ ʙᴀʙʏ..✰**"
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
    [
        
       [
            InlineKeyboardButton("✰ ᴄᴘᴀɴᴇʟ", callback_data="cbmenu"),
            InlineKeyboardButton("ᴀʙᴏᴜᴛ ✰", callback_data="nonabout"),
        ],[
            InlineKeyboardButton("✰ ᴄʟᴏꜱᴇ ✰", callback_data="cls"),
        ],
        
    ]
)

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"✪ ᴠɪᴅᴇᴏ ʟᴏɴɢᴇʀʀ ᴛʜᴇɴ {DURATION_LIMIT} ᴍɪɴᴜᴛᴇꜱꜱ ᴀʀᴇ'ᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴘʟᴀʏ!"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)

        def my_hook(d):
            if d["status"] == "downloading":
                percentage = d["_percent_str"]
                per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
                per = int(per)
                eta = d["eta"]
                speed = d["_speed_str"]
                size = d["_total_bytes_str"]
                bytesx = d["total_bytes"]
                if str(bytesx) in flex:
                    pass
                else:
                    flex[str(bytesx)] = 1
                if flex[str(bytesx)] == 1:
                    flex[str(bytesx)] += 1
                    try:
                        if eta > 2:
                            lel.edit(
                                f"**ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴜʀʀ ꜱᴏɴɢ**"
                            )
                    except Exception as e:
                        pass
                if per > 250:
                    if flex[str(bytesx)] == 2:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴜʀ ꜱᴏɴɢ..**"
                            )
                        print(
                            f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
                if per > 500:
                    if flex[str(bytesx)] == 3:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**Downloading given song..**"
                            )
                        print(
                            f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
                if per > 800:
                    if flex[str(bytesx)] == 4:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**Downloding give song..**"
                            )
                        print(
                            f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
            if d["status"] == "finished":
                try:
                    taken = d["_elapsed_str"]
                except Exception as e:
                    taken = "00:00"
                size = d["_total_bytes_str"]
                lel.edit(
                    f"ᴘʟᴀʏɪɴɢ ᴜʀ ꜱᴏɴɢ ʙᴀʙʏ..✰"
                )
                print(f"[{url_suffix}] Downloaded| Elapsed: {taken} seconds")

        loop = asyncio.get_event_loop()
        x = await loop.run_in_executor(None, download, url, my_hook)
        file_path = await cconvert(x)

    if await is_active_chat(message.chat.id):
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="**✰ ʟᴜᴄᴋʏ ᴍᴜꜱɪᴄꜱ ɴᴏᴡ ᴘʟᴀʏɪɴɢ ✰**\n\n**❄️ ʀᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** **{}**\n**🍒 ᴘʟᴀʏɪɴɢ ᴀᴛ : [{}..](https://t.me/terayaarhoomai)**".format(
                url, message.from_user.mention(), message.chat.title
            ),
        )
    else:
        try:
            await calls.pytgcalls.join_group_call(
                message.chat.id,
                InputStream(
                    InputAudioStream(
                        file_path,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )
        except Exception:
            return await lel.edit(
                "» ᴇʀʀᴏʀ ᴊᴏɪɴɪɴɢ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ. ᴍᴀᴋᴇᴇ ꜱᴜʀᴇᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴀʙʟᴇᴅ.\n\n ɪꜰ ʏᴇꜱ,ᴛʜᴇɴ ᴍᴜꜱɪᴄ ʙᴏᴛ ᴀꜱꜱɪꜱᴛᴀɴᴛ ɪꜱ ɴᴏᴛ ʙᴀɴɴᴇᴅ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ!"
            )


        await music_on(message.chat.id)
        await add_active_chat(message.chat.id)
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="**✰ ꜱᴛᴀʀᴛᴇᴅ ᴘʟᴀʏɪɴɢ ✰({})**\n\n**❄️ ʀᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** **{}**\n**🍒 ᴘʟᴀʏɪɴɢ ᴀᴛ : [{}..](https://t.me/terayaarhoomai)**".format(
                url, message.from_user.mention(), message.chat.title
            ),
        )

    os.remove("final.png")
    return await lel.delete()
