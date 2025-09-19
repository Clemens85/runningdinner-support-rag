import os
from typing import List
from dotenv import load_dotenv
import openai
import tqdm
from VectorDbRepository import VectorDbRepository
from langchain_core.documents import Document
from DocumentProcessor import get_filename_from_metadata

load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

if (os.environ.get('OPENAI_API_KEY') is None) or (os.environ.get('OPENAI_API_KEY') == ''):
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

openai = openai.OpenAI()
EMBEDDING_MODEL = 'text-embedding-3-small'

class RagWriter:
    def __init__(self, repository: VectorDbRepository):
        self.repository = repository

    def embed_text(self, text: str) -> list[float]:
        response = openai.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding
        return embedding
    
    def embed_text_cached(self, text: str, cache_key: str) -> list[float]:
        cache_dir = os.path.join(os.path.dirname(__file__), 'embedding-cache')
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{cache_key}.embedding")
        if os.path.exists(cache_path):
            # Read and return cached embedding (comma-separated floats)
            with open(cache_path, 'r', encoding='utf-8') as f:
                line = f.readline().strip()
                embedding = [float(x) for x in line.split(',') if x]
            return embedding
        # Generate embedding and cache it
        embedding = self.embed_text(text)
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(','.join(f'{x:.10f}' for x in embedding))
        return embedding


    def embed_docs_to_database(self, documents: List[Document]):
        for idx, doc in tqdm.tqdm(enumerate(documents), total=len(documents), desc="Embedding and Storing documents to VectorDB"):
            text = doc.page_content
            filename = get_filename_from_metadata(doc)
            embedding = self.embed_text_cached(text, filename)
            doc_id = str(f"doc-{idx}")

            self.repository.add_document(doc_id, doc, embedding)
            print(f"Stored document with ID: {doc_id} and metadata: {doc.metadata}")

        print(f"{len(documents)} documents were persisted.")

    def find_similar_docs(self, query: str, top_k: int = 3) -> list[str]:
        query_embedding = self.embed_text(query)
        return self.repository.find_similar_docs(query_embedding, top_k=top_k)