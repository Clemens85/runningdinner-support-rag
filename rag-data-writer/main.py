from DocumentProcessor import SUPPORT_EMAILS_DIR, load_support_documents, prepare_docs
from Importer import Importer
from Util import setup_environment
from VectorDbRepositoryFactory import get_vector_db_repository
from RagWriter import RagWriter
from Translator import Translator

setup_environment()

def main():
    docs = load_support_documents(directory_path=SUPPORT_EMAILS_DIR)
    prepare_docs(docs)

    repository = get_vector_db_repository(use_local=True)
    # rag_writer = RagWriter(repository)
    # print(f"Detecting language for {docs[0].page_content}")
    # lang = rag_writer.detect_language(docs[0].page_content)
    # print(f"Detected language: {lang}")

    english_example_file = "2022-08-18_12-32_26"
    english_docs = [doc for doc in docs if english_example_file in doc.metadata['source']]
    
    model = "gpt-4o-mini"
    #model = "gpt-4.1-mini"
     
    print(f"Translating following doc:\n{english_docs[0].page_content}")
    print("\n\n---\n\n")
    translator = Translator(model = model, temperature=0.2, max_tokens=4048)
    translation = translator.translate_to_german(english_docs[0].page_content)
    print(translation)

    return

    importer = Importer(repository=repository)
    importer.import_docs(docs)

if __name__ == '__main__':
    main()