#!/usr/bin/env python3
"""
Test script for Slack integration
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.slack import slack_service
from app.core.config import settings


async def test_slack_service():
    """Test the Slack service functionality"""
    print("🧪 Testing Slack Service...")
    
    # Check if Slack tokens are configured
    if not settings.SLACK_BOT_TOKEN or not settings.SLACK_APP_TOKEN:
        print("⚠️  Slack tokens not configured. Please set SLACK_BOT_TOKEN and SLACK_APP_TOKEN in your .env file")
        return
    
    print("✅ Slack tokens found")
    
    # Test sending a simple message
    channel_id = settings.SLACK_CHANNEL_ID or "C012AB3CD"  # Default test channel ID
    message = "Hello from Newsletter AI! This is a test message."
    
    print(f"📢 Sending test message to channel {channel_id}...")
    success, delivery_info = await slack_service.send_slack_message(channel_id, message)
    
    if success:
        print("✅ Test message sent successfully!")
        print(f"Delivery info: {delivery_info}")
    else:
        print("❌ Failed to send test message")
        print(f"Error: {delivery_info.get('error')}")


async def test_newsletter_slack():
    """Test sending a newsletter via Slack"""
    print("\n🧪 Testing Newsletter Slack Delivery...")
    
    # Check if Slack tokens are configured
    if not settings.SLACK_BOT_TOKEN or not settings.SLACK_APP_TOKEN:
        print("⚠️  Slack tokens not configured. Please set SLACK_BOT_TOKEN and SLACK_APP_TOKEN in your .env file")
        return
    
    # Sample newsletter data
    newsletter_data = {
        "title": "Test Newsletter",
        "introduction": "This is a test newsletter sent via Slack.",
        "sections": [
            {
                "title": "Section 1",
                "content": "This is the content of section 1.",
                "links": [
                    {"url": "https://example.com", "title": "Example Link"}
                ]
            }
        ],
        "conclusion": "Thank you for reading this test newsletter!",
        "mindmap_markdown": "# Test Mindmap\n## Topic 1\n## Topic 2"
    }
    
    channel_id = settings.SLACK_CHANNEL_ID or "C012AB3CD"  # Default test channel ID
    subject_line = "Test Newsletter Subject"
    
    print(f"📢 Sending test newsletter to channel {channel_id}...")
    success, delivery_info = await slack_service.send_newsletter_slack(
        channel_id, newsletter_data, subject_line=subject_line
    )
    
    if success:
        print("✅ Test newsletter sent successfully!")
        print(f"Delivery info: {delivery_info}")
    else:
        print("❌ Failed to send test newsletter")
        print(f"Error: {delivery_info.get('error')}")


if __name__ == "__main__":
    print("🚀 Starting Slack Integration Tests...")
    
    # Run the tests
    asyncio.run(test_slack_service())
    asyncio.run(test_newsletter_slack())
    
    print("\n🏁 Slack Integration Tests Complete!")