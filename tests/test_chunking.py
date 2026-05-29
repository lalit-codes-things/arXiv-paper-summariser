from arxiv_copilot.chunking import ChunkingConfig, PaperChunker


def test_chunker_preserves_section_titles_and_limits_size():
    text = "\n\n".join(
        [
            "Abstract\n" + "overview " * 80,
            "Introduction\n" + "intro " * 400,
            "Method\n" + "method " * 400,
            "Conclusion\n" + "done " * 120,
        ]
    )
    chunker = PaperChunker(ChunkingConfig(max_tokens=220, overlap_tokens=10, chars_per_token=4))

    chunks = chunker.chunk(text)

    assert len(chunks) > 1
    assert chunks[0].section_title is not None
    assert all(chunk.token_estimate <= 260 for chunk in chunks)
    assert [chunk.index for chunk in chunks] == list(range(len(chunks)))
