from enum import Enum
from pydantic import BaseModel, EmailStr


class Role(str, Enum):
    owner = "owner"
    admin = "admin"
    researcher = "researcher"
    viewer = "viewer"


class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: Role
    workspace_ids: list[str]


class Workspace(BaseModel):
    id: str
    name: str
    member_ids: list[str]


class Paper(BaseModel):
    id: str
    title: str
    authors: list[str]
    topic: str
    score: float
    summary: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]


class Annotation(BaseModel):
    id: str
    workspace_id: str
    paper_id: str
    author_id: str
    body: str
    resolved: bool = False
