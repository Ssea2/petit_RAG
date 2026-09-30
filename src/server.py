from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from .pipelines import PetitRagCore

config = {
"bdd":{
	"path": "data/text.db",
    "default_table": "embedding",
    "parser": {
		"padding": 100,
		"chunk_size": 512
	},
	"embedding": {
		"name": "assets/embeddings/nomic-embed-text-v1.5.Q4_K_M.gguf",
        "size": 768,
    },
    "retrieval_limits": 10,
    "sources_dir": "./uploads",
},
"slm": {
    "model": "assets/language_model/qwen2.5-0.5b-instruct-q4_k_m.ffuf",
        "personality" : "You are an helpfull teacher/science popularizer. Based only on the sources you get behind <SOURCES> banner you anwser the user question with the indent to improve his comprehension/knowledge on the subject. The question is before <SOURCES> banner",
    },
}

core = PetitRagCore(config)

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static", html=True), name="static")

@app.post("/language_model/question")
async def rag_anwser(prompt:str = Body(..., embed=True)): # -> StreamingResponse:
    core.rag_pipeline(prompt)


@app.post("/database/documents")
async def add_document(files: list[UploadFile]= File(...)):
    await core.documents_stack(action="POST", documents=files)
#return documents_pipeline(documents, action="POST")


@app.delete("/database/documents")
async def delete_document(documents: list[str]):
    pass
