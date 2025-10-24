from datetime import datetime
import os
import re
from typing import Tuple
from SupportDocument import SupportDocument
from pathlib import Path
from PipelineConfig import RAW_STAGE_DIR, CURATED_STAGE_DIR

INPUT_DIR = RAW_STAGE_DIR
OUTPUT_DIR = CURATED_STAGE_DIR

def get_filename_from_metadata(doc: SupportDocument) -> str:
    return doc.metadata['source']

def map_filename_to_doc_id(filename: str) -> str:
    return filename.split('/')[-1]

def parse_date_from_filename(filename: str):
    match = re.match(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})_(\d{2})\.md', filename)
    if match:
        dt = datetime.strptime(f"{match.group(1)} {match.group(2)}:{match.group(3)}", "%Y-%m-%d %H-%M:%S")
        return dt.isoformat(sep=' ')
    return filename[:-3]


class DocumentProcessor:

    def __init__(self):
        self.all_documents = []

    def load_support_documents(self) -> list[SupportDocument]:
        """Load all markdown files from directory using native Python."""
        self.all_documents = []
        directory = Path(INPUT_DIR)

        # Find all .md files recursively
        md_files = directory.glob("**/*.md")

        for md_file in md_files:
            try:
                # Read file content with UTF-8 encoding
                content = md_file.read_text(encoding='utf-8')

                doc_id = map_filename_to_doc_id(str(md_file))
                filename = doc_id

                # Create document with metadata
                doc = SupportDocument(
                    id=doc_id,
                    page_content=content,
                    metadata={
                        'source': filename
                    },
                )
                self.all_documents.append(doc)
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
                continue

        self.prepare_docs(self.all_documents)

        return self.all_documents

    def get_loaded_support_documents(self) -> list[SupportDocument]:
        return self.all_documents

    def write_loaded_documents(self) -> None:
        # Ensure output directory exists
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        for doc in self.all_documents:
            filename: str = get_filename_from_metadata(doc)
            output_path = os.path.join(OUTPUT_DIR, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc.page_content)

    def clean_and_process_email_metadata(self, text: str) -> Tuple[str, str]:
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
            

    def prepare_docs(self, documents: list[SupportDocument]):
        for doc in documents:
            doc.metadata['type'] = 'support-email'
            doc.metadata['date'] = parse_date_from_filename(get_filename_from_metadata(doc))
            final_page_content = re.sub(r'<img\b[^>]*?\/>', '', doc.page_content)
            final_page_content = re.sub(r'^(IP:|Content:|ID:).*\n?', '', final_page_content, flags=re.MULTILINE)
            final_page_content = re.sub(r'<br\s*/?>', '\n', final_page_content, flags=re.MULTILINE)
            final_page_content, support_type = self.clean_and_process_email_metadata(final_page_content)
            doc.page_content = final_page_content
            doc.metadata['support_type'] = support_type

    def filter_docs_by_support_type(self, documents: list[SupportDocument], support_type: str) -> list[SupportDocument]:
        """
        Filters documents by support type.
        Args:
            documents (list[Document]): List of documents to filter.
            support_type (str): The support type to filter by (e.g., 'frontend', 'wizard', 'admin').
        Returns:
            list[Document]: Filtered list of documents.
        """
        return [doc for doc in documents if doc.metadata.get('support_type') == support_type]

