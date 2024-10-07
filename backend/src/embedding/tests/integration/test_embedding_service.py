import pytest
from ...service import EmbeddingService
from ....chroma import ChromaWrapper


class TestAddTextChunksToCollection:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Initialize the ChromaWrapper
        self.chroma_wrapper = ChromaWrapper()
        self.chroma_wrapper.initialize()
        self.document_collection = self.chroma_wrapper.document_collection

        self.embedding_service = EmbeddingService()

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
