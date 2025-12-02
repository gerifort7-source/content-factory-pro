"""Database models for Content Factory Pro"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ContentStatus(str, enum.Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class ContentType(str, enum.Enum):
    """Content type enumeration"""
    POST = "post"
    STORY = "story"
    REEL = "reel"
    CAROUSEL = "carousel"
    ARTICLE = "article"


class ContentPlatform(str, enum.Enum):
    """Publishing platform enumeration"""
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class User(Base):
    """User model for access control"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="user", cascade="all, delete-orphan")


class Post(Base):
    """Content post model"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(Enum(ContentType), default=ContentType.POST)
    platform = Column(Enum(ContentPlatform), nullable=False)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    media_urls = Column(Text)  # JSON array of media URLs
    hashtags = Column(Text)  # Comma-separated hashtags
    ai_generated = Column(Boolean, default=True)
    ai_model = Column(String(100), default="openai")  # Model used for generation
    temperature = Column(Float, default=0.7)  # AI temperature setting
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="posts")
    schedules = relationship("Schedule", back_populates="post", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="post", cascade="all, delete-orphan")


class Schedule(Base):
    """Post scheduling model"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(Enum(ContentStatus), default=ContentStatus.SCHEDULED)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="schedules")
    post = relationship("Post", back_populates="schedules")


class Analytics(Base):
    """Analytics and engagement tracking model"""
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    platform = Column(Enum(ContentPlatform), nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="analytics")
    post = relationship("Post", back_populates="analytics")


class TelegramConfig(Base):
    """Telegram bot configuration model"""
    __tablename__ = "telegram_configs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    bot_token = Column(String(255), nullable=False)
    chat_id = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIConfig(Base):
    """AI service configuration model"""
    __tablename__ = "ai_configs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    provider = Column(String(50), default="openai")  # openai, claude, etc.
    api_key = Column(String(255), nullable=False)
    model = Column(String(100), default="gpt-3.5-turbo")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
