# V14 Citation Intelligence Tools

## Purpose

Citation intelligence tools help authors ground claims, write related work, detect overlap risk, and evaluate novelty against existing literature.

## Tool Suite

| Tool | Purpose | Output |
| --- | --- | --- |
| Citation suggester | Finds papers that should support or contextualize claims. | Ranked candidate citations with rationale. |
| Related-work writer | Clusters citations into themes and drafts section prose. | Outline, paragraph drafts, and citation map. |
| Claim support checker | Verifies that factual claims have evidence. | Unsupported-claim report. |
| Plagiarism checker | Detects textual overlap and paraphrase risk. | Passage-level overlap report and rewrite guidance. |
| Novelty analyzer | Compares contributions to prior work. | Novelty matrix and risk assessment. |
| Bibliography cleaner | Normalizes and validates references. | Clean BibTeX and metadata warnings. |

## Citation Suggestion Flow

1. Extract claims from introduction, background, methods, and related work.
2. Classify claims as factual, comparative, methodological, historical, or novelty claims.
3. Search known bibliography and external literature indexes.
4. Rank candidates by relevance, authority, recency, and diversity.
5. Present suggestions with why each citation is relevant.
6. Let the author accept, reject, or request alternatives.

## Related Work Generation

The related-work writer creates a section from citation clusters rather than a flat list of papers.

**Cluster dimensions**

- Problem setting.
- Method family.
- Dataset or benchmark.
- Evaluation metric.
- Historical lineage.
- Competing approach.
- Limitation addressed by the current paper.

**Generated outputs**

- Theme outline.
- Paragraph-level citation plan.
- Draft prose with placeholders for author verification.
- Contrast statements explaining how the current work differs.

## Plagiarism Checks

Plagiarism checks operate at passage, paragraph, and section levels.

**Risk categories**

- Exact overlap.
- Near paraphrase.
- Missing quotation.
- Missing citation.
- Self-plagiarism risk.
- Template boilerplate that should be excluded from concern.

**Recommended actions**

- Rewrite with original framing.
- Add a citation.
- Quote and cite when exact wording is necessary.
- Move duplicated methodological details to an appendix when appropriate.

## Novelty Analysis

Novelty analysis compares the paper's claimed contributions against cited and discovered literature.

**Novelty matrix columns**

- Current paper claim.
- Closest prior work.
- Similarity explanation.
- Difference explanation.
- Evidence required.
- Novelty confidence.
- Risk level.

## Integrity Rules

- Never invent citations.
- Mark citation metadata as incomplete when uncertain.
- Distinguish user-provided references from discovered suggestions.
- Require author confirmation before inserting citations into final prose.
- Explain why a novelty claim may be too broad or unsupported.
