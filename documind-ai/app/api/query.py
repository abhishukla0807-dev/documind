from fastapi import APIRouter, HTTPException, Depends

from app.schemas import QueryRequest, QueryResponse, SourceReference
from app.retrieval.retriever import CodeRetriever
from app.retrieval.vector_store import QdrantStoreManager
from app.ingestion.embedder import ContextualEmbedder
from app.llm.prompts import build_query_messages
from app.llm.generator import AnswerGenerator
from app.exceptions import (
    VectorStoreUnavailableError,
    EmbeddingServiceUnavailableError,
    GenerationServiceUnavailableError,
)

router = APIRouter(tags=["Query"])


def get_retriever() -> CodeRetriever:
    """
    Dependency provider — constructs a CodeRetriever with its required
    collaborators. Using FastAPI's Depends() here means the retriever
    (and its underlying clients) can be swapped out in tests without
    touching the endpoint function.
    """
    return CodeRetriever(
        store_manager=QdrantStoreManager(),
        embedder=ContextualEmbedder()
    )


@router.post("/ai/query", response_model=QueryResponse)
async def query_repository(
    request: QueryRequest,
    retriever: CodeRetriever = Depends(get_retriever)
):
    """
    End-to-end RAG query pipeline:
    Retrieve relevant chunks -> Build grounded prompt -> Generate answer.
    """
    try:
        chunks = retriever.retrieve(
            repo_id=request.repo_id,
            question=request.question,
            top_k=request.top_k
        )

        messages = build_query_messages(request.question, chunks)

        generator = AnswerGenerator()
        answer_text = generator.generate(messages)

        sources = [
            SourceReference(
                file_path=chunk["file_path"],
                start_line=chunk["start_line"],
                end_line=chunk["end_line"],
                layer=chunk["layer"],
                score=chunk["score"]
            )
            for chunk in chunks
        ]

        return QueryResponse(
            answer=answer_text,
            sources=sources,
            repo_id=request.repo_id
        )

    except VectorStoreUnavailableError as e:
        raise HTTPException(status_code=503, detail=f"Vector store unavailable: {e}")

    except EmbeddingServiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=f"Embedding service unavailable: {e}")

    except GenerationServiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=f"Generation service unavailable: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query pipeline failed unexpectedly: {e}")