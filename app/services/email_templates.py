"""
Email templates for different newsletter types and user preferences
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class NewsletterType(Enum):
    """Newsletter template types"""
    DAILY_DIGEST = "daily_digest"
    WEEKLY_ROUNDUP = "weekly_roundup"
    BREAKING_NEWS = "breaking_news"
    CUSTOM_PROMPT = "custom_prompt"
    RESEARCH_SUMMARY = "research_summary"


class EmailTemplateManager:
    """Manages email templates for different newsletter types"""

    def __init__(self):
        self.templates = {
            NewsletterType.DAILY_DIGEST: self._daily_digest_template,
            NewsletterType.WEEKLY_ROUNDUP: self._weekly_roundup_template,
            NewsletterType.BREAKING_NEWS: self._breaking_news_template,
            NewsletterType.CUSTOM_PROMPT: self._custom_prompt_template,
            NewsletterType.RESEARCH_SUMMARY: self._research_summary_template,
        }

    def get_template(
        self,
        newsletter_type: NewsletterType,
        newsletter_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get HTML template for specific newsletter type"""
        template_func = self.templates.get(newsletter_type, self._default_template)
        return template_func(newsletter_data, user_preferences or {})

    def _get_base_styles(self, primary_color: str = "#667eea") -> str:
        """Get base CSS styles for all templates"""
        return f"""
        <style>
            /* Reset and base styles */
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                line-height: 1.6; 
                color: #2d3748; 
                background-color: #f7fafc;
                margin: 0; padding: 0;
            }}
            .email-container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background-color: #ffffff;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            }}
            .header {{ 
                background: linear-gradient(135deg, {primary_color} 0%, {self._darken_color(primary_color)} 100%); 
                padding: 40px 30px; 
                text-align: center; 
                color: white;
            }}
            .header h1 {{ 
                font-size: 28px; 
                font-weight: 700; 
                margin-bottom: 8px;
            }}
            .content {{ padding: 30px; }}
            .section {{ margin: 30px 0; }}
            .article {{ 
                margin: 20px 0; 
                padding: 20px; 
                background: #f8f9fa; 
                border-radius: 10px;
                border-left: 4px solid {primary_color};
            }}
            .footer {{ 
                background-color: #2d3748; 
                color: #e2e8f0; 
                padding: 30px; 
                text-align: center; 
            }}
            @media only screen and (max-width: 600px) {{
                .content {{ padding: 20px; }}
                .header {{ padding: 30px 20px; }}
            }}
        </style>
        """

    def _daily_digest_template(
        self, 
        newsletter_data: Dict[str, Any], 
        user_preferences: Dict[str, Any]
    ) -> str:
        """Template for daily digest newsletters"""
        title = newsletter_data.get("title", "Daily Digest")
        sections = newsletter_data.get("sections", [])
        user_name = user_preferences.get("name", "")
        primary_color = self._get_topic_color(user_preferences.get("topics", []))

        greeting = f"Good morning{f', {user_name}' if user_name else ''}! ☀️"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            {self._get_base_styles(primary_color)}
            <style>
                .digest-intro {{
                    background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
                    padding: 25px;
                    border-radius: 12px;
                    border-left: 5px solid #f56565;
                    margin: 20px 0;
                }}
                .time-badge {{
                    background: {primary_color};
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>📰 {title}</h1>
                    <div class="time-badge">{datetime.now().strftime("%A, %B %d")}</div>
                </div>
                <div class="content">
                    <div class="digest-intro">
                        <h2>{greeting}</h2>
                        <p>Here's what's happening in your world today. We've curated the most important stories based on your interests.</p>
                    </div>
                    {"".join([self._format_digest_section(section) for section in sections])}
                </div>
                <div class="footer">
                    <h3>Newsletter AI</h3>
                    <p>Your daily dose of personalized insights</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _weekly_roundup_template(
        self, 
        newsletter_data: Dict[str, Any], 
        user_preferences: Dict[str, Any]
    ) -> str:
        """Template for weekly roundup newsletters"""
        title = newsletter_data.get("title", "Weekly Roundup")
        sections = newsletter_data.get("sections", [])
        user_name = user_preferences.get("name", "")
        primary_color = self._get_topic_color(user_preferences.get("topics", []))

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            {self._get_base_styles(primary_color)}
            <style>
                .week-header {{
                    background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%);
                    padding: 25px;
                    border-radius: 12px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .stat-card {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    border: 2px solid #e2e8f0;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>📊 {title}</h1>
                    <p>Week of {datetime.now().strftime("%B %d, %Y")}</p>
                </div>
                <div class="content">
                    <div class="week-header">
                        <h2>Week in Review{f' for {user_name}' if user_name else ''}</h2>
                        <p>The most important stories and trends from the past week</p>
                    </div>
                    {"".join([self._format_roundup_section(section) for section in sections])}
                </div>
                <div class="footer">
                    <h3>Newsletter AI</h3>
                    <p>Your weekly intelligence briefing</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _breaking_news_template(
        self, 
        newsletter_data: Dict[str, Any], 
        user_preferences: Dict[str, Any]
    ) -> str:
        """Template for breaking news newsletters"""
        title = newsletter_data.get("title", "Breaking News")
        sections = newsletter_data.get("sections", [])
        primary_color = "#dc2626"  # Red for urgency

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            {self._get_base_styles(primary_color)}
            <style>
                .breaking-banner {{
                    background: linear-gradient(45deg, #dc2626, #ef4444);
                    color: white;
                    padding: 15px;
                    text-align: center;
                    font-weight: bold;
                    animation: pulse 2s infinite;
                }}
                .urgent-content {{
                    border: 3px solid #dc2626;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                    background: #fef2f2;
                }}
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.8; }}
                    100% {{ opacity: 1; }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="breaking-banner">
                    🚨 BREAKING NEWS ALERT 🚨
                </div>
                <div class="header">
                    <h1>⚡ {title}</h1>
                    <p>{datetime.now().strftime("%I:%M %p, %B %d, %Y")}</p>
                </div>
                <div class="content">
                    {"".join([self._format_breaking_section(section) for section in sections])}
                </div>
                <div class="footer">
                    <h3>Newsletter AI</h3>
                    <p>Breaking news delivered instantly</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _custom_prompt_template(
        self, 
        newsletter_data: Dict[str, Any], 
        user_preferences: Dict[str, Any]
    ) -> str:
        """Template for custom prompt newsletters"""
        title = newsletter_data.get("title", "Custom Newsletter")
        custom_prompt = newsletter_data.get("custom_prompt", "")
        sections = newsletter_data.get("sections", [])
        primary_color = self._get_topic_color(user_preferences.get("topics", []))

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            {self._get_base_styles(primary_color)}
            <style>
                .prompt-display {{
                    background: linear-gradient(135deg, #f0f9ff 0%, #dbeafe 100%);
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid #3b82f6;
                    margin: 20px 0;
                    font-style: italic;
                }}
                .custom-badge {{
                    background: #8b5cf6;
                    color: white;
                    padding: 5px 12px;
                    border-radius: 15px;
                    font-size: 12px;
                    display: inline-block;
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>✨ {title}</h1>
                    <div class="custom-badge">Custom Request</div>
                </div>
                <div class="content">
                    {f'<div class="prompt-display"><strong>Your request:</strong> "{custom_prompt}"</div>' if custom_prompt else ''}
                    {"".join([self._format_custom_section(section) for section in sections])}
                </div>
                <div class="footer">
                    <h3>Newsletter AI</h3>
                    <p>Personalized content, exactly as you requested</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _research_summary_template(
        self, 
        newsletter_data: Dict[str, Any], 
        user_preferences: Dict[str, Any]
    ) -> str:
        """Template for research summary newsletters"""
        title = newsletter_data.get("title", "Research Summary")
        sections = newsletter_data.get("sections", [])
        primary_color = "#059669"  # Green for research

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            {self._get_base_styles(primary_color)}
            <style>
                .research-header {{
                    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                    padding: 25px;
                    border-radius: 12px;
                    border-left: 5px solid #059669;
                }}
                .methodology {{
                    background: #f8fafc;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    font-size: 14px;
                    color: #64748b;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🔬 {title}</h1>
                    <p>Research compiled on {datetime.now().strftime("%B %d, %Y")}</p>
                </div>
                <div class="content">
                    <div class="research-header">
                        <h2>Research Findings</h2>
                        <p>Comprehensive analysis based on the latest available data and sources</p>
                    </div>
                    {"".join([self._format_research_section(section) for section in sections])}
                </div>
                <div class="footer">
                    <h3>Newsletter AI</h3>
                    <p>Evidence-based insights and analysis</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _default_template(
        self, 
        newsletter_data: Dict[str, Any], 
        user_preferences: Dict[str, Any]
    ) -> str:
        """Default template fallback"""
        return self._daily_digest_template(newsletter_data, user_preferences)

    # Section formatting methods
    def _format_digest_section(self, section: Dict[str, Any]) -> str:
        """Format section for daily digest"""
        title = section.get("title", "")
        articles = section.get("articles", [])
        
        html = f'<div class="section">'
        if title:
            html += f'<h2 style="color: #1a202c; border-bottom: 2px solid #667eea; padding-bottom: 8px;">{title}</h2>'
        
        for article in articles:
            if isinstance(article, dict):
                html += f'''
                <div class="article">
                    <h3 style="color: #2d3748; margin-bottom: 10px;">{article.get("title", "")}</h3>
                    <p style="color: #4a5568;">{article.get("content", "")[:200]}...</p>
                    {f'<a href="{article.get("url", "")}" style="color: #667eea;">Read more →</a>' if article.get("url") else ""}
                </div>
                '''
        
        html += '</div>'
        return html

    def _format_roundup_section(self, section: Dict[str, Any]) -> str:
        """Format section for weekly roundup"""
        return self._format_digest_section(section)  # Same format for now

    def _format_breaking_section(self, section: Dict[str, Any]) -> str:
        """Format section for breaking news"""
        title = section.get("title", "")
        articles = section.get("articles", [])
        
        html = f'<div class="section">'
        if title:
            html += f'<h2 style="color: #dc2626; font-weight: bold;">{title}</h2>'
        
        for article in articles:
            if isinstance(article, dict):
                html += f'''
                <div class="urgent-content">
                    <h3 style="color: #dc2626; margin-bottom: 10px;">🚨 {article.get("title", "")}</h3>
                    <p style="color: #1a202c; font-weight: 500;">{article.get("content", "")}</p>
                    {f'<a href="{article.get("url", "")}" style="color: #dc2626; font-weight: bold;">Full Story →</a>' if article.get("url") else ""}
                </div>
                '''
        
        html += '</div>'
        return html

    def _format_custom_section(self, section: Dict[str, Any]) -> str:
        """Format section for custom prompt"""
        return self._format_digest_section(section)  # Same format for now

    def _format_research_section(self, section: Dict[str, Any]) -> str:
        """Format section for research summary"""
        title = section.get("title", "")
        articles = section.get("articles", [])
        
        html = f'<div class="section">'
        if title:
            html += f'<h2 style="color: #059669; border-bottom: 2px solid #059669; padding-bottom: 8px;">{title}</h2>'
        
        for article in articles:
            if isinstance(article, dict):
                html += f'''
                <div class="article">
                    <h3 style="color: #065f46; margin-bottom: 10px;">📊 {article.get("title", "")}</h3>
                    <p style="color: #374151;">{article.get("content", "")}</p>
                    <div class="methodology">
                        <strong>Source:</strong> {article.get("source", "Multiple sources")}
                    </div>
                    {f'<a href="{article.get("url", "")}" style="color: #059669;">View Research →</a>' if article.get("url") else ""}
                </div>
                '''
        
        html += '</div>'
        return html

    def _get_topic_color(self, topics: List[str]) -> str:
        """Get primary color based on topics"""
        topic_colors = {
            "tech": "#667eea",
            "business": "#f093fb", 
            "science": "#4facfe",
            "health": "#43e97b",
            "finance": "#fa709a",
            "sports": "#ffecd2",
            "entertainment": "#a8edea"
        }
        
        if topics:
            return topic_colors.get(topics[0].lower(), "#667eea")
        return "#667eea"

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


# Global template manager instance
template_manager = EmailTemplateManager()