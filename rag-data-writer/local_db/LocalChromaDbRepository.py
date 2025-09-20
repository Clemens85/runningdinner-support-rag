import chromadb
from VectorDbRepository import VectorDbRepository
from chromadb.config import Settings
from langchain_core.documents import Document

DATABASE_NAME = ".chromadb"
COLLECTION_NAME = "support-documents-v1"

class LocalChromaDbRepository(VectorDbRepository):
    def __init__(self, database_name: str = DATABASE_NAME, collection_name: str = COLLECTION_NAME,  auto_create: bool = False, settings: Settings = Settings()):
        self.client = chromadb.PersistentClient(path=f"./{database_name}", settings=settings)
        self.collection = self.__get_collection(collection_name, auto_create=auto_create)

    def add_document(self, doc_id: str, document: Document, text_embedding: list[float]):
        text = document.page_content
        self.collection.add(
            documents=[text],
            embeddings=[text_embedding],
            ids=[doc_id],
            metadatas=[document.metadata],
        )

    def __get_collection(self, collection_name: str, auto_create: bool = False):
        if auto_create:
            return self.client.get_or_create_collection(name=collection_name)
        else:
            return self.client.get_collection(name=collection_name)

    def reset(self):
        collection_name = self.collection.name
        existing_collection_names = self.client.list_collections()
        if collection_name in existing_collection_names:
            self.client.delete_collection(name=collection_name)
            return self.client.create_collection(name=collection_name)
        return None
    
    def find_similar_docs(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas']
        )
        similar_texts = results['documents'][0] if results['documents'] else []
        return similar_texts