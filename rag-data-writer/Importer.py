import os
from typing import List
from local_db.LocalChromaDbRepository import LocalChromaDbRepository
from RagWriter import RagWriter
from langchain_core.documents import Document

LOCK_FILE = "import.lock"

class Importer:

    def __init__(self):
        self.__ensure_lock_file_exists()

    def __ensure_lock_file_exists(self):
        if not os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, 'w') as f:
                f.write('')

    def __read_lock_file_lines(self) -> List[str]:
        with open(LOCK_FILE, 'r') as f:
            lines = f.read().splitlines()
        return lines

    def import_docs(self, docs: List[Document]):
        already_imported_docs = self.__read_lock_file_lines()

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
        repository = LocalChromaDbRepository(database_name="local_chroma_db")
        writer = RagWriter(repository=repository, collection_name="support_documents_v1")
        writer.embed_docs_to_database(docs_to_import)
        print ("Append imported document names to lock file...")
        with open(LOCK_FILE, 'a') as f:
            for doc in docs_to_import:
                filename: str = doc.metadata['source']
                filename = filename.split('/')[-1]
                f.write(f"{filename}\n")
        print("Import completed.")