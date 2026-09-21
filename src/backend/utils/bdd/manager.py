import lancedb
from numpy import delete
import ollama

from .utils.parser import DocumentsParser
from .utils.models import ParserMessage, EmbeddingMessage, DataBaseRows
from .utils.embedder import EmbedManager

class bdd_manager:

    def __init__(self, config) -> None:
        self._config = config["bdd_manager"]
        self.bdd_url =self._config["bdd_path"]
        self.chunk_size = self._config["parser"]["chunk_size"]
        self.embedding_model = self._config["embedding_model"]["name"]
        self.max_retrieval = self._config["max_retrieval"]

        self.parser = DocumentsParser(self.chunk_size)
        self.embed = EmbedManager(self.embedding_model)
        self._bdd_connection()
        self.set_table("defaull")
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
            self.table = self.bdd.create_table(table_name, schema=DataBaseRows, mode="overwrite")
            
        return None

    def _multifile_parser(self, filesnames: list[str]) -> list[ParserMessage]:
        return [self.parser.parse(file) for file in filesnames]

    def _multifile_embedding(self, files_datas: list[ParserMessage]) -> list[EmbeddingMessage]:
        return [self.embed.embed(data) for data in files_datas]

    def _rows_making(self, datas: list[EmbeddingMessage]) -> list[DataBaseRows]:
        rows = []
        for message in datas:
            for idx in range(message.chunk_numer):
                rows.append(
                    DataBaseRows(
                        embedding=message.embeddings[idx],
                        chunk=message.chunk[idx],
                        filename=message.filename,
                        filepart=idx
                    )
                )
        return rows

    def add_documents(self, documents: list[str]) -> None:
        parsed_documents = self._multifile_parser(documents)
        embedded_documents = self._multifile_embedding(parsed_documents)
        rows = self._rows_making(embedded_documents)
        table_size = self.table.count_rows()
        self.table.add(
            data=[row.model_dump() for row in rows]
        )
        if table_size == 0:
            self.table.create_index(
                vector_column_name="embedding",
                index_type="IVF_HNSW_SQ"
            )
        else:
            self.table.optimize()
        return None


    def retrieval(self, prompt: str) -> list:
        message = ParserMessage(
                filename="None",
                chunk=[prompt]
        )
        if self.table.count_rows() > 0:
            results = self.table.search(
                query=self.embed.embed(message).embeddings
            ).limit(self.max_retrieval).select(["filename", "chunk"]).to_list()
        else:
            results = []
        return results

    def delete_documents(self, documents: list) -> None:
        request_documents = ' '.join("'" + document +"'" for document in documents)
        self.table.delete(f"filename IN ({request_documents})")
        if self.table.count_rows() > 0:
            self.table.optimize()
        return None
