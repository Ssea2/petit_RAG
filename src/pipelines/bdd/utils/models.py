from dataclasses import dataclass

@dataclass
class ChunkInfo:
    distance: float
    chunkStartIndex: int
    chunkLength: int
    filename: str
