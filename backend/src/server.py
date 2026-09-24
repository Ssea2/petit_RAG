from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse

from pipelines import rag_pipeline, documents_pipeline

app = FastAPI()



@app.post("/language_model/question", response_model=StreamingResponse)
async def rag_anwser(prompt:str) -> StreamingResponse:
    return rag_pipeline(prompt)


@app.post("/database/documents")
async def add_document(documents: list[UploadFile]= File(...)):
    return documents_pipeline(documents, action="POST")


@app.delete("/database/documents")
async def delete_document(documents: list[str):
    return documents_pipeline(documents, action="DELETE")
