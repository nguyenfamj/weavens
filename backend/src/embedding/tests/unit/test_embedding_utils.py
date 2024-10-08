import pytest
from ...utils import generate_text_chunk_fingerprint_with_file_name
from hashlib import md5


class TestGenerateTextChunkFingerprintWithFileName:
    text_chunk = "This is a sample text chunk for testing."
    file_name = "test_house_buying_knowledge.md"

    @pytest.mark.unit
    def test_should_return_md5_hash_format(self):
        fingerprint = generate_text_chunk_fingerprint_with_file_name(
            self.text_chunk, self.file_name
        )
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 32

    @pytest.mark.unit
    def test_should_hash_first_and_last_10_characters_of_file_name_with_file_name(
        self,
    ):
        bytes_text_chunk = self.text_chunk.encode("utf-8")
        expected_hash = md5(
            bytes_text_chunk[:10]
            + bytes_text_chunk[-10:]
            + self.file_name.encode("utf-8")
        ).hexdigest()
        fingerprint = generate_text_chunk_fingerprint_with_file_name(
            self.text_chunk, self.file_name
        )
        assert fingerprint == expected_hash
