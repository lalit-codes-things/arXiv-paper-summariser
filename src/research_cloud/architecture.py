"""Collaboration architecture generator for the V7 research cloud."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CollaborationArchitecture:
    """Serializable description of the V7 collaborative platform topology."""

    name: str
    principles: tuple[str, ...]
    client_surfaces: tuple[str, ...]
    collaboration_services: tuple[str, ...]
    data_planes: tuple[str, ...]
    ai_native_services: tuple[str, ...]
    realtime_channels: tuple[str, ...]
    security_controls: tuple[str, ...]
    shared_objects: tuple[str, ...]
    sync_strategy: str
    rollout_phases: tuple[str, ...] = field(default_factory=tuple)

    def as_markdown(self) -> str:
        """Render the architecture as documentation."""

        sections = [
            f"# {self.name}",
            "## Principles\n" + _bullets(self.principles),
            "## Client surfaces\n" + _bullets(self.client_surfaces),
            "## Collaboration services\n" + _bullets(self.collaboration_services),
            "## Data planes\n" + _bullets(self.data_planes),
            "## AI-native services\n" + _bullets(self.ai_native_services),
            "## Real-time channels\n" + _bullets(self.realtime_channels),
            "## Security controls\n" + _bullets(self.security_controls),
            "## Shared objects\n" + _bullets(self.shared_objects),
            f"## Sync strategy\n{self.sync_strategy}",
            "## Rollout phases\n" + _bullets(self.rollout_phases),
        ]
        return "\n\n".join(sections) + "\n"


def build_v7_architecture() -> CollaborationArchitecture:
    """Build the V7 architecture for collaborative AI-native research."""

    return CollaborationArchitecture(
        name="V7 Collaborative AI-Native Research Cloud Architecture",
        principles=(
            "Every research artifact is a permissioned, shareable workspace object.",
            "Real-time collaboration is event-sourced and replayable for auditability.",
            "AI agents participate with explicit roles, scoped permissions, and visible provenance.",
            "Offline-first edits converge through deterministic CRDT-style operation merging.",
        ),
        client_surfaces=(
            "Workspace dashboard for labs, classes, and review teams.",
            "Project spaces for reading queues, evidence maps, notes, and synthesis drafts.",
            "Paper reader with shared annotations, comments, and AI-generated summaries.",
            "Collaborative note editor for live literature reviews and meeting notes.",
            "Research board view for triage, kanban workflows, and synthesis planning.",
            "Shared flashcard deck view for spaced repetition and team study workflows.",
        ),
        collaboration_services=(
            "Workspace service for membership, invitations, project creation, and settings.",
            "Permission service for role-based access checks and audit logging.",
            "Sync gateway for websocket fan-out, reconnects, snapshots, and operation replay.",
            "Annotation service for anchored highlights, margin notes, and threaded replies.",
            "Discussion service for paper-level and project-level conversations.",
            "Review service for shared literature review drafts and citation-backed sections.",
            "Flashcard service for shared decks generated from papers, notes, and annotations.",
        ),
        data_planes=(
            "Transactional metadata store for workspaces, projects, roles, papers, and boards.",
            "Append-only operation log for notes, reviews, boards, annotations, and discussions.",
            "Vector index for semantic search over papers, notes, review sections, and comments.",
            "Object storage for PDFs, extracted figures, generated exports, and attachments.",
            "Cache and presence store for cursors, active collaborators, and ephemeral session data.",
        ),
        ai_native_services=(
            "Research copilot that can summarize, compare, and critique papers inside a project.",
            "Citation-grounded literature review assistant with explicit source provenance.",
            "Flashcard generator that proposes cards requiring editor approval before publication.",
            "Board assistant that clusters papers by method, claim, dataset, and open question.",
            "Moderation and safety checks for shared comments, generated text, and agent actions.",
        ),
        realtime_channels=(
            "workspace:{id}:presence for online members, cursors, and editing locations.",
            "project:{id}:events for paper additions, boards, flashcards, and discussions.",
            "document:{id}:ops for CRDT note and literature review operations.",
            "paper:{id}:annotations for highlights, anchors, replies, and resolution events.",
        ),
        security_controls=(
            "Workspace-scoped roles: owner, admin, editor, commenter, viewer, and AI agent.",
            "Permission checks before every shared-state mutation and sync operation broadcast.",
            "Audit log for membership changes, AI actions, destructive edits, and exports.",
            "Tenant isolation for workspace data, vector indexes, object storage, and cache keys.",
            "Snapshot signing and operation idempotency to protect reconnect and replay flows.",
        ),
        shared_objects=(
            "Shared workspaces",
            "Project spaces",
            "Collaborative annotations",
            "Paper discussions",
            "Shared literature reviews",
            "Shared flashcards",
            "Shared research boards",
            "Collaborative notes",
        ),
        sync_strategy=(
            "Use an append-only operation log with deterministic CRDT-style text operations, "
            "last-writer-wins metadata fields, vector clocks for client catch-up, and snapshots "
            "for fast session joins. Operational transforms can be introduced at the gateway for "
            "legacy clients, but canonical server state is CRDT-compatible and replayable."
        ),
        rollout_phases=(
            "Phase 1: introduce workspaces, projects, roles, and audit-backed shared metadata.",
            "Phase 2: enable real-time notes, shared literature reviews, and operation replay.",
            "Phase 3: add annotations, discussions, shared boards, and shared flashcards.",
            "Phase 4: add AI agents with scoped permissions, provenance, and approval workflows.",
        ),
    )


def _bullets(values: tuple[str, ...]) -> str:
    return "\n".join(f"- {value}" for value in values)
