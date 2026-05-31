# arXiv-paper-summariser

V16 upgrades the project from text-only paper summarisation into a multimodal research-paper understanding platform.
The goal is to deeply understand every modality commonly embedded in papers and supplementary material.

## V16 multimodal capabilities

- **Figure understanding** combines captions, OCR text, and detected visual entities to explain scientific figures.
- **Chart reasoning** consumes extracted chart series and axis metadata to produce trend, range, and comparative observations.
- **Equation interpretation** converts LaTeX, MathML, OCR text, or equation metadata into variable/operator inventories and natural-language reasoning steps.
- **Architecture diagram parsing** transforms system diagrams into components, directed edges, and data/control-flow explanations.
- **Table extraction** normalizes headers, rows, and cell-level facts for downstream summarisation.
- **Video understanding** uses transcripts, frame annotations, and temporal events from supplementary videos.
- **OCR pipelines** provide shared text recognition, cleanup, and structural token extraction for all visual modalities.

## Generated V16 systems

The platform is intentionally modular so production extractors can be attached without changing orchestration code:

| System | Module | Purpose |
| --- | --- | --- |
| Multimodal parsers | `arxiv_paper_summariser.parsers` | Figures, charts, tables, and video supplements |
| OCR pipelines | `arxiv_paper_summariser.ocr` | Text recognition, normalization, token extraction |
| Equation reasoning workflows | `arxiv_paper_summariser.equations` | Symbolic expression interpretation |
| Diagram analysis systems | `arxiv_paper_summariser.diagrams` | Architecture graph parsing and flow analysis |
| V16 orchestration | `arxiv_paper_summariser.platform_v16` | Modality routing and multimodal Markdown summaries |

## Quick start

```python
from arxiv_paper_summariser import build_v16_platform
from arxiv_paper_summariser.modalities import Modality, PaperAsset

platform = build_v16_platform()
assets = [
    PaperAsset(
        asset_id="eq-1",
        modality=Modality.EQUATION,
        source="paper.pdf",
        metadata={"latex": "y = mx + b"},
    )
]

print(platform.multimodal_summary(assets))
```

## Development

Run the test suite with:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
