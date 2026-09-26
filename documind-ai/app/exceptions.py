class DocumindAIException(Exception):
    """Base exception for all DocuMind AI service errors."""
    pass


class EmbeddingServiceUnavailableError(DocumindAIException):
    """Raised when the Ollama embedding service cannot be reached."""
    pass


class GenerationServiceUnavailableError(DocumindAIException):
    """Raised when the Ollama generation (chat) model cannot be reached."""
    pass


class VectorStoreUnavailableError(DocumindAIException):
    """Raised when Qdrant cannot be reached or a Qdrant operation fails."""
    pass


class NoValidFilesError(DocumindAIException):
    """Raised when a repository contains no files matching the allowed extensions."""
    pass