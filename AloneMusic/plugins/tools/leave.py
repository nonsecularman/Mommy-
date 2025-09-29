from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from config import LOGGER_ID
from AnonXMusic import app, userbot
from AnonXMusic.misc import SUDOERS
from AnonXMusic.utils.database import get_client


@app.on_message(filters.command(["leaveall1", "leaveall2", "leaveall3", "leaveall4", "leaveall5"]) & SUDOERS)
async def leave_ass(_, msg: Message):
    rep = await msg.reply_text("Running leave all...")
    left, failed = 0, 0
    assnum = msg.command[0][-1]
    ub = await get_client(assnum)
    async for dialog in ub.get_dialogs():
        if dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
            if dialog.chat.id == LOGGER_ID:
                continue
            try:
                await ub.leave_chat(dialog.chat.id)
                await asyncio.sleep(3)
                left += 1
            except:
                failed += 1
                continue
    await rep.edit_text(f"Left {left} chats, failed to leave {failed} chats.")
