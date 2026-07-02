import asyncio
import os
import re
import time
import urllib.parse
from typing import Union

import aiohttp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist

API_URL = os.environ.get("SHRUTI_API_URL", "http://api01.shrutibots.site")

API_KEY = os.environ.get(
    "SHRUTI_API_KEY", "ShrutiBotsBMnH1V0alhOxaXZLLcpE"
)  ## Get This API KEY FROM TELEGRAM BOT USERNAME: @SHRUTIAPIBOT


def time_to_seconds(time_str):
    stringt = str(time_str)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


async def build_stream_url(video_id: str, dl_type: str) -> str:
    """Builds a direct playable stream URL from the Shruti API (no local download)."""
    query = urllib.parse.quote(video_id)
    return f"{API_URL}/download?url={query}&type={dl_type}&api_key={API_KEY}"


async def download_song(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    return await build_stream_url(video_id, "audio")


async def download_video(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    return await build_stream_url(video_id, "video")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self._recent_prefetches = {}  # vidid_type -> timestamp
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        self._session = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=600)
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    def _clean_link(self, link: str) -> str:
        if not link:
            return ""
        link = str(link)
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]
        return link

    def _extract_vidid(self, link: str) -> Union[str, None]:
        regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
        match = re.search(regex, link)
        return match.group(1) if match else None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        results = VideosSearch(link, limit=1)
        title = duration_min = thumbnail = vidid = None
        duration_sec = 0
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        try:
            stream_url, status = await self.download(link, None, video=True)
            if status:
                return 1, stream_url
            return 0, "Video URL generation failed"
        except Exception as e:
            return 0, f"Video URL generation error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        link = self._clean_link(link)
        try:
            plist = await Playlist.get(link)
        except Exception:
            return []
        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        results = VideosSearch(link, limit=1)
        title = duration_min = vidid = yturl = thumbnail = None
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        import yt_dlp

        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def prefetch(self, link: str, video: bool = False) -> bool:
        """Fire-and-forget request to warm up the Shruti API cache before playback."""
        dl_type = "video" if video else "audio"
        link = self._clean_link(link)
        vidid = self._extract_vidid(link) or link

        cache_key = f"{vidid}_{dl_type}"
        now = time.time()
        if cache_key in self._recent_prefetches:
            if now - self._recent_prefetches[cache_key] < 30:
                return True
        self._recent_prefetches[cache_key] = now

        if len(self._recent_prefetches) > 100:
            self._recent_prefetches = {
                k: v for k, v in self._recent_prefetches.items() if now - v < 300
            }

        session = await self.get_session()
        try:
            async with session.get(
                f"{API_URL}/download",
                params={"url": vidid, "type": dl_type, "api_key": API_KEY, "prefetch": "true"},
            ) as resp:
                await resp.read()
            return True
        except Exception:
            return False

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> tuple:
        if videoid:
            link = self.base + link
        link = self._clean_link(link)

        dl_type = "video" if (video or songvideo) else "audio"
        vidid = self._extract_vidid(link) or link

        # warm up the Shruti API cache in the background so playback starts fast
        asyncio.create_task(self.prefetch(link, video=bool(dl_type == "video")))

        stream_url = await build_stream_url(vidid, dl_type)
        return stream_url, True


YouTube = YouTubeAPI()
