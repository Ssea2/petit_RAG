from .utils import Embedder, DocumentsParser, VectorDataBase

class DataBaseManager:

    def __init__(self, config) -> None:
        self.config = config
        self.chunk_size = self.config["bdd"]["parser"]["chunk_size"]
        self.padding = self.config["bdd"]["parser"]["padding"]
        self.embedder = Embedder(config)
        self.parser = DocumentsParser(chunk_size=self.chunk_size, padding=self.padding)
        self.database = VectorDataBase(config)

    def add_document(self, documents: list[str]):
        pass
