import unittest

from arxiv_paper_summariser import EducationMode, Paper, V13Platform
from arxiv_paper_summariser.concept_graph import ConceptGraphPipeline
from arxiv_paper_summariser.curriculum import CurriculumGenerator


def sample_paper() -> Paper:
    return Paper.from_text(
        title="Graph Neural Networks for Probabilistic Molecule Discovery",
        abstract=(
            "We introduce a graph neural network architecture with Bayesian posterior "
            "estimation for molecule discovery benchmarks."
        ),
        body=(
            "The method combines graph theory, machine learning, optimization, and "
            "probability. An ablation study compares transformer embeddings and a "
            "posterior estimator."
        ),
        keywords=("graph neural network", "posterior estimator"),
    )


class V13PlatformTest(unittest.TestCase):
    def test_concept_graph_pipeline_generates_dependencies_and_prerequisites(self):
        graph = ConceptGraphPipeline(max_concepts=8).run(sample_paper())

        self.assertTrue(graph.concepts)
        self.assertTrue(graph.dependencies)
        self.assertTrue(any("machine learning" in concept.prerequisites for concept in graph.concepts))
        self.assertEqual(len(graph.ordered_concepts()), len(graph.concepts))

    def test_curriculum_generator_supports_all_modes(self):
        generator = CurriculumGenerator(ConceptGraphPipeline(max_concepts=6))

        for mode in EducationMode:
            with self.subTest(mode=mode):
                experience = generator.generate_experience(sample_paper(), mode)
                self.assertIs(experience.mode, mode)
                self.assertTrue(experience.explanations)
                self.assertTrue(experience.prerequisites)
                self.assertTrue(experience.roadmap.milestones)
                self.assertTrue(experience.mini_course.lessons)
                self.assertTrue(experience.diagnostic_quiz)

    def test_platform_tutor_adapts_to_confusion(self):
        platform = V13Platform(CurriculumGenerator(ConceptGraphPipeline(max_concepts=6)))
        experience = platform.generate(sample_paper(), "beginner")

        turn = platform.tutor(experience, "I am confused about the posterior estimator")

        self.assertLess(turn.confidence, 0.5)
        self.assertIsNotNone(turn.quiz)
        self.assertTrue(
            "slow down" in turn.tutor_response.lower() or "isolate" in turn.tutor_response.lower()
        )


if __name__ == "__main__":
    unittest.main()
