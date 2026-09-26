from typing import List, Dict, Any

from app.ingestion.embedder import ContextualEmbedder
from app.llm.provider import get_embedding_client
from app.retrieval.vector_store import QdrantStoreManager
from app.exceptions import VectorStoreUnavailableError, EmbeddingServiceUnavailableError


class CodeRetriever:
    """
    Retrieves the most relevant code chunks for a natural-language
    question, using the same asymmetric embedding strategy that was
    used at ingestion time.
    """

    MIN_SIMILARITY_SCORE = 0.5

    def __init__(self, store_manager: QdrantStoreManager, embedder: ContextualEmbedder):
        self.store_manager = store_manager
        self.embedder = embedder
        self.embedding_client = get_embedding_client()

    def retrieve(self, repo_id: str, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Returns the top_k most relevant chunks for the given question,
        each with its content, file path, line range, layer, and
        similarity score.
        """
        collection_name = f"repo_{repo_id}"

        if not self.store_manager.collection_exists(collection_name):
            raise VectorStoreUnavailableError(
                f"No indexed data found for repo '{repo_id}'. Has it been ingested?"
            )

        query_vector = self._embed_query(question)

        scored_points = self.store_manager.search(
            collection_name=collection_name,
            query_vector=query_vector,
            top_k=top_k
        )

        return self._format_results(scored_points)

    def _embed_query(self, question: str) -> List[float]:
        """
        Applies the 'search_query:' asymmetric prefix (matching the
        'search_document:' prefix used at ingestion) and embeds the
        result into a query vector.
        """
        prefixed_query = self.embedder.prepare_query(question)

        try:
            return self.embedding_client.embed_query(prefixed_query)
        except Exception as e:
            raise EmbeddingServiceUnavailableError(f"Could not embed query: {e}")

    def _format_results(self, scored_points) -> List[Dict[str, Any]]:
        """
        Converts raw Qdrant ScoredPoints into clean dictionaries,
        discarding low-relevance matches below MIN_SIMILARITY_SCORE
        and stripping the ingestion-time embedding prefix from content.
        """
        results = []
        for point in scored_points:
            if point.score < self.MIN_SIMILARITY_SCORE:
                continue

            payload = point.payload
            metadata = payload.get("metadata", {})
            raw_content = self._strip_prefix(payload.get("page_content", ""))

            results.append({
                "content": raw_content,
                "file_path": metadata.get("file_path"),
                "start_line": metadata.get("start_line"),
                "end_line": metadata.get("end_line"),
                "layer": metadata.get("layer"),
                "score": round(point.score, 4)
            })

        return results

    @staticmethod
    def _strip_prefix(prefixed_content: str) -> str:
        """
        Removes the 'search_document: File: <path>\n' prefix that was
        added at ingestion time, returning just the raw code.
        """
        if "\n" in prefixed_content:
            return prefixed_content.split("\n", 1)[1]
        return prefixed_content