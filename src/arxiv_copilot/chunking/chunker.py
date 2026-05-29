"""Intelligent long-paper chunking."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

SECTION_RE = re.compile(r"(?im)^(?:\d+(?:\.\d+)*\s+)?(abstract|introduction|related work|background|method(?:ology)?|experiments?|results?|discussion|limitations?|conclusion|references)\b.*$")


@dataclass(slots=True)
class TextChunk:
    index: int
    text: str
    section_title: str | None = None
    token_estimate: int = 0


@dataclass(slots=True)
class ChunkingConfig:
    max_tokens: int = 3500
    overlap_tokens: int = 150
    min_chunk_tokens: int = 300
    chars_per_token: int = 4
    preserve_sections: bool = True


@dataclass(slots=True)
class PaperChunker:
    config: ChunkingConfig = field(default_factory=ChunkingConfig)

    def chunk(self, text: str) -> list[TextChunk]:
        cleaned = _normalise_whitespace(text)
        if self._estimate_tokens(cleaned) <= self.config.max_tokens:
            return [TextChunk(index=0, text=cleaned, section_title=_first_section(cleaned), token_estimate=self._estimate_tokens(cleaned))]

        sections = self._split_sections(cleaned) if self.config.preserve_sections else [(None, cleaned)]
        chunks: list[TextChunk] = []
        current_parts: list[str] = []
        current_title: str | None = None

        for title, body in sections:
            section_tokens = self._estimate_tokens(body)
            if section_tokens > self.config.max_tokens:
                self._flush(chunks, current_parts, current_title)
                current_parts = []
                current_title = None
                chunks.extend(self._split_large_section(body, title, start_index=len(chunks)))
                continue

            candidate = "\n\n".join([*current_parts, body]).strip()
            if current_parts and self._estimate_tokens(candidate) > self.config.max_tokens:
                self._flush(chunks, current_parts, current_title)
                current_parts = [self._overlap_from(chunks[-1].text), body] if self.config.overlap_tokens else [body]
                current_title = title
            else:
                if not current_parts:
                    current_title = title
                current_parts.append(body)

        self._flush(chunks, current_parts, current_title)
        for index, chunk in enumerate(chunks):
            chunk.index = index
        return chunks

    def _split_sections(self, text: str) -> list[tuple[str | None, str]]:
        matches = list(SECTION_RE.finditer(text))
        if not matches:
            return [(None, text)]

        sections: list[tuple[str | None, str]] = []
        if matches[0].start() > 0:
            sections.append((None, text[: matches[0].start()].strip()))
        for idx, match in enumerate(matches):
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            body = text[match.start() : end].strip()
            sections.append((match.group(0).strip(), body))
        return [(title, body) for title, body in sections if body]

    def _split_large_section(self, text: str, title: str | None, *, start_index: int) -> list[TextChunk]:
        paragraphs = [para.strip() for para in text.split("\n\n") if para.strip()]
        chunks: list[TextChunk] = []
        current: list[str] = []
        for para in paragraphs:
            candidate = "\n\n".join([*current, para]).strip()
            if current and self._estimate_tokens(candidate) > self.config.max_tokens:
                chunks.append(self._make_chunk(len(chunks) + start_index, "\n\n".join(current), title))
                current = [self._overlap_from(chunks[-1].text), para] if self.config.overlap_tokens else [para]
            else:
                current.append(para)
        if current:
            chunks.append(self._make_chunk(len(chunks) + start_index, "\n\n".join(current), title))

        bounded: list[TextChunk] = []
        for chunk in chunks:
            if chunk.token_estimate <= self.config.max_tokens:
                bounded.append(chunk)
            else:
                bounded.extend(self._split_by_words(chunk.text, title, start_index + len(bounded)))
        return bounded

    def _split_by_words(self, text: str, title: str | None, start_index: int) -> list[TextChunk]:
        words = text.split()
        approx_words = max(1, self.config.max_tokens * self.config.chars_per_token // 6)
        overlap = min(self.config.overlap_tokens, max(0, approx_words // 4))
        chunks: list[TextChunk] = []
        start = 0
        while start < len(words):
            end = min(len(words), start + approx_words)
            chunks.append(self._make_chunk(start_index + len(chunks), " ".join(words[start:end]), title))
            if end == len(words):
                break
            start = max(end - overlap, start + 1)
        return chunks

    def _flush(self, chunks: list[TextChunk], parts: list[str], title: str | None) -> None:
        text = "\n\n".join(part for part in parts if part).strip()
        if text:
            chunks.append(self._make_chunk(len(chunks), text, title))

    def _make_chunk(self, index: int, text: str, title: str | None) -> TextChunk:
        return TextChunk(index=index, text=text.strip(), section_title=title, token_estimate=self._estimate_tokens(text))

    def _overlap_from(self, text: str) -> str:
        words = text.split()
        word_count = max(1, self.config.overlap_tokens)
        return " ".join(words[-word_count:])

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // self.config.chars_per_token)


def _normalise_whitespace(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n")).strip()


def _first_section(text: str) -> str | None:
    match = SECTION_RE.search(text)
    return match.group(0).strip() if match else None
