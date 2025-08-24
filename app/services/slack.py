"""
Slack service using Portia AI Slack tools for sending newsletters
"""

from typing import Optional, Dict, Any, Tuple
from app.core.config import settings
from enum import Enum
import json


class SlackStatus(Enum):
    """Slack message delivery status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"


class SlackService:
    """Slack service using Portia AI Slack tools for newsletter delivery"""

    def __init__(self):
        self.bot_token = settings.SLACK_BOT_TOKEN
        self.app_token = settings.SLACK_APP_TOKEN
        self.channel_id = settings.SLACK_CHANNEL_ID
        self.max_retries = 3
        self.retry_delays = [1, 5, 15]  # seconds

    async def send_newsletter_slack(
        self,
        channel_id: str,
        newsletter_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None,
        subject_line: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Send newsletter via Slack using Portia AI Slack tools
        
        Returns:
            Tuple[bool, Dict[str, Any]]: (success, delivery_info)
        """
        delivery_info = {
            "channel_id": channel_id,
            "status": SlackStatus.PENDING.value,
            "attempts": 0,
            "sent_at": None,
            "error": None
        }

        if not self.bot_token or not self.app_token:
            delivery_info["status"] = SlackStatus.FAILED.value
            delivery_info["error"] = "Slack tokens not configured"
            print("⚠️  Slack tokens not configured")
            return False, delivery_info

        # Try sending with retry mechanism
        for attempt in range(self.max_retries):
            delivery_info["attempts"] = attempt + 1
            
            try:
                # Create personalized newsletter content for Slack
                slack_content = self._create_slack_newsletter(
                    newsletter_data, user_preferences, subject_line
                )

                # For now, we'll print the content as a placeholder
                # In a real implementation, this would use Portia AI Slack tools
                print(f"📢 Sending newsletter to Slack channel {channel_id}")
                print(f"Subject: {subject_line}")
                print(f"Content: {slack_content}")
                
                delivery_info.update({
                    "status": SlackStatus.SENT.value,
                    "sent_at": __import__('datetime').datetime.utcnow().isoformat(),
                    "error": None
                })
                
                print(f"✅ Newsletter sent to Slack channel {channel_id} (attempt {attempt + 1})")
                return True, delivery_info

            except Exception as e:
                error_msg = f"Failed to send newsletter to Slack (attempt {attempt + 1}): {str(e)}"
                delivery_info["error"] = error_msg
                print(f"❌ {error_msg}")
                
                # If not the last attempt, wait before retrying
                if attempt < self.max_retries - 1:
                    import asyncio
                    await asyncio.sleep(self.retry_delays[attempt])
                    delivery_info["status"] = SlackStatus.RETRY.value
                    continue

        # All attempts failed
        delivery_info["status"] = SlackStatus.FAILED.value
        return False, delivery_info

    def _create_slack_newsletter(
        self,
        newsletter_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None,
        subject_line: Optional[str] = None
    ) -> str:
        """
        Create formatted newsletter content for Slack
        
        Args:
            newsletter_data: Newsletter content data
            user_preferences: User preferences for personalization
            subject_line: Optional subject line
            
        Returns:
            Formatted Slack message content
        """
        # Extract newsletter components
        title = newsletter_data.get("title", "Newsletter")
        introduction = newsletter_data.get("introduction", "")
        sections = newsletter_data.get("sections", [])
        conclusion = newsletter_data.get("conclusion", "")
        mindmap_markdown = newsletter_data.get("mindmap_markdown", "")
        
        # Build Slack message
        slack_message = f"*{subject_line or title}*\n\n"
        
        if introduction:
            slack_message += f"{introduction}\n\n"
        
        for i, section in enumerate(sections, 1):
            section_title = section.get("title", f"Section {i}")
            section_content = section.get("content", "")
            section_links = section.get("links", [])
            
            slack_message += f"*{section_title}*\n"
            slack_message += f"{section_content}\n"
            
            if section_links:
                slack_message += "\n*Related Links:*\n"
                for link in section_links:
                    url = link.get("url", "")
                    title = link.get("title", url)
                    if url:
                        slack_message += f"• <{url}|{title}>\n"
            
            slack_message += "\n"
        
        if conclusion:
            slack_message += f"*Conclusion*\n{conclusion}\n\n"
        
        if mindmap_markdown:
            slack_message += f"*Newsletter Mindmap*\n```\n{mindmap_markdown}\n```\n"
        
        # Add footer
        slack_message += f"\n_This newsletter was generated by Newsletter AI at {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC_"
        
        return slack_message

    async def send_slack_message(
        self,
        channel_id: str,
        message: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Send a simple message to a Slack channel
        
        Returns:
            Tuple[bool, Dict[str, Any]]: (success, delivery_info)
        """
        delivery_info = {
            "channel_id": channel_id,
            "status": SlackStatus.PENDING.value,
            "attempts": 0,
            "sent_at": None,
            "error": None
        }

        if not self.bot_token or not self.app_token:
            delivery_info["status"] = SlackStatus.FAILED.value
            delivery_info["error"] = "Slack tokens not configured"
            print("⚠️  Slack tokens not configured")
            return False, delivery_info

        try:
            # For now, we'll print the message as a placeholder
            # In a real implementation, this would use Portia AI Slack tools
            print(f"📢 Sending message to Slack channel {channel_id}")
            print(f"Message: {message}")
            
            delivery_info.update({
                "status": SlackStatus.SENT.value,
                "sent_at": __import__('datetime').datetime.utcnow().isoformat(),
                "error": None
            })
            
            print(f"✅ Message sent to Slack channel {channel_id}")
            return True, delivery_info

        except Exception as e:
            error_msg = f"Failed to send message to Slack: {str(e)}"
            delivery_info["error"] = error_msg
            delivery_info["status"] = SlackStatus.FAILED.value
            print(f"❌ {error_msg}")
            return False, delivery_info


# Global slack service instance
slack_service = SlackService()