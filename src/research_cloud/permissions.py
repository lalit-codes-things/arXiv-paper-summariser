"""Role-based permissions for V7 collaborative research workspaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Permission(str, Enum):
    """Actions that can be granted within a workspace or project scope."""

    MANAGE_WORKSPACE = "manage_workspace"
    MANAGE_PROJECTS = "manage_projects"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_PERMISSIONS = "manage_permissions"
    VIEW_PAPERS = "view_papers"
    ADD_PAPERS = "add_papers"
    EDIT_NOTES = "edit_notes"
    COMMENT = "comment"
    ANNOTATE = "annotate"
    EDIT_LITERATURE_REVIEWS = "edit_literature_reviews"
    EDIT_FLASHCARDS = "edit_flashcards"
    EDIT_RESEARCH_BOARDS = "edit_research_boards"
    RUN_AI_AGENTS = "run_ai_agents"


class Role(str, Enum):
    """Built-in V7 collaboration roles."""

    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    COMMENTER = "commenter"
    VIEWER = "viewer"
    AI_AGENT = "ai_agent"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.OWNER: frozenset(Permission),
    Role.ADMIN: frozenset(
        permission for permission in Permission if permission != Permission.MANAGE_WORKSPACE
    ),
    Role.EDITOR: frozenset(
        {
            Permission.VIEW_PAPERS,
            Permission.ADD_PAPERS,
            Permission.EDIT_NOTES,
            Permission.COMMENT,
            Permission.ANNOTATE,
            Permission.EDIT_LITERATURE_REVIEWS,
            Permission.EDIT_FLASHCARDS,
            Permission.EDIT_RESEARCH_BOARDS,
            Permission.RUN_AI_AGENTS,
        }
    ),
    Role.COMMENTER: frozenset(
        {
            Permission.VIEW_PAPERS,
            Permission.COMMENT,
            Permission.ANNOTATE,
        }
    ),
    Role.VIEWER: frozenset({Permission.VIEW_PAPERS}),
    Role.AI_AGENT: frozenset(
        {
            Permission.VIEW_PAPERS,
            Permission.EDIT_NOTES,
            Permission.COMMENT,
            Permission.ANNOTATE,
            Permission.EDIT_LITERATURE_REVIEWS,
            Permission.EDIT_FLASHCARDS,
            Permission.EDIT_RESEARCH_BOARDS,
        }
    ),
}


class PermissionDenied(RuntimeError):
    """Raised when an actor attempts an unauthorized collaboration action."""


@dataclass(slots=True)
class PermissionSystem:
    """Permission registry for workspace members.

    The model intentionally keeps role assignment deterministic and serializable so it can be
    replicated in the shared-state log alongside notes, annotations, boards, and discussions.
    """

    workspace_id: str
    assignments: dict[str, Role] = field(default_factory=dict)
    audit_log: list[dict[str, str]] = field(default_factory=list)

    def bootstrap_owner(self, user_id: str) -> None:
        """Create the first owner without requiring an existing grantor."""

        if self.assignments:
            raise PermissionDenied("workspace owner can only be bootstrapped once")
        self.assignments[user_id] = Role.OWNER
        self.audit_log.append(
            {"actor": "system", "target": user_id, "role": Role.OWNER.value, "action": "bootstrap"}
        )

    def grant_role(self, user_id: str, role: Role, granted_by: str) -> None:
        """Grant a role when the grantor can manage permissions."""

        self.require(granted_by, Permission.MANAGE_PERMISSIONS)
        self.assignments[user_id] = role
        self.audit_log.append(
            {"actor": granted_by, "target": user_id, "role": role.value, "action": "grant"}
        )

    def revoke(self, user_id: str, revoked_by: str) -> None:
        """Remove a member from the workspace."""

        self.require(revoked_by, Permission.MANAGE_MEMBERS)
        if self.assignments.get(user_id) == Role.OWNER:
            owner_count = sum(1 for role in self.assignments.values() if role == Role.OWNER)
            if owner_count == 1:
                raise PermissionDenied("cannot remove the last workspace owner")
        self.assignments.pop(user_id, None)
        self.audit_log.append({"actor": revoked_by, "target": user_id, "action": "revoke"})

    def role_for(self, user_id: str) -> Role | None:
        """Return the actor's role, if any."""

        return self.assignments.get(user_id)

    def can(self, user_id: str, permission: Permission) -> bool:
        """Return whether an actor is allowed to perform an action."""

        role = self.role_for(user_id)
        if role is None:
            return False
        return permission in ROLE_PERMISSIONS[role]

    def require(self, user_id: str, permission: Permission) -> None:
        """Raise when an actor does not have the requested permission."""

        if not self.can(user_id, permission):
            raise PermissionDenied(
                f"actor '{user_id}' lacks '{permission.value}' in workspace '{self.workspace_id}'"
            )
