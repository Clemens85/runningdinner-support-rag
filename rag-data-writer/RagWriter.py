import os
from typing import List
import openai
import torch
import tqdm
from transformers import pipeline
from VectorDbRepository import VectorDbRepository
from langchain_core.documents import Document
from DocumentProcessor import get_filename_from_metadata
from Util import setup_environment
from LanguageDetector import LanguageDetector
from Translator import Translator

setup_environment()

openai = openai.OpenAI()
EMBEDDING_MODEL = 'text-embedding-3-small'

class RagWriter:
    def __init__(self, repository: VectorDbRepository):
        self.repository = repository
        self.language_detector = LanguageDetector()
        self.translator = Translator()

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
        for _, doc in tqdm.tqdm(enumerate(documents), total=len(documents), desc="Embedding and Storing documents to VectorDB"):
            text = doc.page_content

            # TODO: Anonymize names and address data here if needed

            languge = self.language_detector.detect_language(text)  # Detect and set language metadata
            doc.metadata['language'] = languge

            if languge != 'de':
                translation = self.translator.translate_to_german(doc.page_content)
                translated_doc = Document(
                    page_content=translation,
                    metadata={**doc.metadata, 'language': "de", "filename": get_filename_from_metadata(doc) + "_translated"}
                )
                self.put_to_vector_db(translated_doc)

            self.put_to_vector_db(doc)

        print(f"{len(documents)} documents were persisted.")

    def put_to_vector_db(self, doc: Document):
        filename = get_filename_from_metadata(doc)
        embedding = self.embed_text_cached(doc.page_content, filename)
        doc_id = filename
        self.repository.add_document(doc_id, doc, embedding)
        print(f"Stored translated document with ID: {doc_id} and metadata: {doc.metadata}")


    def find_similar_docs(self, query: str, top_k: int = 3) -> list[str]:
        query_embedding = self.embed_text(query)
        return self.repository.find_similar_docs(query_embedding, top_k=top_k)
    
