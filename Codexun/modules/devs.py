import os
import sys
import shutil
import re
import subprocess
import traceback
from inspect import getfullargspec
from io import StringIO
from time import time

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Codexun import app, OWNER
from Codexun.config import OWNER_ID, BOT_NAME, UPSTREAM_REPO, UPSTREAM_BRANCH
from Codexun.database.chats import blacklist_chat, blacklisted_chats, whitelist_chat
from Codexun.utils.decorators import sudo_users_only
from Codexun.utils.decorators import errors
from Codexun.utils.filters import command
from Codexun.modules import check_heroku
from Codexun.database.functions import start_restart_stage


@app.on_message(command(["rebootmusic", "restart"]) & filters.user(OWNER_ID))
@check_heroku
async def gib_restart(client, message, hap):
    msg_ = await message.reply_text(f"🍒 ʀᴇꜱᴛᴀʀᴛɪɴɢ..\n\nɪᴛ ᴡɪʟʟ ʙᴇ ᴛᴀᴋᴇ ꜰᴇᴡ ꜱᴇᴄᴏɴᴅꜱ ᴛᴏ ꜱᴛᴀʀᴛ ᴀɢᴀɪɴ, ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...\n\n**ʙᴏᴛ - {BOT_NAME}** 🍑")
    hap.restart()


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})

@Client.on_message(command("update") & filters.user(OWNER))
@errors
async def update(_, message: Message):
    m = subprocess.check_output(["git", "pull"]).decode("UTF-8")
    if str(m[0]) != "A":
        x = await message.reply_text("🍑 ꜰᴏᴜɴᴅ ᴜᴘᴅᴀᴛᴇ! ᴜᴘᴅᴀᴛɪɴɢ...")
        await start_restart_stage(x.chat.id, x.message_id)
        os.execvp("python3", ["python3", "-m", "Codexun"])
    else:
        await message.reply_text("ʙᴏᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ **ᴜᴘ ᴛᴏ ᴅᴀᴛᴇ** ᴍᴏᴅᴇ ᴡɪᴛʜ **[ʟᴀᴛᴇꜱᴛ ᴠᴇʀꜱɪᴏɴ](https://github.com/mrluckyxd/fortest)**", disable_web_page_preview=True)
        
async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(command(["exec", "em"]) & ~filters.edited)
@sudo_users_only
async def executor(client, message):
    if len(message.command) < 2:
        return await edit_or_reply(
            message, text="🍑 ᴘʟᴇᴀꜱᴇ ɢɪʙ ᴍᴇ ꜱᴏᴍᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴇxᴄᴜᴛᴇ"
        )
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await message.delete()
    t1 = time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = f"**ᴏᴜᴛᴘᴜᴛ**:\n\n```{evaluation.strip()}```"
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation.strip()))
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="🍒", callback_data=f"runtime {t2-t1} Seconds")]]
        )
        await message.reply_document(
            document=filename,
            caption=f"**ɪɴᴘᴜᴛ:**\n`{cmd[0:980]}`\n\n**ᴏᴜᴛᴘᴜᴛ:**\n`ᴀᴛᴛᴀᴄʜᴇᴅ ᴅᴏᴄᴜᴍᴇɴᴛ`",
            quote=False,
            reply_markup=keyboard,
        )
        await message.delete()
        os.remove(filename)
    else:
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏳",
                        callback_data=f"runtime {round(t2-t1, 3)} Seconds",
                    )
                ]
            ]
        )
        await edit_or_reply(message, text=final_output, reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"runtime"))
async def runtime_func_cq(_, cq):
    runtime = cq.data.split(None, 1)[1]
    await cq.answer(runtime, show_alert=True)
