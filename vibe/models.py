from dataclasses import dataclass, field

@dataclass
class Track:
    id:str
    title:str
    artist:str
    album:str="Unknown album"
    duration:float=0.0
    artwork_url:str=""
    release_id:str=""
    playback_url:str=""
    provider:str=""
    liked:bool=False
    playback_type:str="none"  # full, preview, none

@dataclass
class Playlist:
    name:str
    tracks:list[Track]=field(default_factory=list)
    index:int=0

    @property
    def current(self):
        return self.tracks[self.index] if self.tracks else None
