from datetime import datetime
import re
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document

SUPPORT_EMAILS_DIR = "../gmail-reader/gmail_threads"

def load_support_documents(directory_path: str = SUPPORT_EMAILS_DIR) -> list[Document]:
  text_loader_kwargs = {'encoding': 'utf-8'}
  all_documents = []
  loader = DirectoryLoader(directory_path, glob="**/*.md", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
  docs = loader.load()
  all_documents.extend(docs)
  return all_documents


patterns_to_remove = [
    r'**Date**: ',                
    r'**Subject**: '                             
]

def parse_date(filename: str):
    match = re.match(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})_(\d{2})\.md', filename)
    if match:
        dt = datetime.strptime(f"{match.group(1)} {match.group(2)}:{match.group(3)}", "%Y-%m-%d %H-%M:%S")
        return dt.isoformat(sep=' ')
    return filename[:-3]


def clean_and_process_email_metadata(text: str) -> str:
    result = []
    support_type = "generic"
    text_lines = text.splitlines()
    first_message=True
    for line in text_lines:
        if line.startswith(("**Date**: ", "**Subject**: ")):
            continue
        if line.startswith("## From: "):
            if first_message == True:
                line = "## User"
                first_message = False
            elif "runyourdinner@gmail.com" in line.lower():
                line = "## Assistant"
            else:
                line = "## User"
        if line.startswith("Page: "):
            if "wizard" in line.lower():
                support_type = 'wizard'
            elif "admin" in line.lower():
                support_type = 'admin'
            else:
                support_type = 'generic_frontend'
            continue
        result.append(line)
    page_content = '\n'.join(result)
    return page_content, support_type
            
    
def prepare_docs(documents: list[Document]):
    for doc in documents:
        filename: str = get_filename_from_metadata(doc)
        doc.metadata['type'] = 'support-email'
        doc.metadata['date'] = parse_date(filename)
        final_page_content = re.sub(r'<img\b[^>]*?\/>', '', doc.page_content)
        final_page_content = re.sub(r'^(IP:|Content:|ID:).*\n?', '', final_page_content, flags=re.MULTILINE)
        final_page_content, support_type = clean_and_process_email_metadata(final_page_content)
        doc.page_content = final_page_content
        doc.metadata['support_type'] = support_type

def get_filename_from_metadata(doc: Document) -> str:
    filename: str = doc.metadata['source']
    return filename.split('/')[-1]

def filter_docs_by_support_type(documents: list[Document], support_type: str) -> list[Document]:
    """
    Filters documents by support type.  
    Args:
        documents (list[Document]): List of documents to filter.
        support_type (str): The support type to filter by (e.g., 'frontend', 'wizard', 'admin').
    Returns:
        list[Document]: Filtered list of documents.
    """
    return [doc for doc in documents if doc.metadata.get('support_type') == support_type]

