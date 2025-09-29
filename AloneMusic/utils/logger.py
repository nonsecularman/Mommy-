from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ChatPermissions, Message
from AnonXMusic import app
from AnonXMusic.misc import SUDOERS
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from AnonXMusic import app, Userbot
from AnonXMusic.utils.database import get_assistant
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant, ChatAdminRequired
from pyrogram.types import Message, ChatPrivileges
import asyncio
from typing import Optional
from random import randint
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat
from pyrogram.enums import ParseMode
from AnonXMusic import app
from AnonXMusic.utils.database import is_on_off
from config import LOGGER_ID as LOG_GROUP_ID
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message, User, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import random


async def play_logs(message, streamtype):
    if await is_on_off(2):
        chat_members = await app.get_chat_members_count(message.chat.id)
        try:
            txt = message.text.split(None, 1)[1]
        except:
            txt = ""
        logger_text = f"""
<b>{app.mention} ᴘʟᴀʏ ʟᴏɢ</b>
╔════❰𝐏𝐋𝐀𝐘𝐈𝐍𝐆❱═══❍⊱❁۪۪
<b>◈ 𝐂𝐡𝐚𝐭 ➪ </b>{message.chat.title}
<b>◈ 𝐂𝐡𝐚𝐭 𝐈𝐝 ➪ </b> <code>{message.chat.id}</code>
<b>◈ 𝐔𝐬𝐞𝐫 ➪ </b> {message.from_user.mention}
<b>◈ 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞 ➪ </b> @{message.from_user.username}
<b>◈ 𝐈𝐝 ➪ </b> <code>{message.from_user.id}</code>
<b>◈ 𝐂𝐡𝐚𝐭 𝐋𝐢𝐧𝐤 ➪ </b> @{message.chat.username}
<b>◈ 𝐂𝗵𝗮𝘁 𝗠𝗲𝗺𝗯𝗲𝗿𝘀 ➪ </b> <code>{chat_members}</code>
<b>◈ 𝐒𝐞𝐚𝐫𝐜𝐡𝐞𝐝 ➪ </b> <code>{txt}</code>
<b>◈ 𝐁𝐲 ➪ </b> {streamtype}
╚═══❰ #𝐍𝐞𝐰𝐒𝐨𝐧𝐠 ❱══❍⊱❁۪۪"""
        if message.chat.id != LOG_GROUP_ID:
            try:
                await app.send_message(
                    chat_id=LOG_GROUP_ID,
                    text=logger_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except:
                pass
        return
