# V14 Reviewer Simulation System

## Objectives

The reviewer simulation system helps authors anticipate peer-review outcomes by generating independent, venue-aware critiques. It is not a substitute for real peer review; it is a diagnostic system for improving clarity, evidence, novelty, and compliance before submission.

## Reviewer Personas

V14 uses configurable reviewer personas so critiques cover multiple perspectives.

| Persona | Focus | Typical flags |
| --- | --- | --- |
| Methodologist | Technical correctness and experimental design | Weak baselines, missing ablations, confounded evaluation. |
| Domain expert | Fit with field literature and novelty | Overclaimed novelty, missing related work, unclear contribution. |
| Skeptical reviewer | Failure modes and reproducibility | Insufficient details, fragile assumptions, missing artifacts. |
| Writing reviewer | Communication and structure | Unclear abstract, weak motivation, confusing figures. |
| Venue-area reviewer | Conference fit and criteria | Scope mismatch, anonymity issues, page-limit problems. |

## Simulation Pipeline

1. **Manuscript ingestion:** Parse sections, figures, tables, equations, references, and appendices.
2. **Venue rubric loading:** Apply review criteria, score scales, ethical requirements, and formatting constraints.
3. **Evidence mapping:** Link claims to experiments, citations, figures, or appendices.
4. **Independent review generation:** Generate one review per persona without sharing intermediate judgments.
5. **Score calibration:** Normalize scores against the venue scale and mark confidence levels.
6. **Meta-review synthesis:** Combine reviews into accept-risk, borderline-risk, and reject-risk factors.
7. **Revision planning:** Convert critiques into prioritized actions.

## Scorecard

Each simulated reviewer returns:

- Summary of the paper.
- Strengths.
- Weaknesses.
- Questions for authors.
- Required revisions.
- Optional improvements.
- Confidence score.
- Overall recommendation.
- Dimension scores for novelty, significance, soundness, clarity, reproducibility, ethics, and venue fit.

## Rebuttal Generation

The rebuttal engine transforms reviews into a response matrix.

| Input | Generated output |
| --- | --- |
| Reviewer criticism | Atomic concern with severity and topic. |
| Manuscript evidence | Suggested response with section, figure, table, or appendix references. |
| Missing evidence | Revision TODO or suggested experiment. |
| Misunderstanding | Clarification response and manuscript edit recommendation. |
| Valid criticism | Agreement response and concrete fix. |

## Safeguards

- Simulated reviews must label uncertainty when a judgment depends on missing context.
- The system must not fabricate reviewer identities, acceptance probabilities, or citations.
- Rebuttals must remain professional, concise, and evidence-based.
- The system should recommend additional experiments rather than inventing results.
