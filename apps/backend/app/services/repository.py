from app.models.schemas import Paper, Role, User, Workspace

USERS = {
    "founder@arxivcopilot.ai": {
        "password": "research",
        "user": User(id="user-founder", email="founder@arxivcopilot.ai", name="Research Lead", role=Role.owner, workspace_ids=["workspace-ai-lab"]),
    }
}

WORKSPACES = {
    "workspace-ai-lab": Workspace(id="workspace-ai-lab", name="AI Lab", member_ids=["user-founder"])
}

PAPERS = [
    Paper(id="attention", title="Attention Is All You Need", authors=["Vaswani et al."], topic="transformers", score=0.98, summary="The foundational transformer architecture that enables scalable sequence modeling."),
    Paper(id="rag", title="Retrieval-Augmented Generation for Knowledge-Intensive NLP", authors=["Lewis et al."], topic="retrieval", score=0.94, summary="Combines parametric generation with non-parametric retrieval for grounded answers."),
    Paper(id="graph-rag", title="Graph Retrieval-Augmented Generation", authors=["Research Collective"], topic="graph RAG", score=0.91, summary="Uses entity and citation graphs to improve multi-hop research synthesis."),
]


def authenticate(email: str, password: str) -> User | None:
    record = USERS.get(email)
    if record and record["password"] == password:
        return record["user"]
    return None


def get_user(user_id: str) -> User | None:
    for record in USERS.values():
        if record["user"].id == user_id:
            return record["user"]
    return None


def list_feed() -> list[Paper]:
    return sorted(PAPERS, key=lambda paper: paper.score, reverse=True)


def find_paper(paper_id: str) -> Paper | None:
    return next((paper for paper in PAPERS if paper.id == paper_id), None)


ANNOTATIONS = []


def list_annotations(workspace_id: str):
    return [annotation for annotation in ANNOTATIONS if annotation.workspace_id == workspace_id]


def add_annotation(annotation):
    ANNOTATIONS.append(annotation)
    return annotation
