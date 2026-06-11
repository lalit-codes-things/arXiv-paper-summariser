from app.models.schemas import ChatResponse, Paper


def answer_paper_question(paper: Paper, message: str) -> ChatResponse:
    answer = (
        f"For {paper.title}, the most relevant lens is {paper.topic}. "
        f"Your question asks: '{message}'. The copilot would retrieve paper chunks, team annotations, "
        "and graph neighbors, then synthesize methodology, findings, limitations, and comparisons."
    )
    return ChatResponse(answer=answer, citations=[paper.id, "workspace-annotations", "relationship-graph"])
