import os
from typing import List
from RagWriter import RagWriter
from SupportDocument import SupportDocument
from PipelineConfig import IMPORT_LOCK_FILE

class Importer:

    def __init__(self, rag_writer: RagWriter, reset_lock_file: bool = False, reset_vector_db: bool = False, reset_embedding_cache: bool = False):
        self.rag_writer = rag_writer
        self._ensure_lock_file_exists()
        if reset_lock_file:
            print("Resetting lock file...")
            os.remove(IMPORT_LOCK_FILE)
            self._ensure_lock_file_exists()
        if reset_vector_db:
            print("Resetting Vector DB...")
            self.rag_writer.get_vector_db_repository().reset()
        if reset_embedding_cache:
            self.rag_writer.clear_embedding_cache()


    def _ensure_lock_file_exists(self):
        if not os.path.exists(IMPORT_LOCK_FILE):
            with open(IMPORT_LOCK_FILE, 'w') as f:
                f.write('')

    def _read_lock_file_lines(self) -> List[str]:
        with open(IMPORT_LOCK_FILE, 'r') as f:
            lines = f.read().splitlines()
        return lines

    def import_docs(self, docs: List[SupportDocument]):
        already_imported_docs = self._read_lock_file_lines()

        docs_to_import = []
        for doc in docs:
            filename: str = doc.metadata['source']
            filename = filename.split('/')[-1]
            print (f"Checking if document {filename} is already in Vector DB...")

            if filename in already_imported_docs:
                print(f"Document {filename} already imported, skipping.")
                continue

            docs_to_import.append(doc)

        print(f"Importing {len(docs_to_import)} new documents to Vector DB...")
        final_imported_docs = self.rag_writer.embed_docs_to_database(docs_to_import)
        print (f"Append final imported document names (final number: {len(final_imported_docs)}) to lock file...")
        with open(IMPORT_LOCK_FILE, 'a') as f:
            for doc in final_imported_docs:
                filename: str = doc.metadata['source']
                filename = filename.split('/')[-1]
                f.write(f"{filename}\n")
        print("Import completed.")