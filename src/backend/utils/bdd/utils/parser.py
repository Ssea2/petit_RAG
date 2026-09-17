import os
from models import ParserMessage

class DocumentsParser:

    def __init__(self, chunk_size: int) -> None:
        self.extension = [".txt", ".md"]
        self.chunk_size = chunk_size

    def parse(self, filename: str) -> ParserMessage:
        _, extension_ = os.path.splitext(filename)
        match extension_:
            case ".txt" | ".sh" | ".bash" | ".md":
                return self._str_parser(filename)
            case ".pdf":
                return self._pdf_parser(filename)
            case _ :
                raise ValueError(
                    f"Unsupported file extension: {extension_}"
                )

    def _str_parser(self, filename: str) -> ParserMessage:
        with open(filename, "r") as opened_filename:
            data = opened_filename.read()
        return ParserMessage(file_name=filename, chunk=self._parser(data))

    def _pdf_parser(self, filename: str) -> ParserMessage:
        return ParserMessage(file_name=filename, chunk=["a"])


    def _parser(self, file_data: str) -> list[str]:
        file_len = len(file_data)
        return [
            file_data[start_idx: start_idx+self.chunk_size] 
            for start_idx in range(0, file_len, self.chunk_size)
        ]
