import pytest

from arxiv_copilot.citations import extract_citations
from arxiv_copilot.utils.retry import RetryConfig, retry


def test_extract_citations_from_references_section():
    text = "Body\n\nReferences\n[1] Smith, J. A useful paper. Journal. 2020.\n[2] Doe, J. Another paper. 2021."

    citations = extract_citations(text)

    assert len(citations) == 2
    assert citations[0].year == "2020"
    assert "Smith" in citations[0].authors[0]


def test_retry_eventually_succeeds(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("not yet")
        return "ok"

    assert retry(flaky, RetryConfig(attempts=3, initial_delay=0)) == "ok"


def test_retry_reraises_last_error(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)

    with pytest.raises(ValueError):
        retry(lambda: (_ for _ in ()).throw(ValueError("boom")), RetryConfig(attempts=2, initial_delay=0))
