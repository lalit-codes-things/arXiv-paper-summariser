"""Shared workspace state for V7 collaborative research workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from .permissions import Permission, PermissionSystem, Role
from .sync_engine import SyncEngine


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass(slots=True)
class Annotation:
    id: str
    paper_id: str
    anchor: str
    body: str
    author: str
    created_at: str


@dataclass(slots=True)
class DiscussionPost:
    id: str
    subject_id: str
    body: str
    author: str
    created_at: str


@dataclass(slots=True)
class Paper:
    id: str
    arxiv_id: str
    title: str
    added_by: str
    annotations: list[Annotation] = field(default_factory=list)
    discussions: list[DiscussionPost] = field(default_factory=list)


@dataclass(slots=True)
class ResearchBoardCard:
    id: str
    title: str
    lane: str
    linked_paper_ids: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Flashcard:
    id: str
    prompt: str
    answer: str
    source_paper_id: str | None
    created_by: str


@dataclass(slots=True)
class ProjectSpace:
    id: str
    name: str
    created_by: str
    papers: dict[str, Paper] = field(default_factory=dict)
    boards: dict[str, ResearchBoardCard] = field(default_factory=dict)
    flashcards: dict[str, Flashcard] = field(default_factory=dict)
    literature_review: SyncEngine = field(init=False)
    notes: dict[str, SyncEngine] = field(default_factory=dict)
    discussions: list[DiscussionPost] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.literature_review = SyncEngine(document_id=f"literature-review:{self.id}")


@dataclass(slots=True)
class Workspace:
    id: str
    name: str
    owner_id: str
    permissions: PermissionSystem = field(init=False)
    projects: dict[str, ProjectSpace] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.permissions = PermissionSystem(workspace_id=self.id)
        self.permissions.bootstrap_owner(self.owner_id)


@dataclass(slots=True)
class SharedStateManager:
    """Aggregate root for collaborative workspaces and real-time shared state."""

    workspaces: dict[str, Workspace] = field(default_factory=dict)

    def create_workspace(self, workspace_id: str, name: str, owner_id: str) -> Workspace:
        workspace = Workspace(id=workspace_id, name=name, owner_id=owner_id)
        self.workspaces[workspace_id] = workspace
        return workspace

    def create_project(self, workspace_id: str, project_id: str, name: str, actor: str) -> ProjectSpace:
        workspace = self._workspace(workspace_id)
        workspace.permissions.require(actor, Permission.MANAGE_PROJECTS)
        project = ProjectSpace(id=project_id, name=name, created_by=actor)
        workspace.projects[project_id] = project
        return project

    def grant_role(self, workspace_id: str, user_id: str, role: Role, granted_by: str) -> None:
        self._workspace(workspace_id).permissions.grant_role(user_id, role, granted_by)

    def can(self, workspace_id: str, user_id: str, permission: Permission) -> bool:
        return self._workspace(workspace_id).permissions.can(user_id, permission)

    def add_paper(
        self,
        workspace_id: str,
        project_id: str,
        paper_id: str,
        arxiv_id: str,
        title: str,
        actor: str,
    ) -> Paper:
        workspace, project = self._workspace_and_project(workspace_id, project_id)
        workspace.permissions.require(actor, Permission.ADD_PAPERS)
        paper = Paper(id=paper_id, arxiv_id=arxiv_id, title=title, added_by=actor)
        project.papers[paper_id] = paper
        return paper

    def annotate_paper(
        self,
        workspace_id: str,
        project_id: str,
        paper_id: str,
        anchor: str,
        body: str,
        actor: str,
    ) -> Annotation:
        workspace, project = self._workspace_and_project(workspace_id, project_id)
        workspace.permissions.require(actor, Permission.ANNOTATE)
        annotation = Annotation(
            id=str(uuid4()),
            paper_id=paper_id,
            anchor=anchor,
            body=body,
            author=actor,
            created_at=_utc_now(),
        )
        project.papers[paper_id].annotations.append(annotation)
        return annotation

    def discuss(
        self,
        workspace_id: str,
        project_id: str,
        subject_id: str,
        body: str,
        actor: str,
    ) -> DiscussionPost:
        workspace, project = self._workspace_and_project(workspace_id, project_id)
        workspace.permissions.require(actor, Permission.COMMENT)
        post = DiscussionPost(
            id=str(uuid4()),
            subject_id=subject_id,
            body=body,
            author=actor,
            created_at=_utc_now(),
        )
        if subject_id in project.papers:
            project.papers[subject_id].discussions.append(post)
        else:
            project.discussions.append(post)
        return post

    def upsert_board_card(
        self,
        workspace_id: str,
        project_id: str,
        title: str,
        lane: str,
        actor: str,
        linked_paper_ids: list[str] | None = None,
        card_id: str | None = None,
    ) -> ResearchBoardCard:
        workspace, project = self._workspace_and_project(workspace_id, project_id)
        workspace.permissions.require(actor, Permission.EDIT_RESEARCH_BOARDS)
        card = ResearchBoardCard(
            id=card_id or str(uuid4()),
            title=title,
            lane=lane,
            linked_paper_ids=linked_paper_ids or [],
        )
        project.boards[card.id] = card
        return card

    def add_flashcard(
        self,
        workspace_id: str,
        project_id: str,
        prompt: str,
        answer: str,
        actor: str,
        source_paper_id: str | None = None,
    ) -> Flashcard:
        workspace, project = self._workspace_and_project(workspace_id, project_id)
        workspace.permissions.require(actor, Permission.EDIT_FLASHCARDS)
        flashcard = Flashcard(
            id=str(uuid4()),
            prompt=prompt,
            answer=answer,
            source_paper_id=source_paper_id,
            created_by=actor,
        )
        project.flashcards[flashcard.id] = flashcard
        return flashcard

    def note_engine(
        self, workspace_id: str, project_id: str, note_id: str, actor: str
    ) -> SyncEngine:
        workspace, project = self._workspace_and_project(workspace_id, project_id)
        workspace.permissions.require(actor, Permission.EDIT_NOTES)
        return project.notes.setdefault(note_id, SyncEngine(document_id=f"note:{project_id}:{note_id}"))

    def literature_review_engine(self, workspace_id: str, project_id: str, actor: str) -> SyncEngine:
        workspace, project = self._workspace_and_project(workspace_id, project_id)
        workspace.permissions.require(actor, Permission.EDIT_LITERATURE_REVIEWS)
        return project.literature_review

    def realtime_payload(self, workspace_id: str, project_id: str) -> dict[str, object]:
        """Produce a compact state payload for websocket or event-stream broadcasts."""

        _, project = self._workspace_and_project(workspace_id, project_id)
        return {
            "project_id": project.id,
            "papers": len(project.papers),
            "board_cards": len(project.boards),
            "flashcards": len(project.flashcards),
            "discussion_posts": len(project.discussions)
            + sum(len(paper.discussions) for paper in project.papers.values()),
            "literature_review": project.literature_review.snapshot(),
            "notes": {note_id: engine.snapshot() for note_id, engine in project.notes.items()},
        }

    def _workspace(self, workspace_id: str) -> Workspace:
        try:
            return self.workspaces[workspace_id]
        except KeyError as exc:
            raise KeyError(f"unknown workspace: {workspace_id}") from exc

    def _workspace_and_project(self, workspace_id: str, project_id: str) -> tuple[Workspace, ProjectSpace]:
        workspace = self._workspace(workspace_id)
        try:
            return workspace, workspace.projects[project_id]
        except KeyError as exc:
            raise KeyError(f"unknown project: {project_id}") from exc
