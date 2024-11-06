from chromadb import Documents

from ..chroma import ChromaWrapper
from ..logging import Logger
from .utils import generate_text_chunk_fingerprint_with_file_name

logger = Logger(__name__).logger


class EmbeddingService:
    def __init__(self):
        self.document_collection = ChromaWrapper().document_collection
        logger.info("EmbeddingService initialized")

    def query_similar_documents(self, query_text: str, n_results: int = 5) -> list[str]:
        """
        Query similar documents to the query text.
        """
        try:
            response = self.document_collection.query(
                query_texts=[query_text], n_results=n_results
            )

            results = {
                "ids": response["ids"],
                "documents": response["documents"],
                "metadatas": response["metadatas"],
            }

            return results

        except Exception as e:
            logger.error(f"Error querying similar documents: {e}")
            raise e

    def add_text_chunks_to_collection(
        self,
        text_chunks: Documents,
        file_name: str,
        shared_metadata: dict = {},
    ) -> None:
        """
        Add text chunks to the collection, the text chunks should be extracted from the same single file.

        Args:
            text_chunks (list[str]): List of text chunks to be added to the collection.
            file_name (str): Name of the file from which the text chunks were extracted. The file name is used as metadata for the text chunks.
            shared_metadata (dict): Shared metadata to be added to the text chunks.
        """
        try:
            fingerprints = [
                generate_text_chunk_fingerprint_with_file_name(chunk, file_name)
                for chunk in text_chunks
            ]

            base_metadata = {**shared_metadata, "file_name": file_name}

            self.document_collection.add(
                documents=text_chunks,
                ids=fingerprints,
                metadatas=[base_metadata for _ in text_chunks],
            )
        except Exception as e:
            logger.error(f"Error adding text chunks to collection: {e}")
            raise e
