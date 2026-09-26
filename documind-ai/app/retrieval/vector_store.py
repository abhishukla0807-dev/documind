from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document

from app.config import get_settings
from app.llm.provider import get_embedding_client
from app.exceptions import VectorStoreUnavailableError
from typing import List


settings = get_settings()


class QdrantStoreManager:
    """
    Manages Qdrant collection lifecycle: ensuring a collection exists
    with the correct schema, and indexing pre-built Documents into it.

    This class only knows about STORAGE — it does not build Documents
    or apply embedding prefixes; that responsibility belongs to
    ContextualEmbedder.
    """

    def __init__(self):
        try:
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
            self.embeddings = get_embedding_client()
        except Exception as e:
            raise VectorStoreUnavailableError(f"Could not connect to Qdrant: {e}")

    def collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)

    def delete_collection(self, collection_name: str) -> None:
        if self.client.collection_exists(collection_name):
            self.client.delete_collection(collection_name)

    def _ensure_collection(self, collection_name: str) -> None:
        """
        Ensures the collection exists with the correct 768-dimension vector
        space and Cosine similarity metric.
        """
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )




    def index_documents(
        self,
        documents: List[Document],
        collection_name: str,
        force_recreate: bool = False
    ) -> int:
        """
        Indexes the given (already-prefixed) Documents into the named
        collection.

        force_recreate=False (default): existing collection is reused,
        new points are appended — safe for repeated/incremental ingests.

        force_recreate=True: existing collection is dropped first,
        giving a full clean re-index. Caller must opt in explicitly.
        """
        if not documents:
            return 0

        try:
            if force_recreate:
                self.delete_collection(collection_name)

            self._ensure_collection(collection_name)

            Qdrant(
                client=self.client,
                collection_name=collection_name,
                embeddings=self.embeddings,
            ).add_documents(documents)

            return len(documents)

        except VectorStoreUnavailableError:
            raise
        except Exception as e:
            raise VectorStoreUnavailableError(f"Failed to index documents in Qdrant: {e}")




    #phase 3.1 c-->added a search method

    def search(self, collection_name: str, query_vector: List[float], top_k: int = 5):
        """
        Performs a similarity search in the given collection and returns
        raw Qdrant scored points (payload + similarity score).
        """
        try:
            return self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k
            )
        except Exception as e:
            raise VectorStoreUnavailableError(f"Qdrant search failed: {e}")