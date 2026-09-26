from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language


class PreciseCodeChunker:
    """
    Splits source files into syntax-aware chunks using LangChain,
    tracks exact start/end line numbers, and infers the architectural
    layer of each file for context-enriched embeddings.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_overlap = chunk_overlap

        self.java_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.JAVA,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.general_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def _infer_layer(self, file_path: str) -> str:
        """Heuristic to infer application layer for context enrichment."""
        path_lower = file_path.replace("\\", "/").lower()
        if "/exception/" in path_lower: return "exception handling"
        if "/service/" in path_lower: return "business logic"
        if "/controller/" in path_lower: return "REST API layer"
        if "/repository/" in path_lower: return "data access"
        if "/config/" in path_lower: return "configuration"
        if "/aspect/" in path_lower: return "cross-cutting aspect"
        if "/event/" in path_lower: return "application event handling"
        return "general code"

    def chunk_file(self, file_path: str, content: str, extension: str, repo_id: str) -> List[Dict[str, Any]]:
        """
        Splits file content into language-aware chunks and computes
        exact start/end line numbers.
        """
        if extension == ".java":
            raw_chunks = self.java_splitter.split_text(content)
        else:
            raw_chunks = self.general_splitter.split_text(content)

        chunks_with_metadata = []
        current_search_idx = 0
        layer = self._infer_layer(file_path)

        for idx, chunk_text in enumerate(raw_chunks):
            char_pos = content.find(chunk_text, current_search_idx)

            if char_pos != -1:
                # Advance the search cursor to just past the *unique* part
                # of this chunk (i.e. skip past the overlapping region),
                # so the next chunk's search doesn't re-match text inside
                # this chunk's overlap zone.
                advance = max(len(chunk_text) - self.chunk_overlap, 1)
                current_search_idx = char_pos + advance

                start_line = content.count('\n', 0, char_pos) + 1
                end_line = start_line + chunk_text.count('\n')
            else:
                # Chunk text not found verbatim (can happen if the splitter
                # normalizes whitespace) — fall back to safe defaults
                # rather than crashing.
                start_line, end_line = 1, 1

            chunks_with_metadata.append({
                "chunk_id": f"{repo_id}_{file_path}_{idx}",
                "content": chunk_text,
                "metadata": {
                    "repo_id": repo_id,
                    "file_path": file_path,
                    "extension": extension,
                    "start_line": start_line,
                    "end_line": end_line,
                    "layer": layer
                }
            })

        return chunks_with_metadata