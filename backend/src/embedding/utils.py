import hashlib


def generate_text_chunk_fingerprint_with_file_name(
    text_chunk: str, file_name: str
) -> str:
    """
    Generate a fingerprint for a text chunk with the file name.
    """
    bytes_text_chunk = text_chunk.encode("utf-8")

    # Set fingerprint to first 10 bytes of text chunk, last 10 bytes of text chunk, and file name
    fingerprint = (
        bytes_text_chunk[:10] + bytes_text_chunk[-10:] + file_name.encode("utf-8")
    )

    return hashlib.md5(fingerprint).hexdigest()
