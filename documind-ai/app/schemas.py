from pydantic import BaseModel, Field
from typing import Optional, List


class HealthResponse(BaseModel):
    """Schema for service health status check."""
    status: str = Field(default="UP", description="Current liveness status of the service")
    app_name: str = Field(..., description="Configured application name")
    environment: str = Field(..., description="Runtime environment (e.g. development, production)")


class IngestRequest(BaseModel):
    """Schema for repository ingestion request received from Spring Boot."""
    repo_id: str = Field(..., description="UUID identifier of the cloned repository")
    path: Optional[str] = Field(None, description="Optional explicit directory path of the repository")
    force_recreate: bool = False


class IngestResponse(BaseModel):
    """Schema for repository ingestion response sent back to caller."""
    status: str = Field(..., description="Status of the ingestion job: COMPLETED or FAILED")
    repo_id: str = Field(..., description="UUID of the processed repository")
    total_files_loaded: int = Field(default=0, description="Count of source files read from disk")
    chunks_indexed: int = Field(default=0, description="Total chunks vectorized and upserted into Qdrant")
    message: str = Field(default="Ingestion completed successfully", description="Execution summary or error message")


class QueryRequest(BaseModel):
    """Schema for a natural-language query against an indexed repository."""
    repo_id: str = Field(..., description="UUID of the repository to query")
    question: str = Field(..., min_length=3, max_length=1000, description="Natural-language question about the codebase")
    top_k: int = Field(default=5, ge=1, le=15, description="Number of top matching chunks to retrieve")


class SourceReference(BaseModel):
    """A single cited code location backing part of the generated answer."""
    file_path: str
    start_line: int
    end_line: int
    layer: str
    score: float


class QueryResponse(BaseModel):
    """Schema for the RAG query response returned to the caller."""
    answer: str
    sources: List[SourceReference]
    repo_id: str