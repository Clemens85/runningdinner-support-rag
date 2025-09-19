import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from VectorDbRepository import VectorDbRepository

load_dotenv(override=True)
os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY', '')
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_CLOUD = os.getenv('PINECONE_CLOUD', 'aws')
PINECONE_REGION = os.getenv('PINECONE_REGION', 'us-east-1') 

INDEX_NAME = "support-documents-v1"

class PineconeDbRepository(VectorDbRepository):

    def __init__(self, index_name: str = INDEX_NAME, auto_create: bool = False):
        self.index_name = index_name
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self._init_index(auto_create=auto_create)
    
    def _init_index(self, auto_create: bool = False):
        """Initialize the Pinecone index or verify it exists"""
        # Check if the index already exists
        if not self.pc.has_index(self.index_name) and auto_create:
            # For free tier, we can only create in us-east-1 region
            print(f"Creating new Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI text-embedding-3-small dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_REGION
                )
            )
        
        # Get the index
        self.index = self.pc.Index(self.index_name)

    def add_document(self, doc_id: str, document: Document, text_embedding: list[float]):
        """
        Add a document to the Pinecone index with its embedding
        
        Args:
            doc_id (str): The unique id
            document (Document): The document
            text_embedding (list[float]): Pre-calculated embedding vector for the document
        """
        
        # Create metadata with the document text
        metadata = {
            "text": document.page_content,
            **document.metadata
        }
        
        # Upsert the document embedding to the Pinecone index
        self.index.upsert(
            vectors=[(doc_id, text_embedding, metadata)]
        )
    
    def reset(self):
        """
        Reset the Pinecone index by deleting it and recreating it
        """
        if self.pc.has_index(self.index_name):
            # Delete the existing index
            self.pc.delete_index(self.index_name)
        
        # Recreate the index
        self._init_index()
      
    def find_similar_docs(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        """
        Find similar documents in the Pinecone index based on a query string
        
        Args:
            query (str): The query string to search for similar documents
            top_k (int): The number of top similar documents to return
        
        Returns:
            list[str]: List of document texts that are similar to the query
        """
        # Perform the query to find similar documents
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Extract and return the document texts from the results
        similar_texts = [match['metadata']['text'] for match in results['matches']]
        return similar_texts


    # def add_documents_batch(self, texts: List[str], embeddings: List[List[float]]):
    #     """
    #     Add multiple documents to the Pinecone index with their embeddings in batch
        
    #     Args:
    #         texts (List[str]): List of document texts
    #         embeddings (List[List[float]]): List of pre-calculated embedding vectors for the documents
    #     """
    #     if len(texts) != len(embeddings):
    #         raise ValueError("The number of texts and embeddings must be the same")
            
    #     # Prepare vectors for batch upsert
    #     vectors = []
    #     for i, (text, embedding) in enumerate(zip(texts, embeddings)):
    #         doc_id = f"{uuid.uuid4()}"
    #         metadata = {"text": text}
    #         vectors.append((doc_id, embedding, metadata))
            
    #     # Batch upsert - respecting Pinecone's limits
    #     batch_size = 100  # Pinecone recommends 100 vectors per batch for optimal performance
    #     for i in range(0, len(vectors), batch_size):
    #         batch = vectors[i:i+batch_size]
    #         self.index.upsert(vectors=batch)
