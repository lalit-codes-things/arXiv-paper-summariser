from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from app.core.security import create_access_token, current_user, require_roles
from app.models.schemas import Annotation, ChatRequest, ChatResponse, LoginRequest, Paper, Role, TokenResponse, User
from app.services.chat import answer_paper_question
from app.services.realtime import manager
from app.services.repository import add_annotation, authenticate, find_paper, list_annotations, list_feed

router = APIRouter(prefix="/api/v1")


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: LoginRequest) -> TokenResponse:
    user = authenticate(payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user))


@router.get("/me", response_model=User, tags=["auth"])
def me(user: Annotated[User, Depends(current_user)]) -> User:
    return user


@router.get("/feed", response_model=list[Paper], tags=["research"])
def feed() -> list[Paper]:
    return list_feed()


@router.get("/dashboard", tags=["research"])
def dashboard(user: Annotated[User, Depends(require_roles(Role.owner, Role.admin, Role.researcher, Role.viewer))]) -> dict:
    papers = list_feed()
    return {
        "workspace_ids": user.workspace_ids,
        "trends": ["agentic retrieval", "graph RAG", "multimodal reasoning", "evaluation harnesses"],
        "reading_stats": {"read": 128, "bookmarked": 42, "discussed": 19},
        "saved_topics": ["retrieval", "alignment", "agents"],
        "recommended": papers[:3],
    }


@router.get("/graph", tags=["research"])
def graph() -> dict:
    return {
        "nodes": [
            {"id": "attention", "label": "Transformers", "group": "method"},
            {"id": "rag", "label": "RAG", "group": "method"},
            {"id": "graph-rag", "label": "Graph RAG", "group": "method"},
            {"id": "bench", "label": "Benchmarks", "group": "evaluation"},
        ],
        "edges": [
            {"source": "attention", "target": "rag", "weight": 0.5},
            {"source": "rag", "target": "graph-rag", "weight": 0.9},
            {"source": "graph-rag", "target": "bench", "weight": 0.7},
        ],
    }


@router.post("/papers/{paper_id}/chat", response_model=ChatResponse, tags=["ai"])
def paper_chat(paper_id: str, payload: ChatRequest, _: Annotated[User, Depends(current_user)]) -> ChatResponse:
    paper = find_paper(paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return answer_paper_question(paper, payload.message)


@router.get("/workspaces/{workspace_id}/annotations", response_model=list[Annotation], tags=["workspaces"])
def workspace_annotations(workspace_id: str, _: Annotated[User, Depends(current_user)]) -> list[Annotation]:
    return list_annotations(workspace_id)


@router.post("/workspaces/{workspace_id}/annotations", response_model=Annotation, tags=["workspaces"])
async def create_annotation(workspace_id: str, annotation: Annotation, user: Annotated[User, Depends(require_roles(Role.owner, Role.admin, Role.researcher))]) -> Annotation:
    saved = add_annotation(annotation.model_copy(update={"workspace_id": workspace_id, "author_id": user.id}))
    await manager.broadcast(workspace_id, {"type": "annotation.created", "payload": saved.model_dump()})
    return saved


@router.websocket("/workspaces/{workspace_id}/ws")
async def workspace_socket(websocket: WebSocket, workspace_id: str) -> None:
    await manager.connect(workspace_id, websocket)
    await manager.broadcast(workspace_id, {"type": "presence.joined", "workspace_id": workspace_id})
    try:
        while True:
            message = await websocket.receive_json()
            await manager.broadcast(workspace_id, {"type": "workspace.update", "payload": message})
    except WebSocketDisconnect:
        manager.disconnect(workspace_id, websocket)
