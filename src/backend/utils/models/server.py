from pydantic import BaseModel

class OKresponces(BaseModel):
    message: str = "OK"


class Documents(BaseModel):
    names : list[str]

class Prompt(BaseModel):
    question: str

class RagAwnser(BaseModel):
    response: str
    sources : list[str]
