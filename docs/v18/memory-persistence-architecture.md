# V18 Memory Persistence Architecture

## Purpose

Persistent memory lets the platform reason beyond a single prompt, session, paper, or project. V18 treats memory as a governed scientific asset with provenance, confidence, retention, conflict resolution, and auditability.

## Memory layers

| Layer | Scope | Examples | Storage pattern |
| --- | --- | --- | --- |
| Working memory | Active task context | current paper, plan, extracted claims, open questions | short-lived cache and task checkpoint store |
| Episodic memory | What happened | agent actions, tool calls, decisions, failures, user feedback | append-only event log |
| Semantic memory | What is known | concepts, claims, summaries, mechanisms, domain maps | vector index, graph database, document store |
| Procedural memory | How work is done | workflows, prompts, evaluation rubrics, tool recipes | versioned registry |
| Strategic memory | Why work matters | missions, hypotheses, roadmaps, portfolio decisions | strategic ledger and planning graph |

## Canonical memory object

Every persistent memory entry should use a common envelope:

```json
{
  "memory_id": "mem_01HYPOTHESISMAP",
  "memory_type": "semantic_claim",
  "created_at": "2026-05-28T00:00:00Z",
  "updated_at": "2026-05-28T00:00:00Z",
  "source": {
    "kind": "paper",
    "source_id": "arxiv:0000.00000",
    "url": "https://arxiv.org/abs/0000.00000",
    "accessed_at": "2026-05-28T00:00:00Z"
  },
  "content": {
    "claim": "A method improves summarisation faithfulness on a specific benchmark.",
    "domain": ["natural-language-processing", "scientific-summarisation"],
    "entities": ["method", "benchmark", "metric"]
  },
  "confidence": {
    "score": 0.74,
    "rationale": "Claim is directly supported by extracted results but has limited replication evidence.",
    "uncertainty_factors": ["single benchmark", "no independent reproduction"]
  },
  "provenance": {
    "agent_id": "evidence-extractor-v18",
    "model_version": "tracked-at-runtime",
    "workflow_id": "wf_claim_extraction_v18",
    "parent_memory_ids": []
  },
  "governance": {
    "risk_tier": "low",
    "review_state": "auto_accepted",
    "retention_policy": "retain_until_superseded"
  }
}
```

## Memory stores

### Event log

Stores all task, agent, and memory events as append-only records.

- Enables replay, audit, debugging, and rollback.
- Records task start, checkpoint, tool call, critique, decision, failure, completion, and memory commit events.
- Provides the source of truth for episodic memory.

### Vector index

Stores dense representations for retrieval and similarity search.

- Indexes abstracts, paper sections, claims, summaries, hypotheses, plans, and procedures.
- Supports hybrid retrieval with metadata filters for domain, date, confidence, risk, and source type.
- Uses embedding version tags so indexes can be rebuilt safely.

### Scientific graph

Stores typed entities and relationships.

- Supports reasoning over citations, claims, methods, datasets, mechanisms, contradictions, and transfer opportunities.
- Records relationship confidence and provenance.
- Enables multi-hop discovery such as “methods that improved robustness in chemistry and may transfer to biomedical summarisation.”

### Document store

Stores full text, extracted artifacts, generated reports, protocols, and snapshots.

- Keeps immutable source snapshots when licensing permits.
- Stores generated scientific outputs with references to graph nodes and memory IDs.
- Supports redaction, retention, and archival policies.

### Procedural registry

Stores versioned workflows, prompts, rubrics, tools, and agent policies.

- Requires benchmark evidence before promotion.
- Supports staged rollout, rollback, and deprecation.
- Links procedure versions to outcomes and telemetry.

## Memory consolidation

Memory consolidation converts raw traces into durable knowledge.

1. **Collect:** gather task traces, outputs, feedback, citations, and critique results.
2. **Filter:** remove low-value, duplicate, stale, or unsafe content.
3. **Extract:** identify claims, lessons, reusable procedures, unresolved questions, and strategic implications.
4. **Validate:** check provenance, contradiction status, confidence, and policy constraints.
5. **Commit:** write memory events to the event log and update graph/vector/document stores.
6. **Rehearse:** periodically retrieve and test important memories against new evidence.
7. **Retire:** archive superseded memories while preserving lineage.

## Retrieval strategy

V18 should use multi-memory retrieval rather than plain similarity search.

```text
retrieval_context =
  semantic_matches(query, domain_filters)
  + graph_neighborhood(seed_entities, hops=2)
  + episodic_precedents(task_type, failure_modes)
  + procedural_recipes(workflow_type, quality_score)
  + strategic_constraints(mission_id, portfolio_state)
```

### Retrieval controls

- Prefer high-confidence, recent, and reviewed memories.
- Include known contradictions instead of hiding them.
- Return provenance and confidence with each memory.
- Cap memory by task relevance, not only recency.
- Isolate sensitive or high-risk memories behind policy gates.

## Conflict resolution

Scientific memory must support disagreement.

- **Contradiction edges:** link claims that conflict instead of overwriting either claim.
- **Confidence recalibration:** update confidence when replication, retraction, or stronger evidence appears.
- **Version lineage:** preserve old summaries and show why they were superseded.
- **Review routing:** send unresolved high-impact conflicts to critique agents and human reviewers.
- **Portfolio impact:** notify active programs when a key assumption changes.

## Retention policies

| Memory type | Default retention | Retirement trigger |
| --- | --- | --- |
| Raw task traces | 90–365 days depending on sensitivity | summarized into durable memories or expired by policy |
| Evidence packages | retain while source is relevant and permitted | license removal, retraction, deduplication |
| Semantic claims | retain until superseded | contradiction resolved or confidence falls below threshold |
| Procedures | retain all promoted versions | deprecation after safer or better benchmarked replacement |
| Strategic plans | retain through program lifecycle plus archive period | mission closure, portfolio reset, policy requirement |

## Privacy, safety, and compliance

- Store only permitted source content and respect license constraints.
- Separate user-private notes from shared scientific memory.
- Apply access controls by project, domain, source license, and risk tier.
- Audit every memory mutation with agent identity and workflow version.
- Keep rollback pointers for all generated memory updates.
