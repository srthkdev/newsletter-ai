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
        """Get base CSS styles for all templates with enhanced formatting"""
        return f"""
        <style>
            /* Reset and base styles */
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
                line-height: 1.7; 
                color: #2d3748; 
                background-color: #f7fafc;
                margin: 0; padding: 0;
                font-size: 16px;
            }}
            .email-container {{ 
                max-width: 700px; 
                margin: 0 auto; 
                background-color: #ffffff;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border-radius: 12px;
                overflow: hidden;
            }}
            .header {{ 
                background: linear-gradient(135deg, {primary_color} 0%, {self._darken_color(primary_color)} 100%); 
                padding: 40px 30px; 
                text-align: center; 
                color: white;
            }}
            .header h1 {{ 
                font-size: 32px; 
                font-weight: 700; 
                margin-bottom: 10px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header p {{
                font-size: 16px;
                opacity: 0.9;
                margin: 0;
            }}
            .content {{ 
                padding: 40px 30px; 
            }}
            .summary-section {{
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                padding: 25px;
                border-radius: 12px;
                border-left: 5px solid {primary_color};
                margin-bottom: 30px;
            }}
            .summary-section h2 {{
                color: #1e40af;
                font-size: 20px;
                margin-bottom: 15px;
                font-weight: 600;
            }}
            .summary-section p {{
                color: #1e40af;
                font-size: 16px;
                line-height: 1.6;
                margin: 0;
            }}
            .section {{ 
                margin: 40px 0; 
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 30px;
            }}
            .section:last-child {{
                border-bottom: none;
                padding-bottom: 0;
            }}
            .section-title {{
                color: #1a202c;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 20px;
                border-bottom: 3px solid {primary_color};
                padding-bottom: 10px;
                display: inline-block;
            }}
            .article {{ 
                margin: 25px 0; 
                padding: 25px; 
                background: #f8f9fa; 
                border-radius: 12px;
                border-left: 4px solid {primary_color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            .article h3 {{
                color: #1a202c;
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 15px;
                line-height: 1.3;
            }}
            .article p {{
                color: #4a5568;
                font-size: 16px;
                line-height: 1.7;
                margin-bottom: 15px;
            }}
            .article-summary {{
                background: #e6fffa;
                padding: 15px;
                border-radius: 8px;
                border-left: 3px solid #38b2ac;
                margin: 15px 0;
                font-style: italic;
                color: #234e52;
            }}
            .read-more-link {{
                display: inline-block;
                background: {primary_color};
                color: white;
                padding: 12px 20px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin-top: 15px;
                transition: all 0.3s ease;
            }}
            .read-more-link:hover {{
                background: {self._darken_color(primary_color)};
                transform: translateY(-1px);
            }}
            .introduction, .conclusion {{
                background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
                padding: 25px;
                border-radius: 12px;
                border-left: 5px solid #f56565;
                margin: 25px 0;
            }}
            .introduction h2, .conclusion h2 {{
                color: #c53030;
                font-size: 22px;
                margin-bottom: 15px;
                font-weight: 600;
            }}
            .introduction p, .conclusion p {{
                color: #742a2a;
                font-size: 16px;
                line-height: 1.6;
                margin: 0;
            }}
            .sources-section {{
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                padding: 25px;
                border-radius: 12px;
                margin: 30px 0;
                border-left: 5px solid #22c55e;
            }}
            .sources-section h3 {{
                color: #166534;
                font-size: 20px;
                margin-bottom: 20px;
                font-weight: 600;
            }}
            .source-item {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .mindmap-section {{
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                padding: 25px;
                border-radius: 12px;
                margin: 30px 0;
                border-left: 5px solid #22c55e;
                text-align: center;
            }}
            .mindmap-section h3 {{
                color: #166534;
                font-size: 20px;
                margin-bottom: 20px;
                font-weight: 600;
            }}
            .mindmap-container {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 200px;
            }}
            .mindmap-svg {{
                max-width: 100%;
                height: auto;
                border-radius: 8px;
            }}
            .mindmap-keywords {{
                background: #f8fafc;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                text-align: left;
            }}
            .keyword-tag {{
                display: inline-block;
                background: #22c55e;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.85rem;
                margin: 2px;
                font-weight: 500;
            }}
            .source-title {{
                font-weight: 600;
                color: #1a202c;
                margin-bottom: 8px;
                font-size: 16px;
            }}
            .source-summary {{
                color: #6b7280;
                font-size: 14px;
                line-height: 1.5;
            }}
            .footer {{ 
                background-color: #2d3748; 
                color: #e2e8f0; 
                padding: 40px 30px; 
                text-align: center; 
            }}
            .footer h3 {{
                color: #f7fafc;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            .footer p {{
                font-size: 16px;
                opacity: 0.8;
                margin: 0;
            }}
            .divider {{
                width: 60px;
                height: 4px;
                background: linear-gradient(90deg, {primary_color}, {self._darken_color(primary_color)});
                margin: 30px auto;
                border-radius: 2px;
            }}
            @media only screen and (max-width: 600px) {{
                .content {{ padding: 25px 20px; }}
                .header {{ padding: 30px 20px; }}
                .header h1 {{ font-size: 28px; }}
                .section-title {{ font-size: 20px; }}
                .article h3 {{ font-size: 18px; }}
                .article {{ padding: 20px; }}
            }}
        </style>
        """

    def _daily_digest_template(
        self, 
        newsletter_data: Dict[str, Any], 
        user_preferences: Dict[str, Any]
    ) -> str:
        """Template for daily digest newsletters with enhanced formatting"""
        title = newsletter_data.get("title", "Daily Digest")
        sections = newsletter_data.get("sections", [])
        introduction = newsletter_data.get("introduction", "")
        summary = newsletter_data.get("summary", "")
        conclusion = newsletter_data.get("conclusion", "")
        sources = newsletter_data.get("sources_used", [])
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
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>📰 {title}</h1>
                    <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                </div>
                <div class="content">
                    {'<div class="introduction"><h2>Welcome!</h2><p>' + greeting + ' Here\'s your personalized newsletter with the latest insights.</p></div>' if not introduction else ''}
                    
                    {f'<div class="introduction"><h2>Introduction</h2><p>{introduction}</p></div>' if introduction else ''}
                    
                    {f'<div class="summary-section"><h2>📋 Executive Summary</h2><p>{summary}</p></div>' if summary else ''}
                    
                    <div class="divider"></div>
                    
                    {"".join([self._format_digest_section(section) for section in sections])}
                    
                    {self._format_mindmap_section(newsletter_data)}
                    
                    {f'<div class="conclusion"><h2>Conclusion</h2><p>{conclusion}</p></div>' if conclusion else ''}
                    
                    {self._format_sources_section(sources) if sources else ''}
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
                    <p>Week of {datetime.now().strftime('%B %d, %Y')}</p>
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
                    <p>{datetime.now().strftime('%I:%M %p, %B %d, %Y')}</p>
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
                    <p>Research compiled on {datetime.now().strftime('%B %d, %Y')}</p>
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
        """Format section for daily digest with enhanced display and markdown cleaning"""
        title = section.get("title", "")
        articles = section.get("articles", [])
        
        html = '<div class="section">'
        if title:
            html += f'<h2 class="section-title">{title}</h2>'
        
        for article in articles:
            if isinstance(article, dict):
                html += '<div class="article">'
                
                # Article title
                if article.get("title"):
                    html += f'<h3>{article["title"]}</h3>'
                
                # Article summary if available
                if article.get("summary"):
                    clean_summary = self._clean_markdown_for_email(article["summary"])
                    html += f'<div class="article-summary"><strong>Summary:</strong> {clean_summary}</div>'
                
                # Full article content (cleaned of markdown)
                if article.get("content"):
                    clean_content = self._clean_markdown_for_email(article["content"])
                    html += f'<p>{clean_content}</p>'
                
                # Read more link
                if article.get("url"):
                    html += f'<a href="{article["url"]}" class="read-more-link">Read Full Article →</a>'
                
                html += '</div>'
                
            elif isinstance(article, str):
                # Handle string articles from writing agent (clean markdown)
                clean_article = self._clean_markdown_for_email(article)
                html += f'<div class="article"><p>{clean_article}</p></div>'
        
        html += '</div>'
        return html
    
    def _clean_markdown_for_email(self, content: str) -> str:
        """Clean markdown content for HTML email display"""
        if not content:
            return ""
        
        import re
        
        # Remove markdown syntax and convert to HTML-safe content
        cleaned = content
        
        # Convert markdown links [text](url) to HTML links
        cleaned = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" style="color: #667eea; text-decoration: none;">\1</a>', cleaned)
        
        # Convert **bold** to <strong>
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', cleaned)
        
        # Convert *italic* to <em>
        cleaned = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', cleaned)
        
        # Handle headers by converting to appropriate HTML tags
        cleaned = re.sub(r'^### (.+)$', r'<h4 style="color: #374151; margin: 15px 0 8px 0;">\1</h4>', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^## (.+)$', r'<h3 style="color: #1f2937; margin: 20px 0 10px 0;">\1</h3>', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^# (.+)$', r'<h2 style="color: #111827; margin: 25px 0 12px 0;">\1</h2>', cleaned, flags=re.MULTILINE)
        
        # Convert line breaks to HTML
        cleaned = re.sub(r'\n\s*\n', '<br><br>', cleaned)  # Double line breaks
        cleaned = cleaned.replace('\n', '<br>')  # Single line breaks
        
        # Remove any remaining markdown artifacts
        cleaned = re.sub(r'\*{1,2}', '', cleaned)  # Remove stray asterisks
        cleaned = re.sub(r'#{1,6}\s*', '', cleaned)  # Remove stray headers
        cleaned = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', cleaned)  # Remove broken links
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

    def _format_roundup_section(self, section: Dict[str, Any]) -> str:
        """Format section for weekly roundup"""
        return self._format_digest_section(section)  # Same format for now

    def _format_breaking_section(self, section: Dict[str, Any]) -> str:
        """Format section for breaking news with markdown cleaning"""
        title = section.get("title", "")
        articles = section.get("articles", [])
        
        html = f'<div class="section">'
        if title:
            html += f'<h2 style="color: #dc2626; font-weight: bold;">{title}</h2>'
        
        for article in articles:
            if isinstance(article, dict):
                clean_content = self._clean_markdown_for_email(article.get("content", ""))
                html += f'''
                <div class="urgent-content">
                    <h3 style="color: #dc2626; margin-bottom: 10px;">🚨 {article.get("title", "")}</h3>
                    <p style="color: #1a202c; font-weight: 500;">{clean_content}</p>
                    {f'<a href="{article.get("url", "")}" style="color: #dc2626; font-weight: bold;">Full Story →</a>' if article.get("url") else ""}
                </div>
                '''
            elif isinstance(article, str):
                # Handle string articles from writing agent (clean markdown)
                clean_article = self._clean_markdown_for_email(article)
                html += f'<div class="urgent-content" style="color: #1a202c; font-weight: 500; margin: 15px 0;">{clean_article}</div>'
        
        html += '</div>'
        return html

    def _format_custom_section(self, section: Dict[str, Any]) -> str:
        """Format section for custom prompt"""
        return self._format_digest_section(section)  # Same format for now

    def _format_research_section(self, section: Dict[str, Any]) -> str:
        """Format section for research summary with markdown cleaning"""
        title = section.get("title", "")
        articles = section.get("articles", [])
        
        html = f'<div class="section">'
        if title:
            html += f'<h2 style="color: #059669; border-bottom: 2px solid #059669; padding-bottom: 8px;">{title}</h2>'
        
        for article in articles:
            if isinstance(article, dict):
                clean_content = self._clean_markdown_for_email(article.get("content", ""))
                html += f'''
                <div class="article">
                    <h3 style="color: #065f46; margin-bottom: 10px;">📊 {article.get("title", "")}</h3>
                    <p style="color: #374151;">{clean_content}</p>
                    <div class="methodology">
                        <strong>Source:</strong> {article.get("source", "Multiple sources")}
                    </div>
                    {f'<a href="{article.get("url", "")}" style="color: #059669;">View Research →</a>' if article.get("url") else ""}
                </div>
                '''
            elif isinstance(article, str):
                # Handle string articles from writing agent (clean markdown)
                clean_article = self._clean_markdown_for_email(article)
                html += f'<div class="article" style="color: #374151; margin: 15px 0;">{clean_article}</div>'
        
        html += '</div>'
        return html

    def _format_sources_section(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources section for email display"""
        if not sources:
            return ""
        
        html = '<div class="sources-section">'
        html += '<h3>📚 Sources & References</h3>'
        
        for source in sources[:8]:  # Limit to 8 sources for email
            if isinstance(source, dict):
                title = source.get("title", "Unknown Source")
                summary = source.get("summary", "")
                url = source.get("url", "")
                
                html += '<div class="source-item">'
                html += f'<div class="source-title">{title}</div>'
                if summary:
                    # Limit summary length for email
                    truncated_summary = summary[:150] + "..." if len(summary) > 150 else summary
                    html += f'<div class="source-summary">{truncated_summary}</div>'
                if url:
                    html += f'<a href="{url}" style="color: #22c55e; font-weight: 500; text-decoration: none;">Visit Source →</a>'
                html += '</div>'
        
        html += '</div>'
        return html
    
    def _format_mindmap_section(self, newsletter_data: Dict[str, Any]) -> str:
        """Format mindmap section for email with SVG and keywords"""
        mindmap_svg = newsletter_data.get("mindmap_svg", "")
        keywords_data = newsletter_data.get("keywords_data", {})
        
        if not mindmap_svg and not keywords_data:
            return ""
        
        mindmap_html = '<div class="mindmap-section"><h3>🗺️ Newsletter Keywords Map</h3>'
        
        # Add description
        mindmap_html += '<p style="color: #166534; margin-bottom: 20px;">Visual overview of key topics and themes covered in this newsletter.</p>'
        
        # Include SVG if available
        if mindmap_svg:
            # Clean SVG for email compatibility
            cleaned_svg = mindmap_svg.replace('xmlns="http://www.w3.org/2000/svg"', '')
            mindmap_html += f'''
            <div class="mindmap-container">
                {cleaned_svg}
            </div>
            '''
        
        # Add keywords summary
        if keywords_data and keywords_data.get("primary_keywords"):
            mindmap_html += '<div class="mindmap-keywords">'
            mindmap_html += '<p style="font-weight: 600; margin-bottom: 10px; color: #166534;">🔑 Key Topics:</p>'
            
            for keyword in keywords_data["primary_keywords"][:8]:  # Top 8 keywords
                mindmap_html += f'<span class="keyword-tag">{keyword}</span>'
            
            mindmap_html += '</div>'
        
        mindmap_html += '</div>'
        return mindmap_html

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