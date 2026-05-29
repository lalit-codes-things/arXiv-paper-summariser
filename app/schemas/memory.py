from datetime import datetime

from pydantic import BaseModel, Field


class UserProfileRead(BaseModel):
    id: str
    interests: list[str] = Field(default_factory=list)
    topic_clusters: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class MemoryEvent(BaseModel):
    user_id: str
    paper_id: str
    action: str = "viewed"
    notes: str | None = None


class ReadingHistoryRead(BaseModel):
    id: int
    user_id: str
    paper_id: str
    action: str
    notes: str | None = None
    viewed_at: datetime

    model_config = {"from_attributes": True}
