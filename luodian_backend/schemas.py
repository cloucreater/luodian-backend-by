from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class ArticleCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    summary: Optional[str] = None
    cover: Optional[str] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    cover: Optional[str] = None

class ArticleOut(BaseModel):
    id: int
    title: str
    content: str
    category: Optional[str]
    summary: Optional[str]
    cover: Optional[str]
    views: int
    likes: int
    comments_count: int
    created_at: datetime

class CommentCreate(BaseModel):
    article_id: int
    content: str

class CommentOut(BaseModel):
    id: int
    article_id: int
    user_id: int
    content: str
    likes: int
    created_at: datetime
    username: Optional[str] = None
    avatar: Optional[str] = None

class FavoriteCreate(BaseModel):
    article_id: int

class PostCreate(BaseModel):
    content: str
    images: Optional[List[str]] = None

class PostOut(BaseModel):
    id: int
    user_id: int
    content: str
    images: Optional[List[str]]
    likes: int
    comments_count: int
    created_at: datetime
    username: Optional[str] = None
    avatar: Optional[str] = None

class PostCommentCreate(BaseModel):
    content: str

class PostCommentOut(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime
    username: Optional[str] = None
    avatar: Optional[str] = None

class AIRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None

class AIResponse(BaseModel):
    reply: str
