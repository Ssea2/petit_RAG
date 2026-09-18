from lancedb.pydantic import LanceModel

class ParserMessage(LanceModel):
    filename: str
    chunk: list[str]

class EmbeddingMessage(LanceModel):
    filename: str
    chunk : list[str]
    chunk_numer: int
    embeddings: list[list[float]]

class DataBaseRows(LanceModel):
    embedding : list[float]
    chunk: str
    filename: str
    filepart: int

