from local_db.LocalChromaDbRepository import LocalChromaDbRepository
from RagWriter import RagWriter
from DocumentProcessor import SUPPORT_EMAILS_DIR, load_support_documents, prepare_docs
from Importer import Importer

def main():
    docs = load_support_documents(directory_path=SUPPORT_EMAILS_DIR)
    prepare_docs(docs)
    
    importer = Importer()
    importer.import_docs(docs)

if __name__ == '__main__':
    main()