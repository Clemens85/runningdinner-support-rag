from abc import ABC, abstractmethod
from SupportDocument import SupportDocument

class VectorDbRepository(ABC):

    @abstractmethod
    def add_document(self, doc_id: str, document: SupportDocument, text_embedding: list[float]):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def find_similar_docs(self, query: str, top_k: int = 3) -> list[str]:
        pass