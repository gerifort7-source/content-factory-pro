"""Pydantic schemas for API request/response validation"""
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ContentStatusEnum(str, Enum):
    draft = "draft"
    scheduled = "scheduled"
    published = "published"
    failed = "failed"
    archived = "archived"


class ContentTypeEnum(str, Enum):
    post = "post"
    story = "story"
    reel = "reel"
    carousel = "carousel"
    article = "article"


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    is_admin: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Post Schemas
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    content_type: ContentTypeEnum = ContentTypeEnum.post
    hashtags: Optional[str] = None
    ai_generated: bool = True
    ai_model: str = "openai"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class PostCreate(PostBase):
    platform: str
    media_urls: Optional[List[str]] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    hashtags: Optional[str] = None
    status: Optional[ContentStatusEnum] = None


class Post(PostBase):
    id: int
    user_id: int
    platform: str
    status: ContentStatusEnum
    media_urls: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schedule Schemas
class ScheduleBase(BaseModel):
    post_id: int
    scheduled_time: datetime
    max_retries: int = 3


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    status: Optional[ContentStatusEnum] = None


class Schedule(ScheduleBase):
    id: int
    user_id: int
    status: ContentStatusEnum
    retry_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class AnalyticsMetrics(BaseModel):
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    impressions: int = 0
    reach: int = 0
    engagement_rate: float = 0.0


class AnalyticsUpdate(BaseModel):
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    clicks: Optional[int] = None
    impressions: Optional[int] = None
    reach: Optional[int] = None


class Analytics(AnalyticsMetrics):
    id: int
    post_id: int
    platform: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Content Generation Schemas
class ContentGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    content_type: ContentTypeEnum
    platform: str
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"
    language: Optional[str] = "en"
    hashtags: bool = True
    max_tokens: int = Field(default=500, le=2000)


class ContentGenerationResponse(BaseModel):
    content: str
    title: str
    hashtags: List[str]
    ai_model: str
    tokens_used: int
    generation_time: float


# Publishing Schemas
class PublishPostRequest(BaseModel):
    post_id: int
    platform: str
    scheduled_time: Optional[datetime] = None


class PublishPostResponse(BaseModel):
    post_id: int
    status: str
    platform: str
    published_at: datetime
    message: str


# Health Check
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    database: str
    services: dict


# Error Response
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
