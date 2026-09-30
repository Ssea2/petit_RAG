from pydantic import config

from .bdd.manager import DataBaseManager
from fastapi import UploadFile, File

class PetitRagCore:

    def __init__(self, config) -> None:
        self.core = DataBaseManager(config)

    def rag_pipeline(self, prompt: str):
        retrived_doc, sources = self.core.retrival(prompt)

    async def documents_stack(self, action:str, documents: list[UploadFile]=File(...)):
        match action:
            case "POST":
                return await self.core.add_document(files=documents)
            case "DELETE":
                return "2"
            case _:
                return None
