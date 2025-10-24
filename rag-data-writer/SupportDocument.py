from pydantic import BaseModel

class SupportDocument(BaseModel):
    """
    A document with support information, which mimics the behavior of langchain's Document class.
    """
    id: str
    page_content: str
    metadata: dict