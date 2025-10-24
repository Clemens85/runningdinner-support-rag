from local_db.LocalChromaDbRepository import LocalChromaDbRepository
from pinecone_db.PineconeDbRepository import PineconeDbRepository
from VectorDbRepository import VectorDbRepository

def get_vector_db_repository(use_local: bool = False) -> VectorDbRepository:
    if use_local:
        return LocalChromaDbRepository(auto_create=True)
    else:
        return PineconeDbRepository(auto_create=True)