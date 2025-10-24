import os
from pathlib import Path
from typing import List
import openai
import tqdm
from VectorDbRepository import VectorDbRepository
from DocumentProcessor import map_filename_to_doc_id, get_filename_from_metadata, parse_date_from_filename
from Util import setup_environment
from LanguageDetector import LanguageDetector
from Translator import Translator
from SupportDocument import SupportDocument
from PipelineConfig import EMBEDDING_CACHE_DIR, ANONYMIZED_STAGE_DIR, TRANSLATED_STAGE_DIR
from anonymizer.Anonymizer import Anonymizer

setup_environment()

openai = openai.OpenAI()
EMBEDDING_MODEL = 'text-embedding-3-small'

class RagWriter:
    def __init__(self, repository: VectorDbRepository, anonymizer: Anonymizer, translator: Translator):
        self.repository = repository
        self.language_detector = LanguageDetector()
        self.translator: Translator = translator
        self.anonymizer: Anonymizer = anonymizer

    def embed_text(self, text: str) -> list[float]:
        response = openai.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding
        return embedding
    
    def embed_text_cached(self, text: str, cache_key: str) -> list[float]:
        cache_dir = EMBEDDING_CACHE_DIR
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


    def embed_docs_to_database(self, documents: List[SupportDocument]) -> List[SupportDocument]:

        persisted_documents = []

        for _, doc in tqdm.tqdm(enumerate(documents), total=len(documents), desc="Embedding and Storing documents to VectorDB"):

            language = self.language_detector.detect_language(doc.page_content)  # Detect and set language metadata
            doc.metadata['language'] = language

            doc.page_content = self.anonymizer.anonymize_personal_data(doc.page_content, language)
            self.write_to_stage_dir(ANONYMIZED_STAGE_DIR, doc.page_content, get_filename_from_metadata(doc))

            if language != 'de':
                translation = self.translator.translate_to_german(doc.page_content)
                new_filename = get_filename_from_metadata(doc) + "_translated"
                translated_doc = SupportDocument(
                    id = new_filename,
                    page_content=translation,
                    metadata={**doc.metadata, 'language': "de", 'source': new_filename}
                )
                persisted_documents.append(self.put_to_vector_db(translated_doc))
                self.write_to_stage_dir(TRANSLATED_STAGE_DIR, translated_doc.page_content, new_filename)

            persisted_documents.append(self.put_to_vector_db(doc))
            self.write_to_stage_dir(TRANSLATED_STAGE_DIR, doc.page_content, get_filename_from_metadata(doc))

        print(f"{len(persisted_documents)} documents were persisted.")
        return persisted_documents

    def put_to_vector_db(self, doc: SupportDocument) -> SupportDocument:
        filename = get_filename_from_metadata(doc)
        embedding = self.embed_text_cached(doc.page_content, filename)
        self.repository.add_document(doc.id, doc, embedding)
        print(f"Stored document embeddings for ID: {doc.id} and metadata: {doc.metadata} into vector database")
        return doc


    def _get_language_from_filepath(self, filepath: Path) -> str:
        # base filename (e.g. `2020-11.md`)
        base_filename = filepath.name
        # candidate translated path (`/foo/bar/2020-11.md_translated`)
        translated_path = filepath.parent / (base_filename + "_translated")
        if translated_path.exists():
            return 'en' # original document was translated from English (and is hence an English document)
        return 'de'

    def embed_docs_from_stage_to_database(self, stage: str) -> None:
        directory = Path(stage)
        read_documents = directory.glob("**/*.md*") # Consider also md files with _translated suffix

        for md_file in read_documents:
            try:
                content = md_file.read_text(encoding='utf-8')
                doc_id = map_filename_to_doc_id(str(md_file))
                date = parse_date_from_filename(doc_id)

                language = self._get_language_from_filepath(md_file)

                # Create document with metadata
                doc = SupportDocument(
                    id=doc_id,
                    page_content=content,
                    metadata={
                        'source': str(doc_id),
                        'date': date,
                        'type': 'support-email',
                        'language': language
                    },
                )
                self.put_to_vector_db(doc)
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
                continue

    def find_similar_docs(self, query: str, top_k: int = 3) -> list[str]:
        query_embedding = self.embed_text(query)
        return self.repository.find_similar_docs(query_embedding, top_k=top_k)
    
    def clear_embedding_cache(self):
        print("Clearing Embedding Cache...")
        cache_dir = EMBEDDING_CACHE_DIR
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, filename)
                if os.path.isfile(file_path) and filename.endswith('.embedding'):
                    os.remove(file_path)
            print("Cleared embedding cache.")
        else:
            print("No embedding cache found to clear.")

    def write_to_stage_dir(self, stage_dir: str, text: str, filename: str) -> None:
        os.makedirs(stage_dir, exist_ok=True)
        file_path = os.path.join(stage_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def get_vector_db_repository(self) -> VectorDbRepository:
        return self.repository