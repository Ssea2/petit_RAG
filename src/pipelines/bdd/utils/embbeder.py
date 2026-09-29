from typing import List
import llama_cpp
import os

from numpy import float32

class Embedder:

    def __init__(self, config) -> None:
        self._config = config["bdd"]["embedding"]
        self.model_path = self._config["name"]

        self._check_model(self.model_path)

    def _check_model(self, path) -> None:
        if os.path.isfile(path):
            self._init_model(path)
        else:
            raise FileNotFoundError(
                f"Embedding model not found: {path}"
            )

    def _init_model(self, path) -> None:
        self.embedding_model = llama_cpp.Llama(
            model_path=path,
            embedding=True,
            verbose=False
        )

    def embed(self, chunk: list[str]) -> list[list]:
        embeddings = self.embedding_model.create_embedding(
            input=chunk
        )["data"]
        return [ chunk["embedding"] for chunk in embeddings]
