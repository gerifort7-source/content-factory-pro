"""Scheduler service for automatic post publishing"""
import logging
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
import pytz

from app.services.telegram_handler import TelegramHandler

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing post scheduling and publishing"""

    def __init__(self):
        """Initialize scheduler service"""
        self.scheduler = BackgroundScheduler()
        self.telegram_handler = TelegramHandler()
        self._jobs = {}

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler service started")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler service shutdown")

    def schedule_post(self, post_id: int, scheduled_time: datetime, chat_id: str, content: str, media_urls: Optional[list] = None) -> str:
        """Schedule a post for publishing
        
        Args:
            post_id: ID of the post to schedule
            scheduled_time: When to publish the post
            chat_id: Telegram chat ID
            content: Post content text
            media_urls: Optional list of media URLs
            
        Returns:
            Job ID for the scheduled task
        """
        try:
            job_id = f"post_{post_id}_{int(scheduled_time.timestamp())}"
            
            job = self.scheduler.add_job(
                self._publish_post,
                DateTrigger(run_date=scheduled_time),
                args=[post_id, chat_id, content, media_urls],
                id=job_id,
                name=f"Publish post {post_id}",
                replace_existing=True,
            )
            
            self._jobs[post_id] = job_id
            logger.info(f"Post {post_id} scheduled for {scheduled_time}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error scheduling post {post_id}: {str(e)}")
            raise

    def schedule_recurring_post(self, post_id: int, cron_expression: str, chat_id: str, content: str, timezone: str = "UTC") -> str:
        """Schedule a recurring post
        
        Args:
            post_id: ID of the post
            cron_expression: Cron expression for scheduling (e.g., '0 9 * * 1' for 9 AM Monday)
            chat_id: Telegram chat ID
            content: Post content text
            timezone: Timezone for cron scheduling
            
        Returns:
            Job ID for the scheduled task
        """
        try:
            job_id = f"recurring_post_{post_id}"
            
            job = self.scheduler.add_job(
                self._publish_post,
                CronTrigger.from_crontab(cron_expression, timezone=pytz.timezone(timezone)),
                args=[post_id, chat_id, content, None],
                id=job_id,
                name=f"Recurring post {post_id}",
                replace_existing=True,
            )
            
            self._jobs[post_id] = job_id
            logger.info(f"Recurring post {post_id} scheduled: {cron_expression}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error scheduling recurring post {post_id}: {str(e)}")
            raise

    def cancel_scheduled_post(self, post_id: int) -> bool:
        """Cancel a scheduled post
        
        Args:
            post_id: ID of the post to cancel
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        try:
            if post_id in self._jobs:
                job_id = self._jobs[post_id]
                self.scheduler.remove_job(job_id)
                del self._jobs[post_id]
                logger.info(f"Scheduled post {post_id} cancelled")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelling post {post_id}: {str(e)}")
            return False

    async def _publish_post(self, post_id: int, chat_id: str, content: str, media_urls: Optional[list] = None):
        """Internal method to publish a post
        
        Args:
            post_id: ID of the post
            chat_id: Telegram chat ID
            content: Post content text
            media_urls: Optional list of media URLs
        """
        try:
            logger.info(f"Publishing post {post_id} to chat {chat_id}")
            
            if media_urls:
                for media_url in media_urls:
                    await self.telegram_handler.send_media(chat_id, media_url, content)
            else:
                await self.telegram_handler.send_message(chat_id, content)
                
            logger.info(f"Post {post_id} published successfully")
            
        except Exception as e:
            logger.error(f"Error publishing post {post_id}: {str(e)}")
            raise

    def get_scheduled_jobs(self) -> dict:
        """Get all scheduled jobs
        
        Returns:
            Dictionary of scheduled jobs
        """
        jobs_info = {}
        for job in self.scheduler.get_jobs():
            jobs_info[job.id] = {
                "name": job.name,
                "next_run_time": job.next_run_time,
                "trigger": str(job.trigger),
            }
        return jobs_info
