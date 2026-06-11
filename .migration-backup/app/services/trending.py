from app.repositories.papers import PaperRepository
from app.schemas.paper import PaperRead, TrendingPaper


class TrendingService:
    def __init__(self, papers: PaperRepository):
        self.papers = papers

    async def trending(self, *, limit: int = 10) -> list[TrendingPaper]:
        rows = await self.papers.trending(limit=limit)
        return [
            TrendingPaper(
                paper=PaperRead.model_validate(paper),
                score=score,
                reason="recent views and search activity",
            )
            for paper, score in rows
        ]
