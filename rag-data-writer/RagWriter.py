import os
from typing import List
from dotenv import load_dotenv
import openai
import tqdm
from VectorDbRepository import VectorDbRepository
from langchain_core.documents import Document

load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

if (os.environ.get('OPENAI_API_KEY') is None) or (os.environ.get('OPENAI_API_KEY') == ''):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

openai = openai.OpenAI()
EMBEDDING_MODEL = 'text-embedding-3-small'

class RagWriter:
    def __init__(self, repository: VectorDbRepository, collection_name: str):
        self.repository = repository
        self.collection_name = collection_name

    def embed_text(self, text: str) -> list[float]:
        response = openai.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding
        return embedding
    
    def embed_docs_to_database(self, documents: List[Document]):
        collection = self.repository.get_collection(self.collection_name, auto_create=True)
        
        for idx, doc in tqdm.tqdm(enumerate(documents), total=len(documents), desc="Embedding and Storing documents to VectorDB"):
            text = doc.page_content
            embedding = self.embed_text(text)
            doc_id = str(f"doc-{idx}")

            collection.add(
                documents=[text],
                embeddings=[embedding],
                ids=[doc_id],
                metadatas=[doc.metadata],
            )
            print(f"Stored document with ID: {doc_id} and metadata: {doc.metadata} in {self.collection_name}")

        print(f"{len(documents)} Dokumente wurden gespeichert.")

    def find_similar_docs(self, query: str, top_k: int = 3) -> list[str]:
        collection = self.repository.get_collection(auto_create=False)
        query_embedding = self.embed_text(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results['documents'][0]