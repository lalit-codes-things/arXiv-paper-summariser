import unittest

from arxiv_paper_summariser import build_v16_platform
from arxiv_paper_summariser.modalities import Modality, PaperAsset


class V16PlatformTest(unittest.TestCase):
    def test_routes_all_requested_modalities(self):
        platform = build_v16_platform()
        assets = [
            PaperAsset("fig-1", Modality.FIGURE, "paper.pdf", caption="A microscopy example.", metadata={"entities": ["cell"]}),
            PaperAsset("chart-1", Modality.CHART, "paper.pdf", metadata={"chart": {"series": [{"name": "accuracy", "values": [0.7, 0.8, 0.9]}]}}),
            PaperAsset("eq-1", Modality.EQUATION, "paper.pdf", metadata={"latex": "y = mx + b"}),
            PaperAsset("arch-1", Modality.ARCHITECTURE_DIAGRAM, "paper.pdf", metadata={"graph": {"components": ["encoder", "decoder"], "edges": [("encoder", "decoder", "latent")]}}),
            PaperAsset("table-1", Modality.TABLE, "paper.pdf", metadata={"table": {"headers": ["model", "score"], "rows": [["V16", 0.95]]}}),
            PaperAsset("video-1", Modality.VIDEO, "supp.mp4", metadata={"transcript": "The model segments objects.", "frames": ["input frame", "mask frame"], "events": ["segmentation appears"]}),
        ]

        results = platform.understand_paper(assets)

        self.assertEqual([result.modality for result in results], [asset.modality for asset in assets])
        self.assertTrue(all(result.summary for result in results))
        self.assertIn("V16 multimodal", platform.multimodal_summary(assets))

    def test_ocr_fallback_extracts_structural_tokens(self):
        platform = build_v16_platform()
        asset = PaperAsset("ocr-1", Modality.OCR, "paper.pdf", content="loss = x1 + 2")

        result = platform.understand_asset(asset)

        self.assertEqual(result.extracted["tokens"]["numbers"], ["2"])
        self.assertIn("=", result.extracted["tokens"]["operators"])


if __name__ == "__main__":
    unittest.main()
