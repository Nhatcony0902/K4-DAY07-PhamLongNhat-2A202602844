from __future__ import annotations

import math
import re

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])[ \n]+")


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sentences = [s.strip() for s in _SENTENCE_BOUNDARY.split(text) if s.strip()]
        size = self.max_sentences_per_chunk
        return [" ".join(sentences[i : i + size]) for i in range(0, len(sentences), size)]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _hard_split(self, current_text: str) -> list[str]:
        size = max(1, self.chunk_size)
        return [current_text[i : i + size] for i in range(0, len(current_text), size)]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return self._hard_split(current_text)

        separator, rest = remaining_separators[0], remaining_separators[1:]
        if separator == "":
            return self._hard_split(current_text)

        chunks: list[str] = []
        buffer = ""
        for part in current_text.split(separator):
            candidate = part if not buffer else buffer + separator + part
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunks.extend(self._split(buffer, rest))
            buffer = part
        if buffer:
            chunks.extend(self._split(buffer, rest))
        return [chunk for chunk in chunks if chunk]


_ATX_HEADING = re.compile(r"^(#{1,6})\s+(\S.*)$")
_NUMBERED_HEADING = re.compile(r"^(\d+(?:\.\d+)+\.?|\d+\.)\s+(\S.*)$")


class HeadingChunker:
    """
    Split text into one chunk per heading/section.

    Recognises two heading styles, because policy pages mix them:
        - Markdown ATX headings: "# ", "## ", ... "###### "
        - Numbered clauses:      "1. ", "1.1 ", "2.3.1. "

    A numbered clause sits one level below an ATX heading of the same depth,
    so "1." is treated as a child of the document's "# title".

    Text appearing before the first heading becomes its own chunk. Each chunk
    is prefixed with its parent headings ("Title > 1. Section") when
    include_parent_headings is True, so a retrieved chunk still says which
    clause it came from.
    """

    def __init__(self, include_parent_headings: bool = True) -> None:
        self.include_parent_headings = include_parent_headings

    def _heading(self, line: str) -> tuple[int, str] | None:
        atx = _ATX_HEADING.match(line)
        if atx:
            return len(atx.group(1)), atx.group(2).strip()
        numbered = _NUMBERED_HEADING.match(line)
        if numbered:
            return numbered.group(1).rstrip(".").count(".") + 2, line.strip()
        return None

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections: list[tuple[int, str, list[str]]] = []
        preamble: list[str] = []
        for line in text.splitlines():
            heading = self._heading(line)
            if heading is None:
                (sections[-1][2] if sections else preamble).append(line)
            else:
                sections.append((heading[0], heading[1], []))

        chunks: list[str] = []
        if preamble and "".join(preamble).strip():
            chunks.append("\n".join(preamble).strip())

        trail: list[tuple[int, str]] = []
        for level, title, body in sections:
            trail = [item for item in trail if item[0] < level]
            trail.append((level, title))
            heading_line = " > ".join(t for _, t in trail) if self.include_parent_headings else title
            content = "\n".join(body).strip()
            chunks.append(f"{heading_line}\n\n{content}" if content else heading_line)
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    magnitude = math.sqrt(_dot(vec_a, vec_a)) * math.sqrt(_dot(vec_b, vec_b))
    if magnitude == 0:
        return 0.0
    return _dot(vec_a, vec_b) / magnitude


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0).chunk(text),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3).chunk(text),
            "recursive": RecursiveChunker(chunk_size=chunk_size).chunk(text),
        }
        return {
            name: {
                "count": len(chunks),
                "avg_length": sum(len(c) for c in chunks) // len(chunks) if chunks else 0,
                "chunks": chunks,
            }
            for name, chunks in strategies.items()
        }
