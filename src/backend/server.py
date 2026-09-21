from fastapi import FastAPI

from utils.bdd.manager import bdd_manager
from utils.slm.manager import slm_manager
from utils.config_loader import API_config
from utils.models import OKresponces, Documents, Prompt, RagAwnser

config = API_config()
bdd = bdd_manager(config=config)
slm = slm_manager(config=config)
app = FastAPI()


@app.post("/small_language_model/question", response_model=RagAwnser)
def slm_anwser(prompt: Prompt):
    informations = bdd.retrieval(prompt.question)
    anwser, sources = slm.generate(prompt=prompt.question, documents=informations)
    return RagAwnser(response=anwser, sources=sources)

@app.post("/database/docs", response_model=OKresponces)
def bdd_upload(documents: Documents):
    bdd.add_documents(documents.names)
    return OKresponces()

@app.delete("/database/docs", response_model=OKresponces)
def bdd_remove(documents: Documents):
    bdd.delete_documents(documents.names)
    return OKresponces()

