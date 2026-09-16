from pathlib import Path

from app.ingestion.pipeline import ingest_dataset_to_chunks


def test_ingest_dataset_to_chunks(monkeypatch):
    standards_inserted = []
    chunks_inserted = []

    def fake_upsert(standard):
        standards_inserted.append(standard)
        return "test-id"

    def fake_get_standard_id(standard_number):
        return f"id-{standard_number}"

    def fake_insert_chunk(chunk):
        chunks_inserted.append(chunk)
        return "chunk-id"

    class FakeEmbeddingModel:
        def embed_text(self, text):
            return [0.1, 0.2, 0.3]

    monkeypatch.setattr(
        "app.ingestion.pipeline.upsert_standard",
        fake_upsert,
    )

    monkeypatch.setattr(
        "app.ingestion.pipeline.get_standard_id",
        fake_get_standard_id,
    )

    monkeypatch.setattr(
        "app.ingestion.pipeline.insert_chunk",
        fake_insert_chunk,
    )

    result = ingest_dataset_to_chunks(
        str(Path("data/raw/10set.pdf")),
        embedding_model=FakeEmbeddingModel(),
    )

    assert result["standards"] == 10
    assert result["chunks"] > 0

    assert len(standards_inserted) == 10
    assert len(chunks_inserted) == result["chunks"]

    for chunk in chunks_inserted:
        assert "standardId" in chunk
        assert "standardNumber" in chunk
        assert "chunkIndex" in chunk
        assert "text" in chunk
        assert "embedding" in chunk

        assert len(chunk["embedding"]) == 3