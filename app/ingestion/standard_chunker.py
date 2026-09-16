from app.database.models import BISStandard
from app.ingestion.standard_to_text import standard_to_text
from app.ingestion.chunker import chunk_text


def chunk_standard(
    standard: BISStandard,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    """
    Convert one BIS standard into searchable chunks.

    Each chunk keeps the standard number so retrieval can
    identify which BIS standard produced the chunk.
    """

    text = standard_to_text(standard)

    chunks = chunk_text(
        text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    return [
        {
            "standardNumber": standard.standardNumber,
            "chunkIndex": index,
            "text": chunk,
        }
        for index, chunk in enumerate(chunks)
    ]