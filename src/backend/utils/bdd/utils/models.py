from pydantic import BaseModel


class ParserMessage(BaseModel):
    file_name: str
    chunk: list[str]

class EmbeddingMessage(BaseModel):
    pass
