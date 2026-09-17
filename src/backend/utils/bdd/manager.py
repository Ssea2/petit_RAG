import lancedb
import ollama

from config_loader.loader import API_config
from utils.parser import DocumentsParser
from utils.embed import EmbedManager

class bdd_manager:

    def __init__(self) -> None:
        # parameters
        self._config = API_config()["bdd_manager"]
        self.bdd_url =self._config["bdd_path"]
        self.chunk_size = self._config["chunk_size"]
        self.embedding_model = self._config["embedding_model"]

        # initialisation
        self.parser = DocumentsParser(self.chunk_size)
        self.embed = EmbedManager()
        self._bdd_connection()
        return None

    def _bdd_connection(self) -> None:
        self.bdd = lancedb.connect(self.bdd_url)
        return None

    def set_table(self, table_name: str) -> None:
        """
        Search for the table inside the database, 
        if it can't find it, it will be create.
        """
        if table_name is self.bdd.list_tables():
            self.table = self.bdd.open_table(table_name)
        else:
            self.table = self.bdd.create_table(table_name)
        return None

    def _parsing(self, documents : list[str]):
        return {document: self.parser.parse(document) for document in documents}

    def _embedding(self, data):
        pass


    def add_documents(self, documents: list[str]):
        parsed_documents = 
