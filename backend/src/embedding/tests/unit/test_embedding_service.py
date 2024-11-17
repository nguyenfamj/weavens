import pytest
from unittest.mock import Mock, MagicMock, patch

from ...service import EmbeddingService


class TestAddTextChunksToCollection:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.get_chroma_db = Mock()
        self.mock_document_collection = Mock()
        self.get_chroma_db.document_collection = self.mock_document_collection

        self.get_chroma_db_patcher = patch(
            "src.embedding.service.get_chroma_db",
            return_value=self.get_chroma_db,
        ).start()

        self.mock_generate_fingerprint = patch(
            "src.embedding.service.generate_text_chunk_fingerprint_with_file_name"
        ).start()

        self.embedding_service = EmbeddingService()

        yield

        patch.stopall()

    @pytest.mark.unit
    def test_add_to_collection_with_correct_data(self):
        text_chunks = ["chunk1", "chunk2"]
        file_name = "test.txt"
        shared_metadata = {"key": "value"}

        self.mock_generate_fingerprint.side_effect = ["fp1", "fp2"]

        self.embedding_service.add_text_chunks_to_collection(
            text_chunks, file_name, shared_metadata
        )

        assert self.mock_document_collection.add.call_count == 1

        self.mock_document_collection.add.assert_called_once_with(
            documents=text_chunks,
            ids=["fp1", "fp2"],
            metadatas=[{"key": "value", "file_name": "test.txt"} for _ in text_chunks],
        )

    @pytest.mark.unit
    def test_log_error_when_chroma_wrapper_raises_exception(self):
        text_chunks = ["chunk1", "chunk2"]
        file_name = "test.txt"
        shared_metadata = {"key": "value"}
        error_message = "Error adding text chunks to collection"

        self.mock_generate_fingerprint.side_effect = ["fp1", "fp2"]

        self.mock_document_collection.add.side_effect = Exception(error_message)

        with pytest.raises(Exception) as exception_info:
            self.embedding_service.add_text_chunks_to_collection(
                text_chunks, file_name, shared_metadata
            )

        assert str(exception_info.value) == error_message

    @pytest.mark.unit
    def test_query_similar_documents_should_pass_right_parameters_to_chroma(self):
        self.mock_document_collection.query.return_value = MagicMock()

        self.embedding_service.query_similar_documents("query")

        self.mock_document_collection.query.assert_called_once_with(
            query_texts=["query"], n_results=5
        )

    @pytest.mark.unit
    def test_query_similar_documents_should_return_correct_results(self):
        mock_query_results = {
            "ids": [["id1", "id2"]],
            "documents": [["document1", "document2"]],
            "metadatas": [[{"key": "value"}, {"key": "value"}]],
            "distances": [[0.1, 0.2]],
        }

        self.mock_document_collection.query.return_value = mock_query_results

        results = self.embedding_service.query_similar_documents("query")

        assert results == {
            "ids": ["id1", "id2"],
            "documents": ["document1", "document2"],
            "metadatas": [{"key": "value"}, {"key": "value"}],
        }
