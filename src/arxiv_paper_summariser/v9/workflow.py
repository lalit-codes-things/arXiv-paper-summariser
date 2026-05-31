"""V9 orchestration: paper text to executable implementation workflow."""

from __future__ import annotations

from pathlib import Path

from .architecture import ArchitectureParser
from .codegen import CodeGenerationEngine
from .dependencies import DependencyDetector
from .experiments import ExperimentGenerator
from .extraction import PseudoCodeExtractor
from .models import GeneratedFile, V9WorkflowResult
from .planning import ImplementationPlanner
from .reproducibility import ReproducibilityAnalyzer
from .text import normalize_whitespace


class V9Workflow:
    """Coordinate all V9 engines and optionally materialize a starter repo."""

    def __init__(self) -> None:
        self.pseudo_code_extractor = PseudoCodeExtractor()
        self.architecture_parser = ArchitectureParser()
        self.dependency_detector = DependencyDetector()
        self.implementation_planner = ImplementationPlanner()
        self.experiment_generator = ExperimentGenerator()
        self.reproducibility_analyzer = ReproducibilityAnalyzer()
        self.code_generation_engine = CodeGenerationEngine()

    def run(self, paper_text: str) -> V9WorkflowResult:
        """Generate the full V9 output bundle from raw paper text."""

        normalized = normalize_whitespace(paper_text)
        pseudo_code = self.pseudo_code_extractor.extract(normalized)
        architecture = self.architecture_parser.parse(normalized, pseudo_code)
        dependencies = self.dependency_detector.detect(normalized)
        implementation_plan = self.implementation_planner.plan(pseudo_code, architecture, dependencies)
        experiments = self.experiment_generator.generate(dependencies)
        reproducibility = self.reproducibility_analyzer.analyze(normalized, dependencies)
        checklist = self.implementation_planner.checklist(implementation_plan)
        experiment_yaml = self.experiment_generator.to_yaml(experiments)
        training_pipeline = self._training_pipeline()
        starter_repo = self.code_generation_engine.generate(
            architecture=architecture,
            pseudo_code=pseudo_code,
            dependencies=dependencies,
            experiment_yaml=experiment_yaml,
            checklist_markdown=checklist,
        )
        starter_repo = self._replace_reproducibility_doc(starter_repo, ReproducibilityAnalyzer.workflow_markdown(reproducibility))
        return V9WorkflowResult(
            pseudo_code=pseudo_code,
            architecture=architecture,
            dependencies=dependencies,
            implementation_plan=implementation_plan,
            experiments=experiments,
            reproducibility=reproducibility,
            starter_repo=starter_repo,
            checklist_markdown=checklist,
            experiment_config_yaml=experiment_yaml,
            training_pipeline=training_pipeline,
        )

    def write_starter_repo(self, paper_text: str, output_dir: str | Path) -> V9WorkflowResult:
        """Run V9 and write generated starter-repository files to disk."""

        result = self.run(paper_text)
        root = Path(output_dir)
        for generated in result.starter_repo:
            destination = root / generated.path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(generated.content, encoding="utf-8")
        return result

    @staticmethod
    def _training_pipeline() -> str:
        return "\n".join(
            [
                "load_config -> set_seed -> build_dataloader -> build_model",
                "build_optimizer -> train_epochs -> evaluate_metrics -> save_artifacts",
                "run_seed_sweep -> run_ablations -> emit_reproducibility_report",
            ]
        )

    @staticmethod
    def _replace_reproducibility_doc(files: list[GeneratedFile], content: str) -> list[GeneratedFile]:
        return [
            GeneratedFile(file.path, content) if file.path == "docs/reproducibility_workflow.md" else file
            for file in files
        ]
