from abc import ABC, abstractmethod
from langchain.schema import Document

class VectorDbRepository(ABC):

    @abstractmethod
    def add_document(self, doc_id: str, document: Document, text_embedding: list[float]):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def find_similar_docs(self, query: str, top_k: int = 3) -> list[str]:
        pass