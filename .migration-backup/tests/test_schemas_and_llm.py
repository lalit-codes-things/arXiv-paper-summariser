from arxiv_copilot.chunking import ChunkingConfig, PaperChunker
from arxiv_copilot.llm import LLMClient, SummarizationEngine
from arxiv_copilot.schemas import StructuredSummary


class CountingLLM(LLMClient):
    def __init__(self):
        self.prompts = []

    def complete_json(self, prompt):
        self.prompts.append(prompt)
        return {
            "tl_dr": "short",
            "eli5": "simple",
            "technical_summary": "technical",
            "methodology": ["method"],
            "datasets": [],
            "metrics": [],
            "contributions": ["contribution"],
            "limitations": [],
            "future_work": [],
            "flashcards": [{"question": "q", "answer": "a", "kind": "qa", "source_section": None}],
            "suggested_reading": [],
        }


def test_structured_summary_round_trip():
    summary = StructuredSummary.from_dict(
        {
            "tl_dr": "tl",
            "eli5": "e",
            "technical_summary": "t",
            "flashcards": [{"question": "q", "answer": "a", "kind": "concept"}],
            "suggested_reading": [{"title": "paper", "reason": "related"}],
        }
    )

    assert summary.to_dict()["flashcards"][0]["kind"] == "concept"
    assert summary.to_dict()["suggested_reading"][0]["title"] == "paper"


def test_summarization_engine_merges_long_papers():
    llm = CountingLLM()
    engine = SummarizationEngine(llm=llm, chunker=PaperChunker(ChunkingConfig(max_tokens=80, overlap_tokens=5)))

    summary = engine.summarize(title="Paper", abstract="Abstract", text="Introduction\n" + "token " * 600)

    assert summary.tl_dr == "short"
    assert len(llm.prompts) >= 2
    assert "merging chunk-level" in llm.prompts[-1]
