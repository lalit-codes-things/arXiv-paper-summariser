from arxiv_paper_summariser_v15 import (
    ArchitectureSpec,
    BenchmarkPredictionSystem,
    ExperimentPlanningWorkflow,
    ExperimentSpec,
    SimulationEngine,
)


def make_architecture(name="candidate"):
    return ArchitectureSpec(
        name=name,
        encoder_layers=12,
        decoder_layers=12,
        hidden_size=768,
        retrieval_depth=8,
        context_window=16_384,
        novelty_factor=0.45,
    )


def make_experiment():
    return ExperimentSpec(
        name="pilot",
        dataset_size=100_000,
        training_steps=10_000,
        evaluation_samples=4_000,
        ablations=("retrieval", "reranking", "citation_grounding"),
    )


def test_simulation_engine_estimates_experiment_and_ablation_outputs():
    engine = SimulationEngine()
    result = engine.run(make_architecture(), make_experiment())

    assert result.estimated_gpu_hours > 0
    assert result.estimated_cost_usd > 0
    assert 0 < result.confidence <= 1
    assert set(result.ablation_impacts) == {"retrieval", "reranking", "citation_grounding"}
    assert {"rouge_l", "faithfulness", "citation_f1", "latency_p95_ms"}.issubset(
        result.benchmark_predictions
    )
    assert result.recommendation


def test_benchmark_prediction_system_creates_intervals_and_baseline_deltas():
    result = SimulationEngine().run(make_architecture(), make_experiment())
    system = BenchmarkPredictionSystem()

    predictions = system.predict(result)
    deltas = system.compare_to_baseline(result, {"rouge_l": 45.0, "faithfulness": 0.70})

    assert len(predictions) == len(result.benchmark_predictions)
    assert all(pred.lower_bound <= pred.expected_value <= pred.upper_bound for pred in predictions)
    assert "rouge_l" in deltas
    assert "citation_f1" in deltas


def test_experiment_planning_workflow_selects_candidate_and_builds_backlog():
    conservative = make_architecture("conservative")
    ambitious = ArchitectureSpec(
        name="ambitious",
        encoder_layers=18,
        decoder_layers=12,
        hidden_size=1024,
        retrieval_depth=12,
        context_window=32_768,
        novelty_factor=0.65,
    )
    workflow = ExperimentPlanningWorkflow()

    plan = workflow.generate_plan(
        objective="simulate before implementation",
        architectures=[conservative, ambitious],
        experiment=make_experiment(),
    )
    backlog = workflow.build_research_backlog(plan)

    assert plan.selected_candidate.architecture_name in {"conservative", "ambitious"}
    assert plan.benchmark_predictions
    assert plan.acceptance_gates
    assert backlog[0]["phase"] == "simulate"
    assert backlog[-1]["phase"] == "gate"


def test_empty_architecture_list_is_rejected():
    workflow = ExperimentPlanningWorkflow()

    try:
        workflow.generate_plan("invalid", [], make_experiment())
    except ValueError as exc:
        assert "At least one architecture" in str(exc)
    else:
        raise AssertionError("expected ValueError for empty architecture list")
