
from fastapi import UploadFile, File

from .utils import Embedder, DocumentsParser, VectorDataBase, DocumentsReader, ChunkLoader

class DataBaseManager:

    def __init__(self, config) -> None:
        self.config = config
        self.chunk_size = self.config["bdd"]["parser"]["chunk_size"]
        self.padding = self.config["bdd"]["parser"]["padding"]
        self.embedder = Embedder(config)
        self.parser = DocumentsParser(chunk_size=self.chunk_size, padding=self.padding)
        self.database = VectorDataBase(config)
        self.reader = DocumentsReader(config)
        self.loader = ChunkLoader(config, self.reader)

    async def add_document(self, files: list[UploadFile]=File(...)) -> None:
        for file in files:
            content, filename = await self.reader.read_stream(file)
            data = self.parser.parse(file_data=content, filename=filename)
            chunk: list[str] = [row[0] for row in data if isinstance(row[0], str)]
            embeddings= self.embedder.embed(chunk=chunk)
            for row, embedding in zip(data, embeddings):
                row[0] = embedding
            self.database.add_document(data)

    def retrival(self, prompt: str) -> tuple[list[str], list[str]]:
        prompt_embedding = self.embedder.embed([prompt])[0]
        retrieved_data = self.database.retrieval(prompt_embedding)
        chunks, sources = self.loader.load(retrieved_data)
        return chunks, sources
