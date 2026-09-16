import pytest

from app.ingestion.chunker import chunk_text


def test_chunk_text():
    text = "A" * 2500

    chunks = chunk_text(
        text,
        chunk_size=1000,
        overlap=200
    )

    assert len(chunks) == 3
    assert len(chunks[0]) == 1000
    assert len(chunks[1]) == 1000
    assert len(chunks[2]) == 900


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=100, overlap=100)


def test_empty_text():
    assert chunk_text("") == []