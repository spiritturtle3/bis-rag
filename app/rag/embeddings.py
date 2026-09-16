from fastembed import TextEmbedding


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingModel:
    _model = None

    def __init__(self):
        if EmbeddingModel._model is None:
            EmbeddingModel._model = TextEmbedding(
                model_name=MODEL_NAME
            )

        self.model = EmbeddingModel._model

    def embed_text(self, text: str) -> list[float]:
        vector = list(
            self.model.embed([text])
        )[0]

        return vector.tolist()

    def embed_texts(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        vectors = list(
            self.model.embed(texts)
        )

        return [
            vector.tolist()
            for vector in vectors
        ]