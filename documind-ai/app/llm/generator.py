from typing import List, Dict

from app.llm.provider import get_generation_client
from app.exceptions import GenerationServiceUnavailableError


class AnswerGenerator:
    """
    Sends prepared chat messages to the generation LLM and returns
    the generated answer text.
    """

    def __init__(self):
        self.client = get_generation_client()

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Sends the given system/user messages to the LLM and returns
        the plain text of its response.
        """
        try:
            response = self.client.invoke(messages)
            return response.content
        except Exception as e:
            raise GenerationServiceUnavailableError(
                f"Failed to generate answer: {e}"
            )