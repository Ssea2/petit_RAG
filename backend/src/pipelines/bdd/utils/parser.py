import pathlib
import pymupdf4llm

class DocumentsParser:

    def __init__(self, chunk_size: int, padding: int) -> None:
        self.extension = [".txt", ".md"]
        self.chunk_size = chunk_size
        self.padding = padding

    def parse(self, filename: str):
        extension_ = pathlib.Path(filename).suffix
        match extension_:
            case ".txt" | ".sh" | ".bash" | ".md":
                return self._str_parser(filename)
            case ".pdf":
                return self._pdf_parser(filename)
            case _ :
                raise ValueError(
                    f"Unsupported file extension: {extension_}"
                )

    def _str_parser(self, filename: str):
        return self._parser(file_data=self.read_str(filename), filename=filename)

    def _pdf_parser(self, filename:str):
        return self._parser(file_data=self.read_pdf(filename), filename=filename)

    def read_str(self, filename: str):
        with open(filename, "r") as opened_filename:
            data = opened_filename.read()
        return data

    def read_pdf(self, filename: str):
        return pymupdf4llm.to_markdown(filename)


    def _parser(self, file_data: str, filename: str) -> list[list[str, int, int, str]]:
        file_len = len(file_data)
        data = []
        for idx in range(0, file_len, self.chunk_size - self.padding):
            data.append(
                [file_data[idx:idx+self.chunk_size], idx, self.chunk_size, filename]
            )
        return data
