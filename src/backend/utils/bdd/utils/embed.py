import ollama


class EmbedManager:

    def __init__(self, model) -> None:
        self.embedding_model = model
        self.available_models = self._get_available_models()

    def _get_available_models(self):
        return [model.model for model in list(ollama.list())[0][1]]

    def embed(self, data):
        pass
