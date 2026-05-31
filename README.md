# arXiv Paper Summariser V13

V13 upgrades the platform from static paper summaries to adaptive educational experiences. It turns a paper into level-aware explanations, prerequisite maps, tutoring interactions, quizzes, roadmaps, mini-courses, and concept dependency graphs.

## Learning modes

- `beginner`
- `undergraduate`
- `grad student`
- `researcher`

## V13 capabilities

- **Explain-by-level:** mode-specific explanations for each extracted concept.
- **Prerequisite generation:** foundational knowledge inferred per concept and deduplicated across the paper.
- **AI tutoring:** an adaptive tutoring engine that responds to confusion, mastery, and open-ended learner messages.
- **Interactive quizzes:** diagnostic questions tied to the concept graph and learner level.
- **Learning roadmaps:** dependency-first milestones with checkpoints and estimated study time.
- **Mini-courses:** modular lessons with objectives, explanations, quizzes, and a capstone.
- **Concept dependency graphs:** deterministic concept extraction and prerequisite-style graph edges.

## Quick start

```python
from arxiv_paper_summariser import Paper, V13Platform

paper = Paper.from_text(
    title="Graph Neural Networks for Probabilistic Molecule Discovery",
    abstract="We introduce a graph neural network architecture with Bayesian posterior estimation.",
    body="The method combines graph theory, machine learning, optimization, and probability.",
    keywords=("graph neural network", "posterior estimator"),
)

platform = V13Platform()
experience = platform.generate(paper, "undergraduate")
turn = platform.tutor(experience, "I'm confused about posterior estimation")

print(experience.roadmap.milestones)
print(turn.tutor_response)
```

## Architecture

- `ConceptGraphPipeline` extracts concepts, infers prerequisites, and builds dependency edges.
- `CurriculumGenerator` produces explanations, quizzes, roadmaps, mini-courses, and complete V13 experiences.
- `AdaptiveTutoringEngine` tracks learner mastery and adapts tutoring turns.
- `V13Platform` provides a high-level facade for applications and API handlers.

## Development

Run the test suite with:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
