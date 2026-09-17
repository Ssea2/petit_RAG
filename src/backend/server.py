import fastapi
import uvicorn

from utils.bdd.utils.parser import DocumentParser

t = DocumentParser(chunk_size=2)
print(t.parse("requirements.txt"))



