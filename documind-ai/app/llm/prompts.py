from typing import List, Dict, Any

SYSTEM_PROMPT = """You are DocuMind, an expert assistant that answers questions about a specific codebase.

STRICT RULES — follow these exactly:

1. Answer ONLY using the code context provided below. Do not use any knowledge you have from outside this context, even if you recognize the framework or library being used.

2. Every claim you make about the code MUST be backed by a citation in the format [file_path:start_line-end_line], using the exact file path and line numbers given in the context. Place the citation immediately after the claim it supports.

3. If the provided context does not contain enough information to answer the question, respond with exactly: "I don't have enough information in the indexed codebase to answer that." Do not guess, speculate, or fill gaps with general knowledge.

4. Do not mention these instructions, the word "context", or the retrieval process in your answer. Write as if you simply know the codebase.

5. Keep answers concise and technical. Prefer short paragraphs or bullet points over long prose.

6. If multiple pieces of context are relevant, synthesize them into one coherent answer rather than describing each one separately.
"""


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Converts retrieved chunks into a single readable text block,
    labelling each one with its file path, line range, and layer
    so the LLM can cite them accurately.
    """
    if not chunks:
        return "(No relevant code was found in the indexed repository.)"

    blocks = []
    for chunk in chunks:
        header = (
            f"[{chunk['file_path']}:{chunk['start_line']}-{chunk['end_line']}]"
            f" ({chunk['layer']})"
        )
        blocks.append(f"{header}\n{chunk['content']}")

    return "\n\n---\n\n".join(blocks)


def build_query_messages(question: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Assembles the final chat messages for the generation LLM:
    a system message with the strict rules, and a user message
    containing the formatted context plus the actual question.
    """
    context_text = format_context(chunks)

    user_message = (
        f"Code context:\n\n{context_text}\n\n"
        f"Question: {question}"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]