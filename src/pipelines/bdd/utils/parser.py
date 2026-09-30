
class DocumentsParser:

    def __init__(self, chunk_size: int, padding: int) -> None:
        self.extension = [".txt", ".md"]
        self.chunk_size = chunk_size
        self.padding = padding

    def parse(self, file_data: str, filename: str) -> list[list[bytes | str | int]]:
        file_len = len(file_data)
        data = []
        for idx in range(0, file_len, self.chunk_size - self.padding):
            data.append(
                [file_data[idx:idx+self.chunk_size], idx, self.chunk_size, filename]
            )
        return data
