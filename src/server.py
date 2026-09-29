from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from .pipelines import rag_pipeline, documents_pipeline

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static", html=True), name="static")
#@app.post("/language_model/question", response_model=StreamingResponse)
#async def rag_anwser(prompt:str) -> StreamingResponse:
#    return rag_pipeline(prompt)


@app.post("/database/documents")
async def add_document(files: list[UploadFile]= File(...)):
    for file in files:
        filename = [file.filename]
        print(filename)
        content = []
        destination = f"./uploads/{file.filename}"
        print("FILENAME", file)
        with open(destination, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
                content.append(chunk)

#return documents_pipeline(documents, action="POST")


@app.delete("/database/documents")
async def delete_document(documents: list[str]):
    return documents_pipeline(documents, action="DELETE")
