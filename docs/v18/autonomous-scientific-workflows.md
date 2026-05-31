# V18 Autonomous Scientific Workflows

## Workflow design principles

- Every workflow starts from a scientific objective and ends with evidence, uncertainty, and next actions.
- Workflows are resumable, inspectable, and checkpointed.
- Autonomy is bounded by policy, risk tier, tool permissions, and review gates.
- Hypothesis generation, evidence extraction, critique, and planning are separated to reduce confirmation bias.
- Durable outputs are committed into memory only after provenance and quality checks.

## Workflow 1: continuous literature discovery

**Goal:** identify new papers, datasets, methods, or contradictions relevant to active missions.

1. Monitor configured sources for new scientific artifacts.
2. Deduplicate and normalize metadata.
3. Rank artifacts by mission relevance, novelty, citation graph position, and expected information gain.
4. Extract claims, methods, datasets, metrics, limitations, and open questions.
5. Compare extracted claims against the knowledge graph.
6. Flag novelty, contradictions, replications, and methodological shifts.
7. Generate a discovery brief with citations, confidence, and recommended follow-up tasks.
8. Commit validated claims and discovery events to memory.

**Outputs:** discovery brief, claim records, graph updates, follow-up work packages.

**Review gates:** citation fidelity, contradiction review, high-impact domain policy.

## Workflow 2: autonomous paper summarisation

**Goal:** produce faithful scientific summaries that are reusable in long-term research memory.

1. Retrieve paper metadata, full text when available, and related graph context.
2. Segment the paper into abstract, introduction, methods, results, discussion, limitations, and references.
3. Extract core contributions, experimental setup, datasets, metrics, and limitations.
4. Generate summaries at multiple levels: short brief, technical summary, method card, evidence card, and domain transfer note.
5. Critique factual alignment against extracted spans and references.
6. Link claims to graph entities and confidence scores.
7. Store summary artifacts and semantic memories.

**Outputs:** layered summaries, evidence cards, method cards, limitation records, graph links.

**Quality metrics:** citation precision, unsupported-claim rate, limitation coverage, method completeness, contradiction awareness.

## Workflow 3: cross-domain synthesis

**Goal:** discover transferable mechanisms and research opportunities across fields.

1. Select seed concepts, methods, or hypotheses from a mission.
2. Retrieve graph neighborhoods across multiple domains.
3. Identify analogies by mechanism, mathematical structure, dataset properties, or evaluation pattern.
4. Detect contradictions and negative-transfer risks.
5. Generate synthesis maps with candidate transfers and confidence.
6. Ask critique agents to challenge feasibility and evidence strength.
7. Convert high-value opportunities into hypothesis ledger entries.

**Outputs:** cross-domain synthesis report, analogy map, mechanism map, contradiction ledger, candidate hypotheses.

**Review gates:** domain expert review for high-impact or speculative transfers.

## Workflow 4: hypothesis generation and ranking

**Goal:** transform gaps, contradictions, and analogies into testable scientific hypotheses.

1. Collect gaps, anomalies, contradictions, and underexplored links from active missions.
2. Generate candidate hypotheses with scope, mechanism, evidence basis, and falsification conditions.
3. Score hypotheses by novelty, plausibility, expected information gain, feasibility, risk, and strategic alignment.
4. Cluster related hypotheses into research programs.
5. Create validation plans for top candidates.
6. Record rejected hypotheses with reasons to avoid repeated rediscovery.

**Outputs:** ranked hypothesis ledger, rationale, falsification criteria, validation work packages.

**Scoring dimensions:** novelty, evidence support, testability, feasibility, impact, risk, resource cost, portfolio fit.

## Workflow 5: scientific planning and experiment design

**Goal:** convert a hypothesis into an executable research plan.

1. Define the research question, assumptions, success criteria, and stop conditions.
2. Retrieve relevant prior work, datasets, baselines, metrics, protocols, and known failure modes.
3. Decompose the plan into literature review, data preparation, modeling, simulation, analysis, and validation tasks.
4. Estimate resource needs, timeline, expected information gain, and risks.
5. Generate experiment protocols, benchmark plans, and analysis scripts when appropriate.
6. Route high-risk plans through policy and human review.
7. Track execution results and update the hypothesis ledger.

**Outputs:** research plan, experiment protocol, task graph, evaluation rubric, review checklist.

**Review gates:** ethics, safety, reproducibility, statistical validity, data licensing, and human approval where needed.

## Workflow 6: autonomous critique and replication analysis

**Goal:** reduce false confidence and identify weaknesses before plans or summaries become durable memory.

1. Select target output: summary, claim, hypothesis, plan, or experiment result.
2. Retrieve source evidence and related contradictory evidence.
3. Check citation fidelity, assumptions, statistical validity, reproducibility, and limitation coverage.
4. Produce a critique with severity, recommended fixes, and confidence adjustments.
5. Require remediation for severe issues.
6. Commit critique outcomes to episodic and semantic memory.

**Outputs:** critique report, confidence updates, contradiction links, remediation tasks.

## Workflow 7: self-improvement cycle

**Goal:** improve agents and workflows without compromising safety or scientific rigor.

1. Monitor telemetry for failures, low-quality outputs, high cost, repeated critiques, and user feedback.
2. Identify root causes such as weak retrieval, missing memory, poor prompts, insufficient critique, or tool limits.
3. Propose procedure changes with expected benefits and rollback plans.
4. Run benchmark and regression suites.
5. Route proposed changes through governance gates.
6. Promote approved changes into procedural memory.
7. Monitor live performance and rollback if quality regresses.

**Outputs:** improvement proposal, benchmark report, promoted procedure version, rollout telemetry.

## Workflow 8: long-term research program management

**Goal:** sustain reasoning across months or years.

1. Maintain mission goals, active hypotheses, milestones, assumptions, and risks.
2. Periodically refresh evidence from literature and experiment results.
3. Re-score hypotheses and plans as new evidence appears.
4. Summarize progress, blocked paths, strategic pivots, and portfolio tradeoffs.
5. Archive completed or invalidated work while preserving provenance.
6. Generate next-period research plans.

**Outputs:** program status report, strategic memory updates, roadmap revisions, closed-loop lessons.
