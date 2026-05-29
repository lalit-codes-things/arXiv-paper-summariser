# arXiv Paper Summariser — V7 Collaborative Research Cloud

V7 upgrades this repository from a single-user summariser concept into a collaborative AI-native research cloud platform. It introduces shared workspaces, project spaces, collaborative annotations, real-time note editing, paper discussions, shared literature reviews, shared flashcards, shared research boards, and role-based permissions.

## V7 capabilities

- **Shared workspaces and project spaces** for teams, labs, courses, and review groups.
- **Role-based permissions** with owner, admin, editor, commenter, viewer, and AI-agent roles.
- **Collaborative annotations** anchored to papers with threaded comments and citation context.
- **Paper discussions** for project-level and paper-level debate, decisions, and follow-ups.
- **Shared literature reviews** backed by mergeable shared state and permission-aware edits.
- **Shared flashcards** that teams can curate from papers, annotations, and notes.
- **Shared research boards** for kanban-style triage, reading queues, evidence maps, and synthesis workflows.
- **Real-time collaboration** through a deterministic CRDT-style sync engine.
- **Collaborative note editing** with operation logs, vector clocks, snapshots, and replayable state.

## Repository layout

```text
src/research_cloud/
  architecture.py      # V7 platform topology and collaboration architecture generator
  permissions.py       # Role-based permission model and resource scopes
  shared_state.py      # Workspace/project aggregate state manager
  sync_engine.py       # CRDT-style operation log and conflict resolution

docs/
  V7_COLLABORATION_ARCHITECTURE.md

tests/
  test_v7_collaboration.py
```

## Quick start

```bash
python -m pytest
```

## Example

```python
from research_cloud import (
    Permission,
    Role,
    SharedStateManager,
    SyncEngine,
)

state = SharedStateManager()
workspace = state.create_workspace("workspace-1", "AI Safety Lab", "alice")
project = state.create_project("workspace-1", "project-1", "Alignment Review", "alice")

state.grant_role("workspace-1", "bob", Role.EDITOR, granted_by="alice")
state.add_paper("workspace-1", "project-1", "paper-1", "2301.00001", "A Useful Paper", actor="bob")

sync = SyncEngine(document_id="note-1")
sync.apply_local_insert(actor="alice", index=0, text="Read introduction")
sync.apply_local_insert(actor="bob", index=18, text=" and methods")

assert state.can("workspace-1", "bob", Permission.EDIT_NOTES)
assert sync.materialize() == "Read introduction and methods"
```
