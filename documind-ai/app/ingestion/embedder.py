from typing import List, Dict, Any
from langchain_core.documents import Document


class ContextualEmbedder:
    """
    Transforms raw code chunks into enriched LangChain Documents
    using Asymmetric Task Prefixes (Pillar 1 & 2) and layer-based
    context enrichment (Pillar 3).
    """

    # Folder name → human-readable layer description.
    # Order matters only in that lookup is a simple substring match below.
    LAYER_HINTS = {
        "controller": "REST API layer",
        "service": "business logic layer",
        "repository": "data access layer",
        "entity": "data model / entity",
        "dto": "data transfer object",
        "exception": "exception handling",
        "config": "configuration",
        "aspect": "cross-cutting aspect (logging/timing)",
        "event": "application event handling",
        "security": "security / authentication",
        "git": "git operations utility",
    }

    def _infer_layer(self, file_path: str) -> str:
        """
        Infers the architectural layer of a file from its folder path,
        using the project's own package convention (controller/, service/, etc.).
        Falls back to a generic label when no known folder matches.
        """
        normalized = file_path.replace("\\", "/").lower()
        for folder_keyword, layer_name in self.LAYER_HINTS.items():
            if f"/{folder_keyword}/" in normalized:
                return layer_name
        return "general code"

    def prepare_documents(self, chunks: List[Dict[str, Any]]) -> List[Document]:
        documents = []
        for chunk in chunks:
            file_path = chunk["metadata"]["file_path"]
            raw_code = chunk["content"]
            layer = self._infer_layer(file_path)

            enriched_content = (
                f"search_document: File: {file_path} ({layer})\n{raw_code}"
            )

            # store the inferred layer in metadata too, so it can be
            # displayed or filtered on later without re-parsing the path
            chunk["metadata"]["layer"] = layer

            doc = Document(
                page_content=enriched_content,
                metadata=chunk["metadata"]
            )
            documents.append(doc)
        return documents

    def prepare_query(self, question: str) -> str:
        """
        Applies the asymmetric 'search_query:' prefix to a user's natural
        language question before embedding, so it aligns in vector space
        with document embeddings (which use 'search_document:').
        """
        return f"search_query: {question}"