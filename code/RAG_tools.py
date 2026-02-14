"""doc utilisé:     
https://docs.trychroma.com/docs/overview/getting-started      
https://huggingface.co/blog/ngxson/make-your-own-rag        
https://docs.trychroma.com/docs/embeddings/embedding-functions          
https://rocm.docs.amd.com/projects/ai-developer-hub/en/v1.0/notebooks/inference/rag_ollama_llamaindex.html         
https://api.python.langchain.com/en/latest/document_loaders/langchain_community.document_loaders.directory.DirectoryLoader.html#langchain-community-document-loaders-directory-directoryloader        
GPT pour expliqué se que je comprennais pas 
code du prof
"""
import ollama
import chromadb
import json
import os 
#from llama_index.core import SimpleDirectoryReader
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import hashlib
from tqdm import  tqdm


class RAG_Upload():

    def __init__(self, db, embeding_model, chunk_size:int=4048, overlap_size:int=1028, name_files_in_bdd:str="bdd/rag/files_in_rag.txt"):
        # param splitter
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.overlap_size)


        # stockage temporaire
        self.docs:list = []
        self.split_docs:list = []

        # db 
        self.chroma_collection = db 
        self.embmod = embeding_model
        self.files_in_bdd = name_files_in_bdd

    def store_file_name(self, files:set):
        to_store = ";".join(files) + ";"
        with open(self.files_in_bdd, "a+") as file:
            file.write(to_store)

    def get_document(self, paths:list[str], required_ext:list[str]= ["**/*.pdf"]):
        for file in paths:
            isdir = os.path.isdir(file)
            if isdir==True:
                loader = DirectoryLoader(file, glob=required_ext, loader_cls=PyMuPDFLoader, recursive=True, silent_errors=True)
            else:
                loader = PyMuPDFLoader(file)
            self.docs = loader.load()#reader.load_data()"""

    def split_document(self):
        for doc in self.docs:
            self.split_docs.extend(self.splitter.split_documents([doc])) 

    def fill_db(self):
        files_paths = set()
        for i in tqdm(range(len(self.split_docs))):
            doc = str(self.split_docs[i].page_content)
            embdata = ollama.embed(model=self.embmod, input=doc)["embeddings"]
            id = hashlib.sha256(doc.encode()).hexdigest()
            nospace_filename = str(self.split_docs[i].metadata["file_path"])#.replace(" ", "_")
            files_paths.add(nospace_filename)
            #data[id]=doc
            self.chroma_collection.upsert(
                ids=id,
                documents=doc,
                embeddings=embdata,
                metadatas={"file_path": nospace_filename}
            )
        self.store_file_name(files_paths)

    def stack(self, paths:list):
        self.get_document(paths)
        self.split_document()
        self.fill_db()

class RAG_Delete():

    def __init__(self, db, name_files_in_bdd:str="bdd/rag/files_in_rag.txt"):
        # fichier pour lire les fichier sauvegardé
        self.file_for_files_in_bdd = name_files_in_bdd
        self.collection = db

        # fichier lue
        self.all_files_in_bdd: list = []
    
    def get_files_saved(self):
        with open(self.file_for_files_in_bdd, "r") as file:
            self.all_files_in_bdd = [file for file in file.read().split(";") if len(file) > 1]
        return self.all_files_in_bdd

    def show_saved_files(self):
        print(self.all_files_in_bdd)
    
    def remove_data(self, tokeep):
        #print({"file_path": path for path in self.all_files_in_bdd})
        self.collection.delete(where={
                "file_path": {
                    "$in": self.all_files_in_bdd  # Doit être une liste de strings
                }
            }
        )
        with open(self.file_for_files_in_bdd, "w") as file:
            file.write(";".join(tokeep) + ";")
        #print(self.collection.get(limit=1, include=["metadatas"])['metadatas'])


class RAG_Answer():

    def __init__(self, db, llm="qwen3:0.6b-q4_K_M", top_n_result: int = 15):
        
        self.llm = llm
        self.db  = db
        self.n_result = top_n_result
        self.results = []
        self.files_sources = []
        self.textdata = []
        self.instruction_prompt = "Tu est un chatbot utile, si il y a du contexte entre les banieres <CONTEXTE> répond a la question présent dans les banieres <QUESTION> "


    def get_input_prompt(self, input_query, history):
        self.prompt = str(history)+","+input_query

    def similarity_search(self, threshold=0.3):
        self.files_sources = []
        self.textdata = []
        self.results = self.db.query(
        query_texts=[self.prompt], # Chroma will embed this for you
        n_results=self.n_result # how many results to return
        )
        #print(self.results)
        len_result = len(self.results['ids'][0])
        for i in range(len_result):
            if self.results["distances"][0][i] < threshold:
                pass 
            else:
                self.files_sources.append(self.results["metadatas"][0][i]["file_path"])
                self.textdata.append(self.results["documents"])
        self.files_sources = list(set(self.files_sources))


        

    def update_prompt(self):
        self.enchanced_prompt = f'''Tu est un chatbot utile, 
        si il y a du contexte entre les bannieres <CONTEXTE> répond a la question présent dans les bannieres <QUESTION> 
        de maninère a répondre au mieux avec le plus de détails. Si il y a des url tu les met sous la forme <a href="url" style="text-decoration:none; color:blue;">"url"</a>' 
    
        <QUESTION> {self.prompt} <QUESTION>
        <CONTEXTE> {self.textdata} <CONTEXTE>'''
        #print(self.enchanced_prompt)
        
    def rag_prompt(self):
        stream = ollama.chat(
        model=self.llm,
        messages=[
        {'role': 'system', 'content': self.instruction_prompt},
        {'role': 'user', 'content': self.enchanced_prompt},
        ],
        stream=True,
        )
        return stream, self.files_sources

    def rag_stack(self, input, hist: list = []):
        self.get_input_prompt(input, hist)
        self.similarity_search()
        self.update_prompt()
        stream, files = self.rag_prompt()
        return stream, files


if __name__=="__main__":
    embm = "nomic-embed-text"
    embedding_model = OllamaEmbeddingFunction(
        model_name=embm,     # ou "mxbai‑embed‑large", ou "chroma/all‑minilm‑l6‑v2‑f32"
        url="http://localhost:11434/api/embeddings",)

    client = chromadb.PersistentClient(path="bdd/rag") # robia/isa88 robia2(filtered robia)
    chroma_collection = client.get_or_create_collection("rag",embedding_function=embedding_model,configuration={
            "hnsw": {
                "space": "cosine",
            }
        })

    #RAG_Upload(chroma_collection, embeding_model=embm, chunk_size=512, overlap_size=128).stack(["docs/numpy-user.pdf"])
    t = RAG_Delete()
    t.get_files_saved()
    t.show_saved_files()
    print()

    #print(chroma_collection.get(include=["metadatas"]).get("metadatas"))