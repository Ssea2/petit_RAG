
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


