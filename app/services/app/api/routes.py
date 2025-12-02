"""API routes for content generation and publishing"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

from app.services.content_generator import generate_content, generate_batch_content
from app.services.telegram_handler import telegram_handler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["content"])

# Pydantic models for request/response
class GenerateContentRequest(BaseModel):
    """Request model for content generation"""
    topic: str = Field(..., min_length=3, max_length=500, description="Content topic")
    content_type: str = Field(default="social_media", description="Type: social_media, seo_article, product_description, telegram_post, email_newsletter")
    language: str = Field(default="en", description="Language code: en, ru, etc")
    tone: str = Field(default="professional", description="Tone: professional, casual, technical, creative, humorous, educational")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)

class GenerateContentResponse(BaseModel):
    """Response model for generated content"""
    content: str
    content_type: str
    language: str
    tone: str
    generated_at: datetime

class PublishContentRequest(BaseModel):
    """Request model for publishing content"""
    content: str = Field(..., min_length=1, description="Content to publish")
    caption: Optional[str] = Field(default=None, description="Optional caption")
    media_url: Optional[str] = Field(default=None, description="Optional media URL")
    parse_mode: str = Field(default="HTML", description="Parse mode: HTML, Markdown, etc")

class PublishContentResponse(BaseModel):
    """Response model for publishing"""
    success: bool
    message: str
    published_at: datetime

class BatchGenerateRequest(BaseModel):
    """Request model for batch generation"""
    topics: List[str] = Field(..., min_items=1, max_items=10)
    content_type: str = Field(default="social_media")
    language: str = Field(default="en")
    tone: str = Field(default="professional")

class BatchGenerateResponse(BaseModel):
    """Response model for batch generation"""
    contents: List[str]
    count: int
    content_type: str
    generated_at: datetime

# Routes
@router.post("/content/generate", response_model=GenerateContentResponse)
async def generate_content_endpoint(request: GenerateContentRequest):
    """Generate content using AI"""
    try:
        content = await generate_content(
            prompt=request.topic,
            content_type=request.content_type,
            language=request.language,
            tone=request.tone,
            temperature=request.temperature,
        )
        
        return GenerateContentResponse(
            content=content,
            content_type=request.content_type,
            language=request.language,
            tone=request.tone,
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/content/generate-batch", response_model=BatchGenerateResponse)
async def generate_batch_endpoint(request: BatchGenerateRequest):
    """Generate content for multiple topics"""
    try:
        contents = await generate_batch_content(
            topics=request.topics,
            content_type=request.content_type,
            language=request.language,
            tone=request.tone,
        )
        
        return BatchGenerateResponse(
            contents=contents,
            count=len(contents),
            content_type=request.content_type,
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

@router.post("/content/publish", response_model=PublishContentResponse)
async def publish_content_endpoint(request: PublishContentRequest, background_tasks: BackgroundTasks):
    """Publish content to Telegram"""
    try:
        # Publish message
        if request.media_url:
            success = await telegram_handler.send_photo(
                photo_url=request.media_url,
                caption=request.content or request.caption,
                parse_mode=request.parse_mode,
            )
        else:
            success = await telegram_handler.send_message(
                text=request.content,
                parse_mode=request.parse_mode,
            )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to publish to Telegram")
        
        logger.info(f"Content published successfully")
        
        return PublishContentResponse(
            success=True,
            message="Content published successfully",
            published_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Publishing error: {e}")
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")

@router.get("/telegram/test")
async def test_telegram_connection():
    """Test Telegram connection"""
    try:
        success = await telegram_handler.test_connection()
        if success:
            channel_info = await telegram_handler.get_channel_info()
            return {
                "status": "connected",
                "channel_info": channel_info,
                "message": "Telegram connection successful"
            }
        else:
            raise HTTPException(status_code=500, detail="Telegram connection failed")
    except Exception as e:
        logger.error(f"Telegram test error: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "operational",
        "telegram_handler": "ready",
        "content_generator": "ready",
        "timestamp": datetime.utcnow(),
    }
