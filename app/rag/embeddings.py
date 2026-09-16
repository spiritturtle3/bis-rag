from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-en-v1.5"


class EmbeddingModel:
    _model = None

    def __init__(self):
        if EmbeddingModel._model is None:
            EmbeddingModel._model = SentenceTransformer(MODEL_NAME)

        self.model = EmbeddingModel._model

    def embed_text(self, text: str) -> list[float]:
        vector = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return vector.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return vectors.tolist()