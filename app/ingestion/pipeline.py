from app.database.models import BISStandard
from app.database.repository import insert_chunk
from app.database.standard_repository import (
    get_standard_id,
    upsert_standard,
)
from app.ingestion.cleaner import clean_text
from app.ingestion.chunker import chunk_text
from app.ingestion.pdf_extractor import extract_pdf
from app.ingestion.dataset_pdf_parser import parse_dataset_pdf
from app.ingestion.standard_chunker import chunk_standard
from app.ingestion.universal_normalizer import normalize_dataset
from app.ingestion.validator import validate_standards
from app.rag.embeddings import EmbeddingModel


def ingest_standard(
    pdf_path: str,
    standard: BISStandard,
    embedding_model: EmbeddingModel | None = None,
) -> int:
    """
    Ingest one BIS standard document.

    Stores structured standard metadata in `standards`
    and searchable text chunks with embeddings in `chunks`.
    """

    upsert_standard(standard.model_dump())

    standard_id = get_standard_id(standard.standardNumber)

    if embedding_model is None:
        embedding_model = EmbeddingModel()

    pages = extract_pdf(pdf_path)

    chunk_count = 0

    for page in pages:
        cleaned_text = clean_text(page["text"])

        if not cleaned_text:
            continue

        chunks = chunk_text(cleaned_text)

        for chunk_index, chunk in enumerate(chunks):
            embedding = embedding_model.embed_text(chunk)

            document = {
                "standardId": standard_id,
                "standardNumber": standard.standardNumber,
                "page": page["page"],
                "chunkIndex": chunk_index,
                "text": chunk,
                "embedding": embedding,
            }

            insert_chunk(document)
            chunk_count += 1

    return chunk_count


def ingest_standards(
    standards: list[BISStandard],
    pdf_path: str | None = None,
) -> int:
    """
    Ingest multiple BIS standards.

    Structured metadata is always stored.

    If a PDF is supplied, its text is chunked and embedded.
    """

    embedding_model = EmbeddingModel() if pdf_path else None

    total_chunks = 0

    for standard in standards:
        if pdf_path:
            total_chunks += ingest_standard(
                pdf_path=pdf_path,
                standard=standard,
                embedding_model=embedding_model,
            )
        else:
            upsert_standard(standard.model_dump())

    return total_chunks


def ingest_dataset_pdf(pdf_path: str) -> dict:
    """
    Parse, normalize, validate, and store structured BIS
    standards from a curated dataset PDF.

    No chunks are created.
    """

    # 1. Parse raw records
    records = parse_dataset_pdf(pdf_path)

    # 2. Universal normalization
    standards, normalization_errors = normalize_dataset(records)

    # 3. Validate normalized records
    validation = validate_standards(standards)

    # 4. Store valid records
    inserted = []

    for standard in validation["valid"]:
        standard_id = upsert_standard(
            standard.model_dump()
        )

        inserted.append(
            {
                "standardNumber": standard.standardNumber,
                "id": standard_id,
            }
        )

    return {
        "total": len(records),
        "normalized": len(standards),
        "inserted": len(inserted),
        "normalizationErrors": normalization_errors,
        "validationErrors": validation["invalidCount"],
        "standards": inserted,
    }


def ingest_dataset_to_chunks(
    pdf_path: str,
    embedding_model: EmbeddingModel | None = None,
) -> dict:
    """
    Parse, normalize, validate, and store BIS standards
    as searchable chunks with embeddings.

    Flow:

        PDF
        ↓
        parse_dataset_pdf()
        ↓
        universal normalization
        ↓
        BISStandard
        ↓
        validate_standards()
        ↓
        standard_chunker
        ↓
        embeddings
        ↓
        MongoDB
    """

    # 1. Parse raw records
    records = parse_dataset_pdf(pdf_path)

    # 2. Universal normalization
    standards, normalization_errors = normalize_dataset(records)

    # IMPORTANT:
    # Keep the existing validator behavior.
    validation = validate_standards(standards)

    if validation["invalid"]:
        raise ValueError(
            f"Dataset contains {validation['invalidCount']} "
            "invalid standard records."
        )

    # 3. Create embedding model once
    if embedding_model is None:
        embedding_model = EmbeddingModel()

    total_chunks = 0
    standard_results = []

    # 4. Process each standard
    for standard in validation["valid"]:

        # Store structured metadata
        upsert_standard(
            standard.model_dump()
        )

        # Get MongoDB standard ID
        standard_id = get_standard_id(
            standard.standardNumber
        )

        # Convert standard into searchable chunks
        chunks = chunk_standard(standard)

        standard_chunk_count = 0

        # Generate embeddings and store chunks
        for chunk in chunks:

            embedding = embedding_model.embed_text(
                chunk["text"]
            )

            document = {
                "standardId": standard_id,
                "standardNumber": standard.standardNumber,
                "chunkIndex": chunk["chunkIndex"],
                "text": chunk["text"],
                "embedding": embedding,
            }

            insert_chunk(document)

            total_chunks += 1
            standard_chunk_count += 1

        standard_results.append(
            {
                "standardNumber": standard.standardNumber,
                "chunks": standard_chunk_count,
            }
        )

    return {
        "total": len(records),
        "normalized": len(standards),
        "standards": len(validation["valid"]),
        "chunks": total_chunks,
        "normalizationErrors": normalization_errors,
        "validationErrors": validation["invalidCount"],
        "results": standard_results,
    }