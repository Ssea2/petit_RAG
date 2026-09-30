from pydantic import config
import pymupdf4llm
import pymupdf
from fastapi import UploadFile, File
import os 
import pathlib

class DocumentsReader:

    def __init__(self, config) -> None:
        self.config: dict = config
        self.sources_dir: str = config["sources_dir"]

        self._check_dir(self.sources_dir)

    def _check_dir(self, dir_path) -> None:
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(f"Sources folder not found, you need to create it : {dir_path}")

    def str_reader(self, file: str | bytes) -> str:
        if isinstance(file, bytes):
            content = file.decode()
        elif isinstance(file, str):
            with open(file, "r") as buffer:
                content = buffer.read()
        else:
            raise ValueError("file need to be a str or bytes not a {type(file)}")
        return content

    def pdf_reader(self, file:str | bytes) -> str:
        if isinstance(file, str):
            content = pymupdf4llm.to_markdown(file)
        elif isinstance(file, bytes):
            document = pymupdf.open(stream=file, filetype="pdf")
            content = pymupdf4llm.to_markdown(document)
        else:
            raise ValueError("file need to be a str or bytes not a {type(file)}")

        if not isinstance(content, str):
            raise ValueError("content need to be a str")
        return content

    async def _stream_reader(self, file: UploadFile=File(...)) -> tuple[str, bytes]:
        content = []
        filename = file.filename
        if not isinstance(filename, str):
            raise TypeError("you need to have a valid filename not None")
    
        destination = os.path.join(self.sources_dir, filename)
        with open(destination, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
                content.append(chunk)

        return filename, b"".join(content)

    def read(self, filename: str, filedata: bytes | None = None) -> str:
        extension = pathlib.Path(filename).suffix

        if isinstance(filedata, bytes):
            file = filedata
        else:
            file = filename
        
        match extension:
            case ".txt" | ".md" | ".sh":
                return self.str_reader(file)
            case ".pdf":
                return self.pdf_reader(file)
            case _:
                raise ValueError(f"Bad file extension : {extension}")

    async def read_stream(self, file: UploadFile = File(...)) -> tuple[str, str]:
        filename, bytes_content = await self._stream_reader(file)
        content = self.read(filename, bytes_content)
        return content, filename
    
