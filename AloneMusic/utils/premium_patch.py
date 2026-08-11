#
# Premium Emoji and Colored Buttons Monkeypatch for AloneMusic Bot
# Created by Antigravity AI
#

import asyncio
import json
import logging
import inspect
import aiohttp
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from pyrogram.errors import FloodWait

LOGGER = logging.getLogger("AloneMusic.premium_patch")
LOGGER.info("Initializing Premium Emojis and Colored Buttons Patch...")

# 1. Patch InlineKeyboardButton constructor to support style and custom_emoji_id
original_button_init = InlineKeyboardButton.__init__

EMOJI_MAP = {
    "🌟": "5409368076447657845",
    "🎵": "5409042015415448331",
    "🎶": "5409042015415448331",
    "🔇": "5406742103378115459",
    "🔊": "5409331062419502443",
    "🎤": "5409221983135085894",
    "🎙️": "5409221983135085894",
    "🎙": "5409221983135085894",
    "🔗": "5409032416163540795",
    "👤": "5408846628763217930",
    "🔓": "5409320020058584473",
    "🖕": "5449599971412171546",
    "❤️": "6266992763930158001",
    "✔️": "6267261061947200606",
    "☺️": "5440739140347907722",
    "🥺": "5197545864276495943",
    "🎀": "6190346894984613437",
    "🗑️": "5409320020058584473",
    "🗑": "5409320020058584473"
}

def patched_button_init(self, text, callback_data=None, url=None, web_app=None, login_url=None, user_id=None, switch_inline_query=None, switch_inline_query_current_chat=None, callback_game=None, style=None, icon_custom_emoji_id=None, **kwargs):
    text = str(text)
    
    # Auto-determine style based on button text/content
    if style is None:
        text_lower = text.lower()
        if any(w in text_lower for w in ["close", "stop", "cancel", "delete", "remove", "no", "reject", "🗑", "❌", "▢"]):
            style = "danger"
        elif any(w in text_lower for w in ["play", "resume", "next", "skip", "yes", "confirm", "approve", "start", "▷", "ii", "‣‣i", "↻"]):
            style = "success"
        else:
            style = "primary"

    # Auto-determine custom emoji ID based on emojis in the button text
    if icon_custom_emoji_id is None:
        text_lower = text.lower()
        
        # Check standard emoji map first
        for emo, eid in EMOJI_MAP.items():
            if emo in text:
                icon_custom_emoji_id = eid
                text = text.replace(emo, "").strip()
                break
                
        # Fallback to smart word/symbol mapping if still no emoji set
        if icon_custom_emoji_id is None:
            if any(w in text_lower for w in ["▷", "play", "resume", "start"]):
                icon_custom_emoji_id = "5409042015415448331"  # 🎵
                text = text.replace("▷", "").strip()
            elif any(w in text_lower for w in ["ii", "pause", "stop", "▢", "🔇"]):
                icon_custom_emoji_id = "5406742103378115459"  # Mute 🔇
                text = text.replace("II", "").replace("▢", "").strip()
            elif any(w in text_lower for w in ["skip", "‣‣i", "next"]):
                icon_custom_emoji_id = "5409025823388741707"  # 🎵
                text = text.replace("‣‣I", "").strip()
            elif any(w in text_lower for w in ["↻", "replay", "loop"]):
                icon_custom_emoji_id = "5409368076447657845"  # 🌟
                text = text.replace("↻", "").strip()
            elif any(w in text_lower for w in ["support", "chat", "group", "owner", "admin", "sudo"]):
                icon_custom_emoji_id = "5408846628763217930"  # 👤
            elif any(w in text_lower for w in ["channel", "link", "yt", "youtube", "url"]):
                icon_custom_emoji_id = "5409032416163540795"  # 🔗
            elif any(w in text_lower for w in ["setting", "setup", "config"]):
                icon_custom_emoji_id = "5409368076447657845"  # 🌟
            elif any(w in text_lower for w in ["close", "back", "cancel", "return", "delete", "remove", "trash"]):
                icon_custom_emoji_id = "5409320020058584473"  # Delete/Close: 5409320020058584473
                text = text.replace("ᴄʟᴏsᴇ", "").strip()
                
    # If the text is empty, set it to a zero-width space to show ONLY the custom emoji icon
    if not text.strip():
        text = "\u200b"
        
    original_button_init(self, text=text, callback_data=callback_data, url=url, web_app=web_app, login_url=login_url, user_id=user_id, switch_inline_query=switch_inline_query, switch_inline_query_current_chat=switch_inline_query_current_chat, callback_game=callback_game)
    
    self.style = style
    self.icon_custom_emoji_id = icon_custom_emoji_id

InlineKeyboardButton.__init__ = patched_button_init


# 2. Text conversion function for replacing standard emojis with premium custom emoji HTML entities
def replace_emojis_with_premium(text: str) -> str:
    if not text:
        return text
    
    # Convert string representation of types if passed
    if not isinstance(text, str):
        text = str(text)
        
    for emo, eid in EMOJI_MAP.items():
        tg_tag = f'<tg-emoji emoji-id="{eid}">{emo}</tg-emoji>'
        text = text.replace(emo, tg_tag)
        
    return text


# 3. Serialization helpers for reply markup
def button_to_dict(button):
    btn_dict = {"text": button.text}
    if getattr(button, "url", None) is not None:
        btn_dict["url"] = button.url
    elif getattr(button, "callback_data", None) is not None:
        data = button.callback_data
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        btn_dict["callback_data"] = data
    elif getattr(button, "web_app", None) is not None:
        btn_dict["web_app"] = {"url": button.web_app.url}
    elif getattr(button, "switch_inline_query", None) is not None:
        btn_dict["switch_inline_query"] = button.switch_inline_query
    elif getattr(button, "switch_inline_query_current_chat", None) is not None:
        btn_dict["switch_inline_query_current_chat"] = button.switch_inline_query_current_chat
    elif getattr(button, "login_url", None) is not None:
        btn_dict["login_url"] = {
            "url": button.login_url.url,
            "forward_text": button.login_url.forward_text,
            "bot_username": button.login_url.bot_username,
            "request_write_access": button.login_url.request_write_access,
        }
        
    if getattr(button, "style", None):
        btn_dict["style"] = button.style
    if getattr(button, "icon_custom_emoji_id", None):
        btn_dict["icon_custom_emoji_id"] = str(button.icon_custom_emoji_id)
        
    return btn_dict

def serialize_reply_markup(markup):
    if not markup:
        return None
    if isinstance(markup, InlineKeyboardMarkup):
        keyboard = []
        for row in markup.inline_keyboard:
            row_btns = []
            for btn in row:
                row_btns.append(button_to_dict(btn))
            keyboard.append(row_btns)
        return {"inline_keyboard": keyboard}
    elif isinstance(markup, ReplyKeyboardMarkup):
        keyboard = []
        for row in markup.keyboard:
            row_btns = []
            for btn in row:
                btn_dict = {"text": btn.text}
                if hasattr(btn, "style") and btn.style:
                    btn_dict["style"] = btn.style
                row_btns.append(btn_dict)
            keyboard.append(row_btns)
        return {
            "keyboard": keyboard,
            "resize_keyboard": markup.resize_keyboard,
            "one_time_keyboard": markup.one_time_keyboard,
            "selective": markup.selective
        }
    return None


# 4. HTTP API client for Bot API requests
async def call_bot_api(token, method, params):
    url = f"https://api.telegram.org/bot{token}/{method}"
    serialized_params = {}
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, (dict, list)):
            serialized_params[k] = json.dumps(v)
        else:
            serialized_params[k] = str(v)
            
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=serialized_params, timeout=15) as resp:
                return await resp.json()
    except Exception as e:
        LOGGER.error(f"Error calling Telegram Bot API method {method}: {e}")
        return {"ok": False, "description": str(e)}


# 5. Patch Pyrogram Client methods
original_send_message = Client.send_message
original_edit_message_text = Client.edit_message_text
original_edit_message_reply_markup = Client.edit_message_reply_markup
original_send_photo = Client.send_photo

async def patched_send_message(self, *args, **kwargs):
    if not getattr(self, "me", None) or not self.me.is_bot:
        return await original_send_message(self, *args, **kwargs)
        
    sig = inspect.signature(original_send_message)
    bound = sig.bind(self, *args, **kwargs)
    bound.apply_defaults()
    
    chat_id = bound.arguments.get("chat_id")
    text = bound.arguments.get("text")
    disable_web_page_preview = bound.arguments.get("disable_web_page_preview")
    disable_notification = bound.arguments.get("disable_notification")
    reply_to_message_id = bound.arguments.get("reply_to_message_id")
    reply_markup = bound.arguments.get("reply_markup")
    
    text_processed = replace_emojis_with_premium(text)
    token = self.bot_token
    params = {
        "chat_id": chat_id,
        "text": text_processed,
        "parse_mode": "HTML",
        "disable_web_page_preview": disable_web_page_preview,
        "disable_notification": disable_notification,
        "reply_markup": serialize_reply_markup(reply_markup)
    }
    if reply_to_message_id:
        params["reply_parameters"] = {"message_id": reply_to_message_id}
        
    res = await call_bot_api(token, "sendMessage", params)
    if res.get("ok"):
        message_id = res["result"]["message_id"]
        try:
            return await self.get_messages(chat_id, message_id)
        except Exception:
            pass
            
    # Fallback to original MTProto call in case of failure
    return await original_send_message(self, *args, **kwargs)

async def patched_edit_message_text(self, *args, **kwargs):
    if not getattr(self, "me", None) or not self.me.is_bot:
        return await original_edit_message_text(self, *args, **kwargs)
        
    sig = inspect.signature(original_edit_message_text)
    bound = sig.bind(self, *args, **kwargs)
    bound.apply_defaults()
    
    chat_id = bound.arguments.get("chat_id")
    message_id = bound.arguments.get("message_id")
    text = bound.arguments.get("text")
    disable_web_page_preview = bound.arguments.get("disable_web_page_preview")
    reply_markup = bound.arguments.get("reply_markup")
    
    text_processed = replace_emojis_with_premium(text)
    token = self.bot_token
    params = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text_processed,
        "parse_mode": "HTML",
        "disable_web_page_preview": disable_web_page_preview,
        "reply_markup": serialize_reply_markup(reply_markup)
    }
    
    res = await call_bot_api(token, "editMessageText", params)
    if res.get("ok"):
        try:
            return await self.get_messages(chat_id, message_id)
        except Exception:
            pass
            
    return await original_edit_message_text(self, *args, **kwargs)

async def patched_edit_message_reply_markup(self, *args, **kwargs):
    if not getattr(self, "me", None) or not self.me.is_bot:
        return await original_edit_message_reply_markup(self, *args, **kwargs)
        
    sig = inspect.signature(original_edit_message_reply_markup)
    bound = sig.bind(self, *args, **kwargs)
    bound.apply_defaults()
    
    chat_id = bound.arguments.get("chat_id")
    message_id = bound.arguments.get("message_id")
    reply_markup = bound.arguments.get("reply_markup")
    
    token = self.bot_token
    params = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": serialize_reply_markup(reply_markup)
    }
    
    res = await call_bot_api(token, "editMessageReplyMarkup", params)
    if res.get("ok"):
        try:
            return await self.get_messages(chat_id, message_id)
        except Exception:
            pass
            
    return await original_edit_message_reply_markup(self, *args, **kwargs)

async def patched_send_photo(self, *args, **kwargs):
    if not getattr(self, "me", None) or not self.me.is_bot:
        return await original_send_photo(self, *args, **kwargs)
        
    sig = inspect.signature(original_send_photo)
    bound = sig.bind(self, *args, **kwargs)
    bound.apply_defaults()
    
    chat_id = bound.arguments.get("chat_id")
    photo = bound.arguments.get("photo")
    caption = bound.arguments.get("caption")
    disable_notification = bound.arguments.get("disable_notification")
    reply_to_message_id = bound.arguments.get("reply_to_message_id")
    reply_markup = bound.arguments.get("reply_markup")
    
    caption_processed = replace_emojis_with_premium(caption)
    
    if isinstance(photo, str):
        token = self.bot_token
        params = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption_processed,
            "parse_mode": "HTML",
            "reply_markup": serialize_reply_markup(reply_markup),
            "disable_notification": disable_notification
        }
        if reply_to_message_id:
            params["reply_parameters"] = {"message_id": reply_to_message_id}
            
        res = await call_bot_api(token, "sendPhoto", params)
        if res.get("ok"):
            message_id = res["result"]["message_id"]
            try:
                return await self.get_messages(chat_id, message_id)
            except Exception:
                pass
                
    return await original_send_photo(self, *args, **kwargs)

# 6. Patch Client.start to handle FloodWait automatically
original_start = Client.start

async def patched_start(self):
    try:
        return await original_start(self)
    except FloodWait as e:
        LOGGER.warning(f"Hit FloodWait of {e.value} seconds at startup. Sleeping to respect rate limit...")
        await asyncio.sleep(e.value + 5)
        return await patched_start(self)

# Apply patches
Client.send_message = patched_send_message
Client.edit_message_text = patched_edit_message_text
Client.edit_message_reply_markup = patched_edit_message_reply_markup
Client.send_photo = patched_send_photo
Client.start = patched_start

LOGGER.info("Premium Emojis and Colored Buttons Patch Applied Successfully!")
