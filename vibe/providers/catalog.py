from .youtube import YouTubeProvider

class CatalogProvider:
    name="YouTube Music"
    def __init__(self,youtube=None,session=None): self.youtube=youtube or YouTubeProvider(session=session)
    def search(self,query:str,limit:int=20): return self.youtube.search(query,limit)
    def resolve_audio_url(self,video_id:str)->str: return self.youtube.resolve_audio_url(video_id)
