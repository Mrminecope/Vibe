"""
YouTube Music provider powered by yt-dlp.

Uses YouTube search and resolves a playable audio URL immediately before
mpv starts. No media file is downloaded by Vibe.
"""
from __future__ import annotations
import yt_dlp
from ..models import Track

_BASE_OPTS={"quiet":True,"no_warnings":True,"skip_download":True,"extract_flat":False,"default_search":"ytsearch","noplaylist":True,"source_address":"0.0.0.0"}
_SEARCH_OPTS={**_BASE_OPTS,"extract_flat":True,"playlist_items":"1-50"}
_EXTRACT_OPTS={**_BASE_OPTS,"format":"bestaudio/best"}

def _thumb(entry:dict)->str:
    thumbs=entry.get("thumbnails") or []
    for t in reversed(thumbs):
        if t.get("url"): return t["url"]
    return entry.get("thumbnail","")

class YouTubeProvider:
    name="YouTube Music"
    def __init__(self,api_key="",session=None): self.api_key=""
    @property
    def configured(self): return True

    def search(self,query:str,limit:int=20)->list[Track]:
        limit=min(max(int(limit),1),50)
        q=f"ytsearch{limit}:{query}"
        opts={**_SEARCH_OPTS,"playlist_items":f"1-{limit}"}
        with yt_dlp.YoutubeDL(opts) as ydl: info=ydl.extract_info(q,download=False)
        tracks=[]
        for e in (info or {}).get("entries") or []:
            if not e: continue
            vid=e.get("id") or e.get("url","")
            if not vid: continue
            tracks.append(Track(id=f"youtube:{vid}",title=e.get("title") or "Unknown",artist=e.get("uploader") or e.get("channel") or "YouTube",album="YouTube Music",duration=float(e.get("duration") or 0),artwork_url=_thumb(e),playback_url=vid,provider=self.name,playback_type="full"))
        return tracks

    def resolve_audio_url(self,video_id:str)->str:
        url=f"https://www.youtube.com/watch?v={video_id}"
        with yt_dlp.YoutubeDL(_EXTRACT_OPTS) as ydl: info=ydl.extract_info(url,download=False)
        if not info: raise RuntimeError(f"yt-dlp returned no info for video {video_id!r}")
        stream=info.get("url")
        if not stream:
            for fmt in reversed(info.get("formats") or []):
                if fmt.get("url") and fmt.get("vcodec")=="none": stream=fmt["url"]; break
        if not stream:
            for fmt in reversed(info.get("formats") or []):
                if fmt.get("url"): stream=fmt["url"]; break
        if not stream: raise RuntimeError(f"No playable stream found for video {video_id!r}")
        return stream
