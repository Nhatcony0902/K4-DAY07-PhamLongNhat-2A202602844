from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    NO_CONTEXT = "(không tìm thấy tài liệu liên quan)"

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def _build_prompt(self, question: str, context: str) -> str:
        return (
            "Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu được cung cấp.\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n\n"
            "Chỉ trả lời dựa trên ngữ cảnh ở trên. "
            "Nếu ngữ cảnh không đủ thông tin, hãy nói rõ điều đó."
        )

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        context = "\n\n".join(result["content"] for result in results) or self.NO_CONTEXT
        return self.llm_fn(self._build_prompt(question, context))
