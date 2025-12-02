"""Telegram bot handler for publishing content"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

import aiohttp
from core.config import settings

logger = logging.getLogger(__name__)

class TelegramHandler:
    """Handles Telegram bot operations"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.channel_id = settings.TELEGRAM_CHANNEL_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send text message to channel"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/sendMessage"
                data = {
                    "chat_id": self.channel_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": False
                }
                async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        logger.info(f"Message sent successfully to {self.channel_id}")
                        return True
                    else:
                        logger.error(f"Failed to send message: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def send_photo(self, photo_url: str, caption: str = "", parse_mode: str = "HTML") -> bool:
        """Send photo to channel"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/sendPhoto"
                data = {
                    "chat_id": self.channel_id,
                    "photo": photo_url,
                    "caption": caption,
                    "parse_mode": parse_mode
                }
                async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        logger.info(f"Photo sent successfully")
                        return True
                    else:
                        logger.error(f"Failed to send photo: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return False
    
    async def send_album(self, media_items: List[Dict[str, Any]]) -> bool:
        """Send media album to channel
        
        Args:
            media_items: List of dicts with 'type', 'media', and optional 'caption'
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/sendMediaGroup"
                media = []
                for item in media_items:
                    media_obj = {
                        "type": item.get("type", "photo"),
                        "media": item.get("media"),
                    }
                    if item.get("caption"):
                        media_obj["caption"] = item["caption"]
                        media_obj["parse_mode"] = "HTML"
                    media.append(media_obj)
                
                data = {
                    "chat_id": self.channel_id,
                    "media": media
                }
                async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        logger.info(f"Album sent successfully")
                        return True
                    else:
                        logger.error(f"Failed to send album: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Error sending album: {e}")
            return False
    
    async def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Get channel information"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/getChat"
                data = {"chat_id": self.channel_id}
                async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get("result")
                    else:
                        logger.error(f"Failed to get channel info: {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """Test connection to Telegram API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/getMe"
                async with session.post(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        logger.info("Telegram connection test successful")
                        return True
                    else:
                        logger.error(f"Telegram connection test failed: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return False

# Global handler instance
telegram_handler = TelegramHandler()
