# V18 Platform Architecture

## Mission

V18 creates a persistent AI-native scientific ecosystem that continuously turns scientific signals into structured knowledge, research plans, experiments, and reusable agent capabilities. The platform is designed for autonomous discovery while preserving scientific rigor, provenance, and human-governed safety controls.

## Architectural objectives

1. **Discover continuously:** ingest papers, preprints, datasets, patents, grants, benchmarks, code repositories, and experiment outputs as live scientific signals.
2. **Remember persistently:** retain long-lived scientific context across projects, agents, users, domains, and reasoning sessions.
3. **Reason over horizons:** support immediate summarisation, weekly synthesis, quarterly research programs, and multi-year hypothesis tracking.
4. **Plan scientifically:** convert uncertain hypotheses into testable plans, protocols, simulations, evaluation criteria, and validation checkpoints.
5. **Improve safely:** let agents learn from outcomes through auditable reflection, benchmarked procedure updates, and policy-gated deployment.
6. **Synthesize across domains:** link concepts, mechanisms, methods, datasets, and contradictions across fields to expose non-obvious research opportunities.

## System layers

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         Human & API Interfaces                       │
│ dashboards · notebooks · chat · workflow APIs · review queues         │
├─────────────────────────────────────────────────────────────────────┤
│                       Scientific Orchestration Plane                  │
│ mission control · agent scheduler · policy gates · task graph runtime │
├─────────────────────────────────────────────────────────────────────┤
│                           Cognitive Agent Plane                       │
│ discovery · summarisation · synthesis · planning · critique agents    │
├─────────────────────────────────────────────────────────────────────┤
│                          Persistent Memory Plane                      │
│ working · episodic · semantic · procedural · strategic memories       │
├─────────────────────────────────────────────────────────────────────┤
│                        Knowledge & Evidence Plane                     │
│ scientific graph · vector index · claim store · provenance ledger     │
├─────────────────────────────────────────────────────────────────────┤
│                          Execution & Tool Plane                       │
│ search · retrieval · code · simulation · lab APIs · benchmark runners │
├─────────────────────────────────────────────────────────────────────┤
│                         Observability & Governance                    │
│ audit trails · safety policy · evaluations · drift and quality metrics│
└─────────────────────────────────────────────────────────────────────┘
```

## Core services

### 1. Signal ingestion service

The ingestion service converts external scientific signals into normalized evidence packages.

- **Connectors:** arXiv, PubMed, Crossref, Semantic Scholar, OpenAlex, patent indexes, clinical trial registries, dataset repositories, code hosts, and internal experiment stores.
- **Normalisation:** extracts metadata, abstracts, sections, figures, tables, citations, methods, datasets, metrics, limitations, and funding context.
- **Deduplication:** canonicalises works by DOI, arXiv ID, title similarity, author lists, and citation fingerprints.
- **Provenance:** records source URL, access timestamp, license, transformation steps, model versions, and confidence.

### 2. Scientific knowledge graph

The knowledge graph stores typed scientific objects and relationships.

- **Entities:** papers, authors, institutions, datasets, models, methods, tasks, hypotheses, claims, evidence, protocols, experiments, metrics, domains, and concepts.
- **Relationships:** supports, contradicts, extends, reproduces, uses dataset, evaluates metric, proposes mechanism, cites, improves, fails under, and transfers to domain.
- **Graph functions:** contradiction detection, lineage tracing, impact propagation, analogy discovery, causal mechanism mapping, and gap analysis.

### 3. Agent orchestration runtime

The orchestration runtime coordinates specialised agents as durable, inspectable workflows.

- **Mission controller:** receives strategic research goals and decomposes them into milestones, work packages, and agent task graphs.
- **Task scheduler:** assigns tasks by skill, domain, cost, latency, tool access, memory dependencies, and risk level.
- **State checkpoints:** persists task state, intermediate reasoning artifacts, citations, decisions, and open questions.
- **Policy gates:** routes sensitive or high-impact decisions to human review or stricter validation agents.

### 4. Persistent memory fabric

The memory fabric separates volatile reasoning context from durable scientific memory.

- **Working memory:** active context for a task or conversation.
- **Episodic memory:** chronological traces of agent actions, decisions, failures, and outcomes.
- **Semantic memory:** stable concepts, claims, summaries, and cross-domain mappings.
- **Procedural memory:** reusable workflows, prompts, tool recipes, analysis protocols, and benchmarked agent strategies.
- **Strategic memory:** long-horizon research goals, thesis maps, hypothesis ledgers, roadmaps, and portfolio decisions.

### 5. Scientific planning engine

The planning engine transforms discoveries into research programs.

- **Hypothesis generation:** uses gaps, contradictions, analogies, and mechanism maps to propose testable hypotheses.
- **Plan decomposition:** converts hypotheses into literature reviews, experiments, simulations, dataset searches, baselines, and success criteria.
- **Uncertainty modeling:** records assumptions, confidence, risk, expected value, and information gain.
- **Review loops:** schedules critique, replication analysis, ethics checks, and human approval when needed.

### 6. Self-improvement loop

Self-improvement is handled as a governed workflow, not as uncontrolled model mutation.

1. Observe agent performance, failures, latency, cost, evidence quality, and user feedback.
2. Reflect on root causes and propose procedure, prompt, tool, or routing changes.
3. Test proposed changes against regression benchmarks and scientific quality rubrics.
4. Require policy and human approval for high-impact changes.
5. Promote approved changes into procedural memory with versioned provenance.
6. Monitor post-deployment drift and rollback triggers.

## Data flow

1. **Ingest:** connectors collect scientific artifacts and create evidence packages.
2. **Parse:** extraction agents identify claims, methods, datasets, metrics, limitations, and citations.
3. **Index:** packages are embedded, linked into the graph, and recorded in provenance ledgers.
4. **Discover:** discovery agents monitor novelty, contradictions, anomalous results, and emerging clusters.
5. **Synthesize:** synthesis agents build cross-domain maps, literature briefs, and research opportunity reports.
6. **Plan:** planning agents create testable programs, workflows, and evaluation gates.
7. **Execute:** execution agents run retrieval, analysis, code, simulation, or external tool tasks.
8. **Evaluate:** critique agents score evidence, reproducibility, novelty, and uncertainty.
9. **Remember:** consolidation jobs update semantic, episodic, procedural, and strategic memories.

## Operating model

- **Human-in-the-loop by default:** autonomous systems can recommend and prepare work, but irreversible or high-risk actions require approval.
- **Evidence-first outputs:** every generated scientific assertion must include source references, confidence, and known limitations.
- **Resumability:** every long-running task can pause, resume, replay, or fork from checkpoints.
- **Portfolio awareness:** agent decisions consider global research priorities, not only local task success.
- **Continuous evaluation:** the platform measures factuality, citation fidelity, novelty, reproducibility, plan quality, cost, and safety compliance.
