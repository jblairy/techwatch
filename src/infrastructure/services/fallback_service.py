"""
Fallback verification service - Infrastructure Layer
Hexagonal Architecture DDD
"""
from datetime import date, timedelta
from typing import List, Dict
import logging

from ...domain.entities.post import Post
from ...domain.value_objects.date_range import DateRange

logger = logging.getLogger(__name__)


class FallbackVerificationService:
    """Fallback verification service to detect HTML parsing issues - Infrastructure Layer"""

    def __init__(self):
        pass

    def check_for_missed_posts(self, crawler, date_range: DateRange, found_posts: List[Post]) -> Dict[str, any]:
        """
        Check if there are posts that might have been missed due to parsing issues.

        Args:
            crawler: The crawler to verify
            date_range: The searched date range
            found_posts: The posts found in the range

        Returns:
            Dict containing the fallback verification results
        """
        result = {
            'has_alert': False,
            'alert_message': '',
            'fallback_posts': [],
            'confidence_score': 1.0
        }

        try:
            # Verification 1: No posts found in recent period
            if not found_posts and date_range.contains(date.today()):
                result['has_alert'] = True
                result['alert_message'] = f"⚠️ {crawler.source_name}: No posts found today. Possible parsing issue."
                result['confidence_score'] = 0.3
                return result

            # Verification 2: Very few posts over extended period
            if len(found_posts) <= 1 and date_range.duration_days() >= 7:
                result['has_alert'] = True
                result['alert_message'] = f"⚠️ {crawler.source_name}: Only {len(found_posts)} post(s) found over {date_range.duration_days()} days. Check site structure."
                result['confidence_score'] = 0.5

            # Verification 3: No recent posts but period includes recent days
            if found_posts:
                most_recent = max(post.date for post in found_posts if post.date)
                days_since_last = (date.today() - most_recent).days

                if days_since_last > 3 and date_range.contains(date.today()):
                    result['has_alert'] = True
                    result['alert_message'] = f"⚠️ {crawler.source_name}: Most recent post is {days_since_last} days old. Possible recent issue."
                    result['confidence_score'] = 0.7

            # Verification 4: Try fallback method to verify
            try:
                fallback_posts = crawler.fetch_recent_posts_for_fallback()
                if fallback_posts and not found_posts:
                    result['has_alert'] = True
                    result['alert_message'] = f"⚠️ {crawler.source_name}: Found {len(fallback_posts)} posts via fallback but none in date range. Check date parsing."
                    result['fallback_posts'] = fallback_posts[:3]  # Keep only first 3 for display
                    result['confidence_score'] = 0.2

                elif len(fallback_posts) > len(found_posts) * 3:
                    result['has_alert'] = True
                    result['alert_message'] = f"⚠️ {crawler.source_name}: Significant difference between fallback ({len(fallback_posts)}) and filtered posts ({len(found_posts)}). Check filtering logic."
                    result['confidence_score'] = 0.4

            except Exception as fallback_error:
                logger.warning(f"Fallback verification failed for {crawler.source_name}: {fallback_error}")

        except Exception as e:
            logger.error(f"Error during fallback verification for {crawler.source_name}: {e}")
            result['has_alert'] = True
            result['alert_message'] = f"⚠️ {crawler.source_name}: Error during fallback verification."
            result['confidence_score'] = 0.0

        return result

    def suggest_debugging_steps(self, crawler_name: str) -> List[str]:
        """Suggest debugging steps for a problematic crawler"""
        return [
            f"1. Check if {crawler_name} has changed its HTML structure",
            f"2. Test {crawler_name} URL manually",
            f"3. Verify the CSS selectors used",
            f"4. Check logs for HTTP errors",
            f"5. Check if the site uses JavaScript to load content"
        ]

    def analyze_parsing_quality(self, crawler, posts: List[Post]) -> Dict[str, any]:
        """
        Analyze the quality of parsed posts to detect potential issues.

        Args:
            crawler: The crawler used
            posts: List of parsed posts

        Returns:
            Dict containing quality analysis results
        """
        analysis = {
            'quality_score': 1.0,
            'issues': [],
            'recommendations': []
        }

        if not posts:
            analysis['quality_score'] = 0.0
            analysis['issues'].append("No posts found")
            analysis['recommendations'].append("Check if the source is accessible and has recent content")
            return analysis

        # Check for posts without dates
        posts_without_date = [p for p in posts if p.date is None]
        if posts_without_date:
            ratio = len(posts_without_date) / len(posts)
            analysis['quality_score'] -= ratio * 0.5
            analysis['issues'].append(f"{len(posts_without_date)}/{len(posts)} posts without date")
            analysis['recommendations'].append("Review date extraction logic")

        # Check for posts without proper URLs
        posts_without_url = [p for p in posts if not p.url or not p.url.startswith('http')]
        if posts_without_url:
            ratio = len(posts_without_url) / len(posts)
            analysis['quality_score'] -= ratio * 0.3
            analysis['issues'].append(f"{len(posts_without_url)}/{len(posts)} posts with invalid URLs")
            analysis['recommendations'].append("Review URL extraction and resolution logic")

        # Check for very short titles (potential parsing issues)
        short_titles = [p for p in posts if len(p.title or '') < 10]
        if short_titles:
            ratio = len(short_titles) / len(posts)
            analysis['quality_score'] -= ratio * 0.2
            analysis['issues'].append(f"{len(short_titles)}/{len(posts)} posts with very short titles")
            analysis['recommendations'].append("Review title extraction logic")

        # Ensure score doesn't go below 0
        analysis['quality_score'] = max(0.0, analysis['quality_score'])

        return analysis
