"""V16 multimodal platform orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field

from .diagrams import ArchitectureDiagramParser
from .equations import EquationReasoningWorkflow
from .modalities import Modality, PaperAsset, UnderstandingResult
from .ocr import OCRPipeline
from .parsers import ChartReasoningParser, FigureUnderstandingParser, TableExtractionParser, VideoUnderstandingParser


@dataclass
class V16PaperUnderstandingPlatform:
    """Routes paper assets through modality-specific parsers and reasoning workflows."""

    ocr: OCRPipeline = field(default_factory=OCRPipeline)

    def __post_init__(self) -> None:
        self.figure_parser = FigureUnderstandingParser(self.ocr)
        self.chart_parser = ChartReasoningParser(self.ocr)
        self.equation_workflow = EquationReasoningWorkflow(self.ocr)
        self.diagram_parser = ArchitectureDiagramParser(self.ocr)
        self.table_parser = TableExtractionParser(self.ocr)
        self.video_parser = VideoUnderstandingParser(self.ocr)

    def understand_asset(self, asset: PaperAsset) -> UnderstandingResult:
        """Understand one extracted paper asset."""

        routes = {
            Modality.FIGURE: self.figure_parser.parse,
            Modality.CHART: self.chart_parser.parse,
            Modality.EQUATION: self.equation_workflow.run,
            Modality.ARCHITECTURE_DIAGRAM: self.diagram_parser.parse,
            Modality.TABLE: self.table_parser.parse,
            Modality.VIDEO: self.video_parser.parse,
            Modality.OCR: self.ocr.run,
        }
        return routes[asset.modality](asset)

    def understand_paper(self, assets: list[PaperAsset]) -> list[UnderstandingResult]:
        """Understand every multimodal asset extracted from a paper."""

        return [self.understand_asset(asset) for asset in assets]

    def multimodal_summary(self, assets: list[PaperAsset]) -> str:
        """Create a Markdown summary across all parsed paper modalities."""

        results = self.understand_paper(assets)
        heading = "# V16 multimodal paper understanding summary"
        return "\n\n".join([heading, *(result.to_markdown() for result in results)])


def build_v16_platform() -> V16PaperUnderstandingPlatform:
    """Factory for the V16 platform with default OCR and parser wiring."""

    return V16PaperUnderstandingPlatform()
