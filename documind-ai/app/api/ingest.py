import os
from fastapi import APIRouter, HTTPException, Depends

from app.schemas import IngestRequest, IngestResponse
from app.config import Settings, get_settings
from app.ingestion.loader import RepoLoader
from app.ingestion.chunker import PreciseCodeChunker
from app.ingestion.embedder import ContextualEmbedder
from app.retrieval.vector_store import QdrantStoreManager
from app.exceptions import EmbeddingServiceUnavailableError, VectorStoreUnavailableError

router = APIRouter(tags=["Ingestion"])


@router.post("/ai/ingest", response_model=IngestResponse)
async def ingest_repository(request: IngestRequest, settings: Settings = Depends(get_settings)):
    """
    End-to-end ingestion pipeline:
    Loads files -> Chunks them -> Injects Prefixes -> Embeds & Stores in Qdrant.
    """
    target_path = request.path if request.path else os.path.join(settings.BASE_REPO_PATH, request.repo_id)

    if not os.path.exists(target_path):
        raise HTTPException(
            status_code=404,
            detail=f"Repository path not found on disk: {target_path}"
        )

    try:
        loader = RepoLoader(target_path)
        files = loader.load_repository_files()

        if not files:
            return IngestResponse(
                status="FAILED",
                repo_id=request.repo_id,
                message="No valid source files found in the repository."
            )

        chunker = PreciseCodeChunker()
        all_chunks = []
        for f in files:
            chunks = chunker.chunk_file(
                file_path=f["file_path"],
                content=f["content"],
                extension=f["extension"],
                repo_id=request.repo_id
            )
            all_chunks.extend(chunks)

        embedder = ContextualEmbedder()
        documents = embedder.prepare_documents(all_chunks)

        collection_name = f"repo_{request.repo_id}"
        store_manager = QdrantStoreManager()
        already_existed = store_manager.collection_exists(collection_name)

        indexed_count = store_manager.index_documents(
            documents=documents,
            collection_name=collection_name,
            force_recreate=request.force_recreate
        )

        message = (
            f"Successfully indexed into collection '{collection_name}'"
            + (" (re-created)" if request.force_recreate and already_existed else "")
        )

        return IngestResponse(
            status="COMPLETED",
            repo_id=request.repo_id,
            total_files_loaded=len(files),
            chunks_indexed=indexed_count,
            message=message
        )

    except EmbeddingServiceUnavailableError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Embedding service (Ollama) is unavailable: {e}"
        )

    except VectorStoreUnavailableError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Vector store (Qdrant) is unavailable: {e}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion pipeline failed unexpectedly: {e}"
        )