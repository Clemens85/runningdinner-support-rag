import chromadb
from VectorDbRepository import VectorDbRepository
from chromadb.config import Settings

DATABASE_NAME = "local_chroma_db"
COLLECTION_NAME = "support_documents_v1"

class LocalChromaDbRepository(VectorDbRepository):
    def __init__(self, database_name: str, settings: Settings = Settings()):
        self.client = chromadb.PersistentClient(path=f"./{database_name}", settings=settings)

    def get_collection(self, collection_name: str, auto_create: bool = False):
        if auto_create:
            return self.client.get_or_create_collection(name=collection_name)
        else:
            return self.client.get_collection(name=collection_name)

    def reset_collection(self, collection_name: str):
        existing_collection_names = self.client.list_collections()
        if collection_name in existing_collection_names:
            self.client.delete_collection(name=collection_name)
            return self.client.create_collection(name=collection_name)