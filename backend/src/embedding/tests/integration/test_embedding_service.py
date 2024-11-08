import pytest
from unittest.mock import patch, Mock
from chromadb.api.types import EmbeddingFunction

from ...service import EmbeddingService
from ...vectordb import get_chroma_db


class MockEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        return [[0.1] * 1536 for _ in input]


class TestAddTextChunksToCollection:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Mock the OpenAIEmbeddingFunction
        self.embeddings_patcher = patch(
            "chromadb.utils.embedding_functions.OpenAIEmbeddingFunction",
            return_value=MockEmbeddingFunction(),
        )
        self.embeddings_patcher.start()

        # Initialize the ChromaWrapper
        self.chroma_db = get_chroma_db()
        self.chroma_db.initialize()
        self.document_collection = self.chroma_db.document_collection
        self.embedding_service = EmbeddingService()

    def teardown_method(self):
        # Stop the patcher after each test
        self.embeddings_patcher.stop()

    @pytest.mark.integration
    def test_should_add_to_collection_successfully(self):
        text_chunks = ["This is a test chunk 1.", "This is a test chunk 2."]
        file_name = "test_file.txt"
        shared_metadata = {"file_type": "txt"}

        try:
            # Add text chunks to the collection
            self.embedding_service.add_text_chunks_to_collection(
                text_chunks=text_chunks,
                file_name=file_name,
                shared_metadata=shared_metadata,
            )
            results = self.document_collection.query(
                query_texts=["test chunk"], n_results=2
            )

            assert len(results["ids"][0]) == 2
            assert text_chunks[0] in results["documents"][0]
            assert text_chunks[1] in results["documents"][0]

            for metadata in results["metadatas"][0]:
                assert metadata["file_name"] == file_name
                assert metadata["file_type"] == "txt"

        finally:
            self.document_collection.delete(where={"file_name": file_name})
