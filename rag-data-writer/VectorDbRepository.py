from abc import ABC, abstractmethod
from chromadb import Collection

class VectorDbRepository(ABC):
    @abstractmethod
    def get_collection(self, collection_name: str, auto_create: bool = False) -> Collection:
        pass
    
    @abstractmethod
    def reset_collection(self, collection_name: str) -> Collection:
      pass