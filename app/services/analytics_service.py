"""Analytics service for tracking engagement and content performance"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics to track"""
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    CLICKS = "clicks"
    IMPRESSIONS = "impressions"
    REACH = "reach"
    ENGAGEMENT = "engagement"


class AnalyticsService:
    """Service for tracking and analyzing post performance"""

    def __init__(self):
        """Initialize analytics service"""
        self._metrics_cache = {}
        logger.info("Analytics service initialized")

    def track_metric(self, post_id: int, metric_type: MetricType, value: int, platform: str):
        """Track a metric for a post
        
        Args:
            post_id: ID of the post
            metric_type: Type of metric to track
            value: Metric value
            platform: Social media platform
        """
        key = f"{post_id}_{platform}_{metric_type}"
        if key not in self._metrics_cache:
            self._metrics_cache[key] = []
        
        self._metrics_cache[key].append({
            "value": value,
            "timestamp": datetime.utcnow(),
        })
        logger.debug(f"Tracked {metric_type} for post {post_id}: {value}")

    def update_analytics(self, post_id: int, platform: str, metrics: Dict[str, int]) -> Dict:
        """Update multiple metrics for a post
        
        Args:
            post_id: ID of the post
            platform: Social media platform
            metrics: Dictionary of metric_type: value pairs
            
        Returns:
            Updated analytics data
        """
        try:
            updated_metrics = {}
            for metric_type, value in metrics.items():
                self.track_metric(post_id, MetricType(metric_type), value, platform)
                updated_metrics[metric_type] = value
            
            logger.info(f"Updated analytics for post {post_id} on {platform}")
            return updated_metrics
            
        except Exception as e:
            logger.error(f"Error updating analytics: {str(e)}")
            raise

    def calculate_engagement_rate(self, post_id: int, platform: str) -> float:
        """Calculate engagement rate for a post
        
        Args:
            post_id: ID of the post
            platform: Social media platform
            
        Returns:
            Engagement rate as percentage
        """
        try:
            impressions_key = f"{post_id}_{platform}_{MetricType.IMPRESSIONS}"
            engagement_metrics = [MetricType.LIKES, MetricType.COMMENTS, MetricType.SHARES]
            
            if impressions_key not in self._metrics_cache or not self._metrics_cache[impressions_key]:
                return 0.0
            
            impressions = self._metrics_cache[impressions_key][-1]["value"]
            total_engagement = 0
            
            for metric in engagement_metrics:
                metric_key = f"{post_id}_{platform}_{metric}"
                if metric_key in self._metrics_cache and self._metrics_cache[metric_key]:
                    total_engagement += self._metrics_cache[metric_key][-1]["value"]
            
            if impressions == 0:
                return 0.0
            
            engagement_rate = (total_engagement / impressions) * 100
            logger.debug(f"Engagement rate for post {post_id}: {engagement_rate:.2f}%")
            return engagement_rate
            
        except Exception as e:
            logger.error(f"Error calculating engagement rate: {str(e)}")
            return 0.0

    def get_performance_summary(self, post_id: int, platform: str) -> Dict:
        """Get performance summary for a post
        
        Args:
            post_id: ID of the post
            platform: Social media platform
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            summary = {"post_id": post_id, "platform": platform}
            
            for metric in MetricType:
                key = f"{post_id}_{platform}_{metric}"
                if key in self._metrics_cache and self._metrics_cache[key]:
                    summary[metric.value] = self._metrics_cache[key][-1]["value"]
                else:
                    summary[metric.value] = 0
            
            summary["engagement_rate"] = self.calculate_engagement_rate(post_id, platform)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {str(e)}")
            return {}

    def get_trend_analysis(self, post_id: int, platform: str, metric_type: MetricType, hours: int = 24) -> Dict:
        """Get trend analysis for a metric over time
        
        Args:
            post_id: ID of the post
            platform: Social media platform
            metric_type: Type of metric to analyze
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with trend data
        """
        try:
            key = f"{post_id}_{platform}_{metric_type}"
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            if key not in self._metrics_cache:
                return {"trend": [], "average": 0, "max": 0, "min": 0}
            
            recent_data = [
                entry for entry in self._metrics_cache[key]
                if entry["timestamp"] >= cutoff_time
            ]
            
            if not recent_data:
                return {"trend": [], "average": 0, "max": 0, "min": 0}
            
            values = [entry["value"] for entry in recent_data]
            
            trend = {
                "trend": values,
                "average": sum(values) / len(values),
                "max": max(values),
                "min": min(values),
                "data_points": len(values),
            }
            
            logger.debug(f"Trend analysis for {metric_type} on post {post_id}: {trend}")
            return trend
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {str(e)}")
            return {}

    def compare_posts(self, post_ids: List[int], platform: str, metric_type: MetricType) -> Dict:
        """Compare a metric across multiple posts
        
        Args:
            post_ids: List of post IDs to compare
            platform: Social media platform
            metric_type: Type of metric to compare
            
        Returns:
            Comparison data
        """
        try:
            comparison = {}
            
            for post_id in post_ids:
                key = f"{post_id}_{platform}_{metric_type}"
                if key in self._metrics_cache and self._metrics_cache[key]:
                    comparison[post_id] = self._metrics_cache[key][-1]["value"]
                else:
                    comparison[post_id] = 0
            
            # Calculate average and best performer
            if comparison:
                comparison["average"] = sum(comparison.values()) / len(comparison)
                comparison["best_performer"] = max(comparison.items(), key=lambda x: x[1])[0]
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing posts: {str(e)}")
            return {}
