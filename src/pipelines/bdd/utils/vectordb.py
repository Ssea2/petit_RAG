import sqlite3
from typing import List, Text
import sqlite_vec

from .models import ChunkInfo

class VectorDataBase:

    def __init__(self, config) -> None:
        self._config = config["bdd"]
        self.databasePath = self._config["path"]
        self.table = self._config["default_table"]
        self.embedding_size = self._config["embedding"]["size"]
        self.retrieval_limits = self._config["retrieval_limits"]

        self._connection()

    def _connection(self) -> None:
        self.bdd = sqlite3.connect(self.databasePath)
        self.bdd.enable_load_extension(True)
        sqlite_vec.load(self.bdd)
        self.bdd.enable_load_extension(False)
        self.bdd.row_factory = sqlite3.Row
        self.cursor = self.bdd.cursor()

        self.create_table(table=self.table)

    
    def create_table(self, table: str)-> None:
        if table not in ["default", ""]:
            self.cursor.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {table} USING vec0(
                    embedding float[{self.embedding_size}],
                    +chunkStartIndex INTEGER,
                    +chunkLength INTEGER,
                    +filename TEXT
                )
            """)
        else:
            raise ValueError(
                f"Invalid table name, choose a valid name other than ['default', ''] : {table}"
            )

    def _disconnect(self) -> None:
        self.bdd.close()

    def add_document(self, data) -> None:
        with self.bdd:
            self.cursor.executemany(f"""
                INSERT INTO {self.table} (embedding, chunkStartIndex, chunkLength, filename) 
                VALUES (?,?,?,?)
            """,
                data
            )

    def retrieval(self, vector: bytes) -> list[ChunkInfo]:
        results = self.cursor.execute(f"""
            SELECT distance, chunkStartIndex, chunkLength, filename
            FROM {self.table} 
            WHERE embedding MATCH ?
            ORDER BY distance
            LIMIT ?
        """, (vector, self.retrieval_limits)).fetchall()
        return [ChunkInfo(**dict(chunk)) for chunk in results]

