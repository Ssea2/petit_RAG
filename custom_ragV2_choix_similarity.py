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
#from llama_index.core import SimpleDirectoryReader
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import time
import hashlib
from tqdm import  tqdm

PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

def upload_data(file,embmod, isdir=False,required_ext = "**/*.pdf"):

    chunk_size = 26
    chunk_overlap = 4

    # Créer un splitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=128)
    print("récupération des fichiers")
    if isdir==True:
        """reader = SimpleDirectoryReader(
            input_dir=file,
            required_exts=required_exts,
            recursive=True,
        )"""
        loader = DirectoryLoader(file, glob=required_ext, loader_cls=PyMuPDFLoader, recursive=True, silent_errors=True)

    else:
        """reader = SimpleDirectoryReader(
            input_files=file,
        )
        """
        loader = TextLoader(file)
    docs = loader.load()#reader.load_data()
    split_docs = []
    print("découpage des fichiers")
    for doc in docs:
        split_docs.extend(splitter.split_documents([doc])) 
    #print(split_docs[0].metadata)
    print("formatage des données")
    data = {}
    for i in tqdm(range(len(split_docs))):
        doc = str(split_docs[i].page_content)+"<PATH>"+str(split_docs[i].metadata["file_path"])
        embdata = ollama.embed(model=embmod, input=doc)["embeddings"]
        id = hashlib.sha256(doc.encode()).hexdigest()
        #data[id]=doc
        chroma_collection.upsert(
            ids=id,
            documents=doc,
            embeddings=embdata
        )
    
    """idl = list(data.keys())
    context_doc = list(data.values())
    n=len(idl)
    print("sauvegarde des fichiers")
    for i in tqdm(range(0, n, 1)):
        toget = n-i
        idl = idl[i:i+toget]
        docl = context_doc[i:i+toget]
        chroma_collection.upsert(
            ids=idl,
            documents=docl
        )"""
    return 0 


def RAG_stack(input_query, history, llm="llama3.2:1b"):
    start=time.time()
    #print("query",start)
    input_query = str(history)+","+input_query
    results = chroma_collection.query(
      query_texts=[input_query], # Chroma will embed this for you
      n_results=10 # how many results to return
    )
    dataresult = results["documents"]
    #distanceresult = results["distances"]
    #retrieved_knowledge = zip(dataresult,distanceresult)
    files = []
    for i in dataresult[0]:
        files.append(i.split("<PATH>")[-1])
    files = set(files)
    #print("prompt",start-time.time())
    #print(files)
    print(results)
    instruction_prompt = f'''You are a helpful chatbot.
    Use only the following pieces of context to answer the question, if no context respond "no information available". Don't make up any new information:
    question: {input_query}
    context: {dataresult}
    '''

    #print(results)
    stream = ollama.chat(
        model=llm,
        messages=[
        {'role': 'system', 'content': instruction_prompt},
        {'role': 'user', 'content': input_query},
        ],
        stream=True,
    )
    #print("print",start-time.time())
    # print the response from the chatbot in real-time
    reponse=[]
    #print('Chatbot response:')
    for chunk in stream:
        rep = chunk['message']['content']
        print(NEON_GREEN + rep + RESET_COLOR, end='', flush=True)
        reponse.append(rep)
    print("\n\nSOURCE:")
    for file in files:
        print(PINK+file+RESET_COLOR)
    return input_query

embm = "nomic-embed-text"
embedding_model = OllamaEmbeddingFunction(
    model_name=embm,     # ou "mxbai‑embed‑large", ou "chroma/all‑minilm‑l6‑v2‑f32"
    url="http://localhost:11434/api/embeddings",)

client = chromadb.PersistentClient(path="chroma_db/robia") # robia/isa88 robia2(filtered robia)
chroma_collection = client.get_or_create_collection("robia3",embedding_function=embedding_model,configuration={
        "hnsw": {
            "space": "cosine",
        }
    })

#upload_data("./data", isdir=True, embmod=embm)
history=[]
while True:
    prompt = input("prompt: ")
    if prompt.lower()=="/bye":
        break
        pass
    if prompt.lower()=="/clear":
        history=[]
        pass
    else:
        tmp=RAG_stack(input_query=prompt, history=history, llm="qwen3:0.6b-q4_K_M")
        history.append(tmp)