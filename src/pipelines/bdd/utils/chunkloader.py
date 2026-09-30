from collections import defaultdict
import os

from .models import ChunkInfo

class ChunkLoader:

    def __init__(self, config, reader) -> None:
        self.reader = reader
        self.sources_folder = config["sources_dir"]

    def groupby_name(self, chunks: list[ChunkInfo]):
        groups = defaultdict(lambda : defaultdict(list))
        for chunk in chunks:
            groups[chunk.filename]["chunkStartIndex"].append(chunk.chunkStartIndex)
            groups[chunk.filename]["chunkLength"].append(chunk.chunkLength)
        return groups

    def get_chunk(self, groups: dict[str, list[int]]) -> list[tuple[int,int]]:
        sorted_index = sorted(zip(groups["chunkStartIndex"], groups["chunkLength"]))
        chunks = []
        currentStart = sorted_index[0][0]
        currentLength = sorted_index[0][1]

        for start, length in sorted_index[1:]:
            currentEnd = currentStart + currentLength
            end = start + length
            if currentEnd >= start:
                currentLength = max(currentEnd, end) - currentStart
            else:
                chunks.append((currentStart, currentEnd))
                currentStart = start
                currentLength =  length
        chunks.append((currentStart, currentStart+currentLength))
        return chunks


    def load(self, chunkinfo: list[ChunkInfo]) -> tuple[list[str], list[str]]:
        groups = self.groupby_name(chunkinfo)
        retrieved_content = []
        sources = set()
        for file in groups.keys():
            file_path = os.path.join(self.sources_folder,  file)
            chunks = self.get_chunk(groups[file])
            content = self.reader.read(file_path)
            retrieved_content.extend(
                [content[startidx:endidx] for startidx,endidx in chunks]
            )
            sources.add(file_path)
        return retrieved_content, list(sources)
