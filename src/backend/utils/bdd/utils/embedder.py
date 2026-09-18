import ollama
from .models import ParserMessage, EmbeddingMessage

class EmbedManager:

    def __init__(self, model) -> None:
        self.embedding_model = model
        self.available_models = self._get_available_models()
        self._check_model_availability()

    def _get_available_models(self) -> list[str]:
        return [model.model for model in list(ollama.list())[0][1]]

    def _check_model_availability(self) -> None:
        if not self.embedding_model in self.available_models:
            ollama.pull(self.embedding_model)
            return None
        else:
            return None

    def embed(self, data: ParserMessage) -> EmbeddingMessage:
        embeddings = ollama.embed(
            model = self.embedding_model, 
            input = data.chunk
        )['embeddings']
        return EmbeddingMessage(
                    filename = data.filename,
                    chunk = data.chunk,
                    chunk_numer = len(embeddings),
                    embeddings = embeddings
                    )
