from abc import ABC, abstractmethod
from ..models import Track

class Provider(ABC):
    name="Provider"
    @abstractmethod
    def search(self,query:str,limit:int=20): raise NotImplementedError
    def resolve(self,track:Track): return track
