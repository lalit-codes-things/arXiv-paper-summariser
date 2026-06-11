import pytest

from research_cloud import (
    Permission,
    PermissionDenied,
    Role,
    SharedStateManager,
    SyncEngine,
    build_v7_architecture,
)


def test_permissioned_workspace_project_and_shared_artifacts():
    state = SharedStateManager()
    state.create_workspace("ws", "AI Safety Lab", "alice")
    state.create_project("ws", "alignment", "Alignment Literature Review", "alice")
    state.grant_role("ws", "bob", Role.EDITOR, granted_by="alice")

    paper = state.add_paper(
        "ws", "alignment", "paper-1", "2301.00001", "Scalable Oversight", actor="bob"
    )
    annotation = state.annotate_paper(
        "ws", "alignment", paper.id, "page=2&quote=claim", "Important claim", actor="bob"
    )
    discussion = state.discuss("ws", "alignment", paper.id, "Should compare to RLAIF.", actor="bob")
    card = state.upsert_board_card(
        "ws", "alignment", "Compare oversight papers", "Synthesis", "bob", [paper.id]
    )
    flashcard = state.add_flashcard(
        "ws", "alignment", "What is scalable oversight?", "AI-assisted supervision.", "bob", paper.id
    )

    assert state.can("ws", "bob", Permission.EDIT_LITERATURE_REVIEWS)
    assert annotation in paper.annotations
    assert discussion in paper.discussions
    assert card.linked_paper_ids == [paper.id]
    assert flashcard.source_paper_id == paper.id


def test_viewer_cannot_mutate_shared_state():
    state = SharedStateManager()
    state.create_workspace("ws", "AI Safety Lab", "alice")
    state.create_project("ws", "alignment", "Alignment Literature Review", "alice")
    state.grant_role("ws", "eve", Role.VIEWER, granted_by="alice")

    with pytest.raises(PermissionDenied):
        state.add_paper("ws", "alignment", "paper-1", "2301.00001", "Scalable Oversight", "eve")


def test_sync_engine_merges_text_operations_and_snapshots():
    alice = SyncEngine(document_id="note-1")
    bob = SyncEngine(document_id="note-1")

    op1 = alice.apply_local_insert("alice", 0, "Read intro")
    bob.merge([op1])
    op2 = bob.apply_local_insert("bob", 10, " and methods")
    alice.merge([op2])

    assert alice.materialize() == bob.materialize()
    assert alice.materialize() == "Read intro and methods"
    assert alice.snapshot()["vector_clock"] == {"alice": 1, "bob": 1}

    delete_op = alice.apply_local_delete("alice", 10, 12)
    bob.merge([delete_op])
    assert bob.materialize() == "Read intro"


def test_shared_literature_review_and_realtime_payload():
    state = SharedStateManager()
    state.create_workspace("ws", "AI Safety Lab", "alice")
    state.create_project("ws", "alignment", "Alignment Literature Review", "alice")
    review = state.literature_review_engine("ws", "alignment", "alice")
    review.apply_local_insert("alice", 0, "## Findings")

    note = state.note_engine("ws", "alignment", "meeting", "alice")
    note.apply_local_insert("alice", 0, "Discuss benchmarks")

    payload = state.realtime_payload("ws", "alignment")
    assert payload["literature_review"]["text"] == "## Findings"
    assert payload["notes"]["meeting"]["text"] == "Discuss benchmarks"


def test_architecture_generator_names_required_v7_surfaces():
    markdown = build_v7_architecture().as_markdown()

    assert "Shared workspaces" in markdown
    assert "Project spaces" in markdown
    assert "Collaborative annotations" in markdown
    assert "Shared flashcards" in markdown
    assert "CRDT" in markdown
