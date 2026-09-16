def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[str]:
    """
    Split text into overlapping chunks without creating
    an unnecessarily small final chunk.
    """

    if not text.strip():
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    step = chunk_size - overlap
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Stop when we've reached the end
        if end == len(text):
            break

        # If the remaining text would be smaller than the overlap,
        # include it in the current chunk instead.
        if len(text) - end < overlap:
            break

        start += step

    return chunks