from lancedb.pydantic import LanceModel, Vector
from typing import TypeAlias 


vector_: TypeAlias = Vector(384)


class ParserMessage(LanceModel):
    filename: str
    chunk: list[str]

class EmbeddingMessage(LanceModel):
    filename: str
    chunk : list[str]
    chunk_numer: int
    embeddings: list[vector_]

class DataBaseRows(LanceModel):
    embedding : vector_
    chunk: str
    filename: str
    filepart: int

