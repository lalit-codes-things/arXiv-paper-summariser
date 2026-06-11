"""Deterministic CRDT-style sync engine for collaborative note editing."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import count
from typing import Iterable


class OperationType(str, Enum):
    """Operation types supported by the V7 sync engine."""

    INSERT = "insert"
    DELETE = "delete"
    SET_FIELD = "set_field"


@dataclass(frozen=True, order=True, slots=True)
class OperationId:
    """Stable operation identifier used for deterministic merges."""

    counter: int
    actor: str

    def as_string(self) -> str:
        return f"{self.actor}:{self.counter}"


@dataclass(frozen=True, slots=True)
class Operation:
    """A sync operation with vector-clock metadata."""

    op_id: OperationId
    document_id: str
    op_type: OperationType
    actor: str
    payload: dict[str, object]
    parents: tuple[str, ...] = ()


@dataclass(slots=True)
class _CharAtom:
    value: str
    op_id: OperationId
    deleted: bool = False


@dataclass(slots=True)
class SyncEngine:
    """Mergeable operation log for collaborative notes and shared objects.

    Text editing uses an RGA-inspired sequence of immutable character atoms. Concurrent
    inserts are ordered by operation id, deletes are idempotent tombstones, and every
    operation is retained in an append-only log for replay, snapshots, and audit trails.
    """

    document_id: str
    _counter: count = field(default_factory=lambda: count(1), init=False, repr=False)
    _text: list[_CharAtom] = field(default_factory=list, init=False, repr=False)
    _fields: dict[str, object] = field(default_factory=dict, init=False, repr=False)
    _seen: set[str] = field(default_factory=set, init=False, repr=False)
    operations: list[Operation] = field(default_factory=list)
    vector_clock: dict[str, int] = field(default_factory=dict)

    def apply_local_insert(self, actor: str, index: int, text: str) -> Operation:
        """Insert text locally and return the generated operation."""

        op = self._new_operation(actor, OperationType.INSERT, {"index": index, "text": text})
        self.apply_remote(op)
        return op

    def apply_local_delete(self, actor: str, index: int, length: int) -> Operation:
        """Delete a range locally with tombstones and return the generated operation."""

        op = self._new_operation(actor, OperationType.DELETE, {"index": index, "length": length})
        self.apply_remote(op)
        return op

    def apply_local_set_field(self, actor: str, key: str, value: object) -> Operation:
        """Set metadata on a shared object using last-writer-wins ordering."""

        op = self._new_operation(actor, OperationType.SET_FIELD, {"key": key, "value": value})
        self.apply_remote(op)
        return op

    def merge(self, operations: Iterable[Operation]) -> None:
        """Merge remote operations in deterministic order."""

        for op in sorted(operations, key=lambda candidate: candidate.op_id):
            self.apply_remote(op)

    def apply_remote(self, op: Operation) -> None:
        """Apply a remote operation once."""

        if op.document_id != self.document_id:
            raise ValueError(f"operation targets '{op.document_id}', not '{self.document_id}'")
        if op.op_id.as_string() in self._seen:
            return

        if op.op_type == OperationType.INSERT:
            self._apply_insert(op)
        elif op.op_type == OperationType.DELETE:
            self._apply_delete(op)
        elif op.op_type == OperationType.SET_FIELD:
            self._apply_set_field(op)
        else:
            raise ValueError(f"unsupported operation type: {op.op_type}")

        self._seen.add(op.op_id.as_string())
        self.operations.append(op)
        self.vector_clock[op.actor] = max(self.vector_clock.get(op.actor, 0), op.op_id.counter)

    def materialize(self) -> str:
        """Return the visible note text."""

        return "".join(atom.value for atom in self._text if not atom.deleted)

    def field(self, key: str, default: object | None = None) -> object | None:
        """Read shared object metadata."""

        return self._fields.get(key, default)

    def snapshot(self) -> dict[str, object]:
        """Return a serializable snapshot for clients joining a live session."""

        return {
            "document_id": self.document_id,
            "text": self.materialize(),
            "fields": dict(self._fields),
            "vector_clock": dict(self.vector_clock),
            "operations": [
                {
                    "op_id": op.op_id.as_string(),
                    "type": op.op_type.value,
                    "actor": op.actor,
                    "payload": dict(op.payload),
                    "parents": list(op.parents),
                }
                for op in self.operations
            ],
        }

    def _new_operation(self, actor: str, op_type: OperationType, payload: dict[str, object]) -> Operation:
        op_id = OperationId(next(self._counter), actor)
        return Operation(
            op_id=op_id,
            document_id=self.document_id,
            op_type=op_type,
            actor=actor,
            payload=payload,
            parents=tuple(sorted(self._seen)),
        )

    def _apply_insert(self, op: Operation) -> None:
        visible_index = int(op.payload["index"])
        text = str(op.payload["text"])
        physical_index = self._physical_index_for_visible_index(visible_index)
        atoms = [_CharAtom(value=char, op_id=op.op_id) for char in text]

        while physical_index < len(self._text) and self._text[physical_index].op_id < op.op_id:
            physical_index += 1
        self._text[physical_index:physical_index] = atoms

    def _apply_delete(self, op: Operation) -> None:
        visible_index = int(op.payload["index"])
        length = int(op.payload["length"])
        deleted = 0
        current_visible = 0
        for atom in self._text:
            if atom.deleted:
                continue
            if current_visible >= visible_index and deleted < length:
                atom.deleted = True
                deleted += 1
            current_visible += 1
            if deleted == length:
                break

    def _apply_set_field(self, op: Operation) -> None:
        key = str(op.payload["key"])
        latest = self._field_versions().get(key)
        if latest is None or latest < op.op_id:
            self._fields[key] = op.payload["value"]

    def _physical_index_for_visible_index(self, visible_index: int) -> int:
        if visible_index < 0:
            raise ValueError("index must be non-negative")
        if visible_index == 0:
            return 0

        visible_seen = 0
        for index, atom in enumerate(self._text):
            if not atom.deleted:
                visible_seen += 1
            if visible_seen == visible_index:
                return index + 1
        return len(self._text)

    def _field_versions(self) -> dict[str, OperationId]:
        versions: dict[str, OperationId] = {}
        for op in self.operations:
            if op.op_type == OperationType.SET_FIELD:
                key = str(op.payload["key"])
                versions[key] = max(versions.get(key, op.op_id), op.op_id)
        return versions
