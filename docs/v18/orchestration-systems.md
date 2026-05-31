# V18 Advanced Orchestration Systems

## Purpose

The orchestration layer turns broad scientific missions into reliable multi-agent programs. It coordinates specialist agents, long-running tasks, persistent memory, external tools, safety policies, and human review.

## Orchestration primitives

| Primitive | Description | Persistent state |
| --- | --- | --- |
| Mission | A strategic scientific objective such as “discover high-value methods for low-resource biomedical summarisation.” | goal, sponsor, constraints, success criteria, risk tier |
| Program | A multi-week or multi-month research initiative under a mission. | milestones, budget, priority, roadmap, portfolio links |
| Work package | A scoped unit such as literature synthesis, dataset search, model benchmarking, or experiment design. | owner agent, dependencies, deliverables, evidence requirements |
| Task | A concrete executable action. | inputs, tool calls, status, checkpoints, outputs, citations |
| Review gate | A validation or approval point. | reviewer, criteria, decision, required remediation |
| Memory event | A durable update to episodic, semantic, procedural, or strategic memory. | payload, source, confidence, version, rollback pointer |

## Agent roles

### Mission controller

- Converts user or organizational goals into programs and work packages.
- Maintains the research portfolio and prevents duplicate effort.
- Escalates conflicts between cost, novelty, evidence quality, and risk.

### Discovery agent

- Watches new literature, data releases, benchmarks, and anomalies.
- Detects emerging clusters, contradictions, methodological shifts, and untested assumptions.
- Produces novelty reports and candidate hypotheses.

### Evidence extraction agent

- Extracts claims, methods, datasets, metrics, limitations, and citations.
- Links extracted claims to the scientific graph and claim store.
- Flags low-confidence extraction spans for review.

### Synthesis agent

- Builds cross-paper and cross-domain summaries.
- Finds mechanisms, analogies, reusable methods, and unresolved contradictions.
- Generates synthesis maps with confidence and provenance.

### Planning agent

- Converts hypotheses into executable research workflows.
- Estimates expected information gain, required resources, dependencies, and risks.
- Defines success metrics, baselines, validation plans, and stop conditions.

### Critique agent

- Challenges assumptions, citation fidelity, methodology, statistical validity, and reproducibility.
- Maintains contradiction ledgers and confidence adjustments.
- Requires revisions when outputs do not satisfy scientific quality gates.

### Memory steward

- Consolidates episodic traces into semantic and procedural memory.
- Detects stale knowledge, duplicate memories, and conflicting procedures.
- Manages retention, archival, and rollback policies.

### Improvement agent

- Reviews telemetry and failures to propose workflow improvements.
- Runs regression benchmarks before procedure promotion.
- Writes change proposals for human approval.

## Task graph lifecycle

1. **Intent capture:** receive a mission, constraints, risk tier, allowed tools, and output format.
2. **Mission decomposition:** produce a task graph with dependencies and candidate agents.
3. **Context retrieval:** query relevant working, semantic, episodic, procedural, and strategic memory.
4. **Execution:** dispatch tasks to agents with bounded context, tool permissions, and checkpoint cadence.
5. **Intermediate critique:** evaluate partial outputs before downstream tasks consume them.
6. **Synthesis merge:** integrate outputs into a coherent result with contradictions and uncertainty.
7. **Review gate:** apply policy, scientific quality, and human approval checks.
8. **Memory commit:** record evidence, decisions, lessons, and reusable procedures.
9. **Telemetry update:** record quality, latency, cost, failure modes, and improvement candidates.

## Scheduler design

The scheduler selects the next action using a weighted utility model:

```text
priority_score =
  mission_value
  + expected_information_gain
  + dependency_unblock_value
  + novelty_weight
  - risk_penalty
  - uncertainty_penalty
  - resource_cost
  - staleness_penalty
```

### Scheduling dimensions

- **Skill fit:** domain expertise, tool access, reasoning depth, and agent benchmark history.
- **Memory dependency:** whether the task requires specific strategic, semantic, or episodic context.
- **Risk tier:** low-risk analysis can run autonomously; high-risk recommendations need review.
- **Budget:** token cost, compute time, API cost, storage pressure, and human review capacity.
- **Freshness:** recently changed scientific areas receive higher revalidation priority.

## Governance gates

| Gate | Trigger | Required checks |
| --- | --- | --- |
| Citation fidelity | Scientific claims are produced. | source traceability, quote alignment, metadata integrity |
| Contradiction review | New claim conflicts with stored knowledge. | evidence comparison, confidence update, reviewer routing |
| Experiment safety | Workflow proposes physical, clinical, biological, or security-sensitive actions. | policy review, human approval, risk mitigation |
| Self-improvement | Agent proposes prompt, workflow, or tool-routing changes. | benchmark pass, rollback plan, change log |
| Memory mutation | Durable semantic/procedural/strategic memory is updated. | provenance, confidence, conflict resolution, retention policy |

## Failure handling

- **Checkpoint replay:** restart failed tasks from the last valid checkpoint.
- **Agent substitution:** reroute to another agent when quality or availability degrades.
- **Task decomposition:** split tasks that exceed context, cost, or uncertainty thresholds.
- **Contradiction isolation:** quarantine conflicting claims until critique resolves confidence.
- **Rollback:** revert memory or procedure changes using versioned ledgers.

## Orchestration APIs

Recommended API surfaces:

- `POST /missions`: create a scientific mission.
- `POST /programs/{id}/work-packages`: create work packages under a program.
- `POST /tasks/{id}/dispatch`: execute or resume a task.
- `POST /tasks/{id}/review`: submit critique or human review decisions.
- `POST /memory/commit`: persist a memory event.
- `GET /graph/claims`: query claims, evidence, contradictions, and confidence.
- `GET /telemetry/agents`: inspect agent quality, cost, latency, and improvement proposals.
