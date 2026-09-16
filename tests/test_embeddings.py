from app.rag.embeddings import EmbeddingModel


def test_embedding_model():
    model = EmbeddingModel()

    vector = model.embed_text(
        "Steel pipes for water supply"
    )

    assert isinstance(vector, list)
    assert len(vector) > 0
    assert all(isinstance(value, float) for value in vector)