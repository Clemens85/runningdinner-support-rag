from DocumentProcessor import DocumentProcessor
from Importer import Importer
from Util import setup_environment
from VectorDbRepositoryFactory import get_vector_db_repository
from RagWriter import RagWriter
from Translator import Translator
from anonymizer.AnonymizerOpenAI import AnonymizerOpenAI
from PipelineConfig import TRANSLATED_STAGE_DIR

setup_environment()

#model = "gpt-4o-mini"
model = "gpt-4.1-mini"

def main():

    doc_processor = DocumentProcessor()
    docs = doc_processor.load_support_documents()
    doc_processor.write_loaded_documents()

    repository = get_vector_db_repository(use_local=False)
    anonymizer = AnonymizerOpenAI()
    translator = Translator(model=model, temperature=0.2, max_tokens=8048)
    rag_writer = RagWriter(repository=repository, anonymizer=anonymizer, translator=translator)

    rag_writer.embed_docs_from_stage_to_database(stage=TRANSLATED_STAGE_DIR)
    return

    importer = Importer(rag_writer=rag_writer, reset_lock_file=False, reset_vector_db=True, reset_embedding_cache=False)
    importer.import_docs(docs)


if __name__ == '__main__':
    main()