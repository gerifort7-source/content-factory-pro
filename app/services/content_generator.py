"""AI Content Generator using OpenAI and Anthropic"""

import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import asyncio

import openai
from core.config import settings

logger = logging.getLogger(__name__)

# Системные промпты для разных типов контента
SYSTEM_PROMPTS = {
    "social_media": """You are a professional social media content creator specializing in engaging posts.
    Create compelling, shareable content that drives engagement.
    Use relevant emojis and hashtags.
    Keep it concise and impactful.
    Language: {language}
    Tone: {tone}""",
    
    "seo_article": """You are an SEO content specialist.
    Create optimized content for search engines.
    Include relevant keywords naturally.
    Structure with headers and subheaders.
    Aim for 500-1000 words.
    Language: {language}
    Tone: {tone}""",
    
    "product_description": """You are a product marketing expert.
    Write compelling product descriptions that convert.
    Highlight key benefits and features.
    Include a call-to-action.
    Keep it professional and persuasive.
    Language: {language}
    Tone: {tone}""",
    
    "telegram_post": """You are a Telegram channel content creator.
    Create engaging posts optimized for Telegram.
    Use formatting: bold, italic, code blocks.
    Add relevant emojis.
    Include hashtags at the end.
    Keep message clear and scannable.
    Language: {language}
    Tone: {tone}""",
    
    "email_newsletter": """You are an email marketing copywriter.
    Create engaging newsletter content.
    Include subject line, preview text, and body.
    Use compelling headlines and CTAs.
    Keep paragraphs short.
    Language: {language}
    Tone: {tone}""",
}

TONE_DESCRIPTIONS = {
    "professional": "formal, business-appropriate, authoritative",
    "casual": "friendly, conversational, approachable",
    "technical": "detailed, precise, industry-specific",
    "creative": "imaginative, innovative, engaging",
    "humorous": "witty, funny, entertaining",
    "educational": "informative, explanatory, clear",
}

class ContentGenerator(ABC):
    """Base class for content generators"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

class OpenAIGenerator(ContentGenerator):
    """OpenAI-based content generator"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        openai.api_key = self.api_key
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate content using OpenAI"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model,
                messages=messages,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9),
            )
            
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def generate_with_template(
        self,
        content_type: str,
        topic: str,
        language: str = "en",
        tone: str = "professional",
        **kwargs
    ) -> str:
        """Generate content using predefined template"""
        if content_type not in SYSTEM_PROMPTS:
            raise ValueError(f"Unknown content type: {content_type}")
        
        system_prompt = SYSTEM_PROMPTS[content_type].format(
            language=language,
            tone=TONE_DESCRIPTIONS.get(tone, tone)
        )
        
        user_prompt = f"Create {content_type} content about: {topic}"
        
        return await self.generate(user_prompt, system_prompt=system_prompt, **kwargs)
    
    async def generate_batch(
        self,
        topics: List[str],
        content_type: str = "social_media",
        language: str = "en",
        tone: str = "professional",
    ) -> List[str]:
        """Generate content for multiple topics"""
        tasks = [
            self.generate_with_template(
                content_type=content_type,
                topic=topic,
                language=language,
                tone=tone,
            )
            for topic in topics
        ]
        return await asyncio.gather(*tasks)

class ContentGeneratorFactory:
    """Factory for creating content generators"""
    
    _generators = {
        "openai": OpenAIGenerator,
        # "anthropic": AnthropicGenerator,  # Can be added later
    }
    
    @classmethod
    def create(cls, provider: str = "openai", **kwargs) -> ContentGenerator:
        """Create generator by provider"""
        if provider not in cls._generators:
            raise ValueError(f"Unknown provider: {provider}")
        
        return cls._generators[provider](**kwargs)

# Global generator instance
generator = ContentGeneratorFactory.create()

# Convenience functions
async def generate_content(
    prompt: str,
    content_type: str = "social_media",
    language: str = "en",
    tone: str = "professional",
    **kwargs
) -> str:
    """Generate content with template"""
    return await generator.generate_with_template(
        content_type=content_type,
        topic=prompt,
        language=language,
        tone=tone,
        **kwargs
    )

async def generate_batch_content(
    topics: List[str],
    content_type: str = "social_media",
    language: str = "en",
    tone: str = "professional",
) -> List[str]:
    """Generate content for multiple topics"""
    return await generator.generate_batch(
        topics=topics,
        content_type=content_type,
        language=language,
        tone=tone,
    )

async def generate_custom(
    prompt: str,
    system_prompt: str,
    **kwargs
) -> str:
    """Generate content with custom system prompt"""
    return await generator.generate(prompt, system_prompt=system_prompt, **kwargs)
