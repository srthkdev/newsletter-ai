"""
Newsletter Writing Agent using Portia AI framework with RAG integration
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from portia import Plan, PlanBuilder
from app.portia.base_agent import BaseNewsletterAgent
from app.services.memory import memory_service
from app.services.embeddings import embedding_service
from app.services.rag_system import rag_system


class NewsletterWritingAgent(BaseNewsletterAgent):
    """Portia agent for generating engaging blog-style newsletter content"""

    def __init__(self):
        super().__init__("writing_agent")
        self.memory = memory_service

    async def create_plan(self, context: Dict[str, Any]) -> Plan:
        """Create writing plan using Portia PlanBuilder"""
        user_id = context.get("user_id")
        articles = context.get("articles", [])
        user_preferences = context.get("user_preferences", {})
        custom_prompt = context.get("custom_prompt")

        tone = user_preferences.get("tone", "professional")
        topics = user_preferences.get("topics", [])

        builder = PlanBuilder()

        # Step 1: Analyze content and user preferences
        builder.add_step(
            "analyze_content_and_preferences",
            f"""
            Analyze the provided content and user preferences:
            - Number of articles: {len(articles)}
            - User preferred tone: {tone}
            - User topics: {topics}
            - Custom prompt: {custom_prompt or "None"}
            
            Determine the best structure and approach for the newsletter based on:
            1. Content themes and topics
            2. User's preferred tone and style
            3. Any custom requirements from the prompt
            
            Create an outline for a blog-style newsletter.
            """,
        )

        # Step 2: Retrieve user context from RAG/memory
        builder.add_step(
            "retrieve_user_context",
            f"""
            Retrieve relevant context from the user's history and preferences:
            - Previous newsletter topics and themes
            - Reading patterns and engagement data
            - Personalization insights
            
            Use this context to personalize the newsletter content and avoid repetition.
            User ID: {user_id}
            """,
        )

        # Step 3: Generate newsletter introduction
        builder.add_step(
            "generate_introduction",
            f"""
            Write an engaging introduction for the newsletter that:
            1. Welcomes the reader with the appropriate tone ({tone})
            2. Previews the main topics covered
            3. Connects to current events or trends
            4. Sets the right expectation for the content
            
            Keep it concise but engaging (2-3 paragraphs maximum).
            """,
        )

        # Step 4: Create main content sections
        builder.add_step(
            "create_main_sections",
            f"""
            Create the main content sections of the newsletter:
            1. Group related articles into thematic sections
            2. Write compelling section headers
            3. Summarize key articles with insights and takeaways
            4. Add personal commentary or analysis where appropriate
            5. Use the {tone} tone throughout
            
            Structure as a blog post with clear sections and good flow.
            """,
        )

        # Step 5: Generate conclusion and call-to-action
        builder.add_step(
            "generate_conclusion",
            """
            Write a strong conclusion that:
            1. Summarizes the key themes and insights
            2. Provides actionable takeaways for readers
            3. Includes a call-to-action (feedback, sharing, etc.)
            4. Maintains the established tone
            
            End on a positive, forward-looking note.
            """,
        )

        # Step 6: Format for email and create subject lines
        builder.add_step(
            "format_and_finalize",
            """
            Finalize the newsletter:
            1. Format the content for email delivery (HTML structure)
            2. Generate 3-5 compelling subject line options
            3. Create a plain text version
            4. Add proper email formatting and styling
            5. Ensure mobile-friendly layout
            
            The final output should be ready for email delivery.
            """,
        )

        return builder.build()

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific writing task"""
        if task == "generate_newsletter":
            return await self._generate_newsletter(context)
        elif task == "create_subject_lines":
            return await self._create_subject_lines(context)
        elif task == "format_for_email":
            return await self._format_for_email(context)
        else:
            return await self._execute_full_writing(context)

    async def _generate_newsletter(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete newsletter content with RAG integration"""
        try:
            articles = context.get("articles", [])
            user_preferences = context.get("user_preferences", {})
            custom_prompt = context.get("custom_prompt")
            user_id = context.get("user_id")

            if not articles:
                return {
                    "success": False,
                    "error": "No articles provided for newsletter generation",
                    "content": "",
                }

            # Get user context from memory
            user_context = await self._get_user_writing_context(user_id)

            # Enhance with RAG context
            rag_enhancement = await self._enhance_content_with_rag(
                user_id, articles, user_preferences
            )

            # Generate newsletter structure with RAG context
            newsletter_structure = await self._create_newsletter_structure(
                articles, user_preferences, custom_prompt, user_context, rag_enhancement
            )

            # Generate content for each section with RAG context
            newsletter_content = await self._generate_content_sections(
                newsletter_structure, user_preferences, user_context, rag_enhancement
            )

            # Create final newsletter
            word_count = self._count_words(newsletter_content)
            estimated_read_time = self._estimate_read_time(newsletter_content)

            final_newsletter = {
                "title": newsletter_structure.get(
                    "title", "Your Personalized Newsletter"
                ),
                "introduction": newsletter_content.get("introduction", ""),
                "sections": newsletter_content.get("sections", []),
                "conclusion": newsletter_content.get("conclusion", ""),
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "article_count": len(articles),
                    "word_count": word_count,
                    "estimated_read_time": estimated_read_time,
                    "user_preferences": user_preferences,
                    "custom_prompt": custom_prompt,
                    "rag_context_used": rag_enhancement.get("rag_available", False),
                    "personalization_level": rag_enhancement.get(
                        "recommendations", {}
                    ).get("personalization_level", "basic"),
                },
            }

            # Apply RAG-based content strategy enhancements
            final_newsletter = await self._apply_rag_content_strategy(
                final_newsletter, rag_enhancement
            )

            return {
                "success": True,
                "newsletter": final_newsletter,
                "word_count": word_count,
                "estimated_read_time": estimated_read_time,
                "rag_context": rag_enhancement,
            }

        except Exception as e:
            return await self.handle_error(e, context)

    async def _create_subject_lines(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multiple subject line options"""
        try:
            newsletter_content = context.get("newsletter_content", "")
            articles = context.get("articles", [])
            user_preferences = context.get("user_preferences", {})

            # Extract key themes from articles
            themes = self._extract_themes(articles)
            tone = user_preferences.get("tone", "professional")

            # Generate subject lines based on different strategies
            subject_lines = []

            # Strategy 1: Topic-focused
            if themes:
                main_theme = themes[0]
                subject_lines.append(f"📊 This Week in {main_theme.title()}")
                subject_lines.append(
                    f"Latest {main_theme.title()} Updates You Need to Know"
                )

            # Strategy 2: Benefit-focused
            subject_lines.append("🚀 Your Weekly Dose of Innovation")
            subject_lines.append("Key Insights to Keep You Ahead")

            # Strategy 3: Curiosity-driven
            subject_lines.append("What Everyone's Talking About This Week")
            subject_lines.append("The Stories That Matter Right Now")

            # Strategy 4: Personal/Direct
            if tone == "casual":
                subject_lines.append("Hey! Here's what caught my attention")
                subject_lines.append("Your personalized news digest is ready")
            else:
                subject_lines.append("Your Curated Newsletter Has Arrived")
                subject_lines.append("This Week's Essential Reading")

            return {
                "success": True,
                "subject_lines": subject_lines[:5],  # Return top 5
                "themes": themes,
                "tone": tone,
            }

        except Exception as e:
            return await self.handle_error(e, context)

    async def _format_for_email(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Format newsletter content for email delivery with blog-style templates"""
        try:
            newsletter = context.get("newsletter", {})

            if not newsletter:
                return {
                    "success": False,
                    "error": "No newsletter content provided for formatting",
                }

            # Generate blog-style templates
            templates = self._create_blog_style_template(newsletter, "modern")

            return {
                "success": True,
                "html_content": templates["html"],
                "plain_text": templates["plain_text"],
                "markdown_content": templates["markdown"],
                "newsletter_data": newsletter,
                "template_type": "blog_style_modern",
            }

        except Exception as e:
            return await self.handle_error(e, context)

    async def _execute_full_writing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full writing workflow using Portia plan"""
        try:
            # Create and execute writing plan
            plan = await self.create_plan(context)
            result = await self.run_plan(plan)

            if not result["success"]:
                return result

            # Store newsletter in user's history and embed for RAG
            user_id = context.get("user_id")
            if user_id and result.get("result"):
                newsletter_id = f"newsletter_{datetime.utcnow().isoformat()}"
                newsletter_data = {
                    "id": newsletter_id,
                    "content": result["result"],
                    "generated_at": datetime.utcnow().isoformat(),
                    "articles_used": len(context.get("articles", [])),
                    "user_preferences": context.get("user_preferences", {}),
                    "custom_prompt": context.get("custom_prompt"),
                }

                # Store in memory
                await self.memory.store_newsletter_history(
                    user_id=user_id, newsletter_data=newsletter_data
                )

                # Embed newsletter content for RAG using comprehensive system
                await rag_system.embed_and_store_newsletter(
                    newsletter_id=newsletter_id,
                    user_id=user_id,
                    newsletter_data=newsletter_data,
                )

            return result

        except Exception as e:
            return await self.handle_error(e, context)

    async def _get_user_writing_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's writing context from memory and RAG"""
        if not user_id:
            return {}

        # Get user preferences
        preferences = await self.memory.get_user_preferences(user_id)

        # Get reading patterns
        reading_patterns = await self.memory.get_reading_patterns(user_id)

        # Get recent newsletter history
        recent_newsletters = await self.memory.get_newsletter_history(user_id, limit=5)

        # Get engagement metrics for personalization
        engagement_metrics = await self.memory.get_engagement_metrics(user_id)

        return {
            "preferences": preferences or {},
            "reading_patterns": reading_patterns or {},
            "recent_newsletters": recent_newsletters,
            "engagement_metrics": engagement_metrics or {},
            "personalization_available": bool(preferences or reading_patterns),
        }

    async def _create_newsletter_structure(
        self,
        articles: List[Dict[str, Any]],
        user_preferences: Dict[str, Any],
        custom_prompt: Optional[str],
        user_context: Dict[str, Any],
        rag_enhancement: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create the structure for the newsletter"""

        # Group articles by topic/theme
        grouped_articles = self._group_articles_by_theme(articles)

        # Determine newsletter title
        if custom_prompt:
            title = self._generate_title_from_prompt(custom_prompt)
        else:
            main_topics = list(grouped_articles.keys())[:2]
            if main_topics:
                title = f"Your Weekly Update: {' & '.join(main_topics).title()}"
            else:
                title = "Your Personalized Newsletter"

        # Create section structure
        sections = []
        for theme, theme_articles in grouped_articles.items():
            sections.append(
                {
                    "title": theme.title(),
                    "articles": theme_articles[:3],  # Limit to 3 articles per section
                    "type": "content_section",
                }
            )

        return {
            "title": title,
            "sections": sections,
            "total_articles": len(articles),
            "themes": list(grouped_articles.keys()),
        }

    async def _generate_content_sections(
        self,
        structure: Dict[str, Any],
        user_preferences: Dict[str, Any],
        user_context: Dict[str, Any],
        rag_enhancement: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate content for each section of the newsletter"""

        tone = user_preferences.get("tone", "professional")

        # Generate introduction with RAG context
        introduction = self._generate_introduction(
            structure, tone, user_context, rag_enhancement
        )

        # Generate sections
        sections = []
        for section in structure.get("sections", []):
            section_content = self._generate_section_content(
                section, tone, rag_enhancement
            )
            sections.append(section_content)

        # Generate conclusion
        conclusion = self._generate_conclusion(structure, tone)

        return {
            "introduction": introduction,
            "sections": sections,
            "conclusion": conclusion,
        }

    def _group_articles_by_theme(
        self, articles: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group articles by theme/topic"""
        grouped = {}

        for article in articles:
            # Use the topic from research agent or extract from title/content
            topic = article.get("topic", "general")

            if topic not in grouped:
                grouped[topic] = []

            grouped[topic].append(article)

        # Sort groups by number of articles (most articles first)
        return dict(sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True))

    def _generate_title_from_prompt(self, custom_prompt: str) -> str:
        """Generate newsletter title from custom prompt"""
        # Simple title generation - could be enhanced with NLP
        prompt_lower = custom_prompt.lower()

        if "weekly" in prompt_lower:
            return f"Weekly Update: {custom_prompt[:50]}..."
        elif "daily" in prompt_lower:
            return f"Daily Brief: {custom_prompt[:50]}..."
        else:
            return f"Custom Newsletter: {custom_prompt[:50]}..."

    def _generate_introduction(
        self,
        structure: Dict[str, Any],
        tone: str,
        user_context: Dict[str, Any],
        rag_enhancement: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate newsletter introduction with enhanced RAG personalization"""

        themes = structure.get("themes", [])
        article_count = structure.get("total_articles", 0)

        if tone == "casual":
            greeting = "Hey there!"
            style = "friendly and conversational"
        elif tone == "technical":
            greeting = "Hello,"
            style = "detailed and analytical"
        else:  # professional
            greeting = "Good morning,"
            style = "professional and informative"

        # Enhanced personalization with RAG context
        personalization_note = ""
        reading_insights = ""

        if rag_enhancement and rag_enhancement.get("rag_available"):
            similar_count = len(rag_enhancement.get("similar_content", []))
            personalization_level = rag_enhancement.get("recommendations", {}).get(
                "personalization_level", "basic"
            )

            # Add reading patterns insights
            reading_patterns = rag_enhancement.get("reading_patterns")
            if reading_patterns:
                preferred_topics = reading_patterns.get("preferred_topics", [])
                if preferred_topics and any(
                    topic in themes for topic in preferred_topics
                ):
                    matching_topics = [
                        topic for topic in preferred_topics if topic in themes
                    ]
                    reading_insights = f" I noticed you particularly enjoy {', '.join(matching_topics[:2])}, so I've included extra coverage on those topics."

            if similar_count > 0:
                if personalization_level == "high":
                    personalization_note = f" Based on your reading history of {similar_count} similar newsletters, I've carefully tailored this content to match your interests.{reading_insights}"
                else:
                    personalization_note = f" I've personalized this content based on your preferences and reading patterns.{reading_insights}"

        # Add engagement-based personalization
        engagement_metrics = (
            rag_enhancement.get("engagement_metrics") if rag_enhancement else None
        )
        engagement_note = ""
        if engagement_metrics:
            total_opens = engagement_metrics.get("total_opens", 0)
            if total_opens > 5:
                engagement_note = f" Thanks for being such an engaged reader - this is newsletter #{total_opens + 1} for you!"

        intro_template = f"""
{greeting}

Welcome to your personalized newsletter! I've curated {article_count} interesting articles covering {", ".join(themes[:3]) if themes else "various topics"} that align with your interests.{personalization_note}{engagement_note}

This week's highlights include some fascinating developments that I think you'll find valuable. Let's dive in!
        """.strip()

        return intro_template

    def _generate_section_content(
        self,
        section: Dict[str, Any],
        tone: str,
        rag_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate content for a newsletter section with RAG-enhanced insights"""

        section_title = section.get("title", "Updates")
        articles = section.get("articles", [])

        # Create section introduction with RAG insights
        section_intro = f"## {section_title}\n\n"

        # Add RAG-based section insights
        if rag_context and rag_context.get("rag_available"):
            similar_content = rag_context.get("similar_content", [])
            topic_suggestions = rag_context.get("recommendations", {}).get(
                "topic_suggestions", []
            )

            # Check if this section topic has been covered before
            relevant_history = [
                content
                for content in similar_content
                if section_title.lower() in content.get("content_preview", "").lower()
            ]

            if relevant_history and tone == "casual":
                section_intro += f"You've shown interest in {section_title.lower()} before, so here's what's new:\n\n"
            elif relevant_history and tone == "professional":
                section_intro += f"Building on your previous interest in {section_title.lower()}, here are the latest developments:\n\n"

        # Process each article with enhanced summaries
        article_summaries = []
        for i, article in enumerate(articles):
            title = article.get("title", "Untitled")
            url = article.get("url", "")
            content = article.get("content", "")

            # Create more engaging summary based on tone
            if tone == "casual":
                summary_intro = "🔍 " if i == 0 else "📌 "
            elif tone == "technical":
                summary_intro = f"**Analysis {i + 1}:** "
            else:
                summary_intro = f"**Key Insight {i + 1}:** "

            # Truncate content intelligently (try to end at sentence)
            truncated_content = content[:200]
            if len(content) > 200:
                last_period = truncated_content.rfind(".")
                if (
                    last_period > 100
                ):  # Only use if we have a reasonable amount of content
                    truncated_content = truncated_content[: last_period + 1]
                else:
                    truncated_content += "..."

            summary = f"{summary_intro}**[{title}]({url})**\n\n{truncated_content}\n\n"
            article_summaries.append(summary)

        return {
            "title": section_title,
            "introduction": section_intro,
            "articles": article_summaries,
            "article_count": len(articles),
        }

    def _generate_conclusion(self, structure: Dict[str, Any], tone: str) -> str:
        """Generate newsletter conclusion"""

        if tone == "casual":
            conclusion = """
That's a wrap for this week! I hope you found these insights useful. 

What did you think of this newsletter? Hit reply and let me know what topics you'd like to see more of.

Have a great week!
            """.strip()
        else:
            conclusion = """
## Wrapping Up

Thank you for reading this week's newsletter. I hope these curated insights help you stay informed and ahead of the curve.

If you have feedback or suggestions for future topics, please don't hesitate to reach out.

Best regards,
Your Newsletter AI
            """.strip()

        return conclusion

    def _generate_html_email(self, newsletter: Dict[str, Any]) -> str:
        """Generate HTML email version of newsletter with blog-style formatting"""

        title = newsletter.get("title", "Newsletter")
        introduction = newsletter.get("introduction", "")
        sections = newsletter.get("sections", [])
        conclusion = newsletter.get("conclusion", "")
        metadata = newsletter.get("metadata", {})

        # Get personalization info
        personalization_level = metadata.get("personalization_level", "basic")
        rag_context_used = metadata.get("rag_context_used", False)

        # Enhanced personalization badges
        personalization_badges = []
        if rag_context_used:
            if personalization_level == "high":
                personalization_badges.append("Highly Personalized")
            elif personalization_level == "medium":
                personalization_badges.append("Personalized")
            else:
                personalization_badges.append("Tailored")

        if metadata.get("custom_prompt"):
            personalization_badges.append("Custom Request")

        badge_text = (
            " • ".join(personalization_badges) if personalization_badges else "Standard"
        )

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="x-apple-disable-message-reformatting">
    <title>{title}</title>
    <style>
        /* Reset styles */
        body, table, td, p, a, li, blockquote {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
        table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
        img {{ -ms-interpolation-mode: bicubic; }}
        
        /* Base styles */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
        }}
        
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        .personalization-badge {{
            display: inline-block;
            background-color: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .content {{
            padding: 30px 20px;
        }}
        
        .intro {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            font-size: 16px;
        }}
        
        .section {{
            margin: 40px 0;
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 30px;
        }}
        
        .section:last-of-type {{
            border-bottom: none;
        }}
        
        .section h2 {{
            color: #495057;
            font-size: 24px;
            font-weight: 600;
            margin: 0 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .article {{
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 0 8px 8px 0;
            transition: all 0.3s ease;
        }}
        
        .article:hover {{
            background-color: #e9ecef;
            border-left-color: #0056b3;
        }}
        
        .article h3 {{
            margin: 0 0 10px 0;
            color: #212529;
            font-size: 18px;
            font-weight: 600;
        }}
        
        .article p {{
            margin: 0;
            color: #6c757d;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        .article a {{
            color: #007bff;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .article a:hover {{
            text-decoration: underline;
            color: #0056b3;
        }}
        
        .conclusion {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 25px;
            border-radius: 12px;
            margin: 30px 0;
            text-align: center;
            color: #495057;
        }}
        
        .footer {{
            background-color: #343a40;
            color: #adb5bd;
            text-align: center;
            padding: 20px;
            font-size: 12px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer a {{
            color: #6c757d;
            text-decoration: none;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: #f8f9fa;
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
            font-size: 12px;
            color: #6c757d;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-weight: bold;
            color: #495057;
            font-size: 16px;
        }}
        
        /* Mobile responsiveness */
        @media only screen and (max-width: 600px) {{
            .email-container {{
                width: 100% !important;
            }}
            
            .content {{
                padding: 20px 15px !important;
            }}
            
            .header h1 {{
                font-size: 24px !important;
            }}
            
            .section h2 {{
                font-size: 20px !important;
            }}
            
            .stats {{
                flex-direction: column !important;
            }}
            
            .stat {{
                margin: 5px 0 !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>{title}</h1>
            <div class="personalization-badge">{badge_text}</div>
        </div>
        
        <div class="content">
            <div class="intro">
                {introduction.replace(chr(10), "<br>")}
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{metadata.get("article_count", 0)}</div>
                    <div>Articles</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{metadata.get("estimated_read_time", 5)}</div>
                    <div>Min Read</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{datetime.utcnow().strftime("%b %d")}</div>
                    <div>Generated</div>
                </div>
            </div>
            
            {"".join([self._format_section_html(section) for section in sections])}
            
            <div class="conclusion">
                {conclusion.replace(chr(10), "<br>")}
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Newsletter AI</strong> - Personalized content powered by AI</p>
            <p>Generated on {datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")}</p>
            <p>
                <a href="#" style="color: #6c757d;">Unsubscribe</a> | 
                <a href="#" style="color: #6c757d;">Update Preferences</a> | 
                <a href="#" style="color: #6c757d;">View Online</a>
            </p>
        </div>
    </div>
</body>
</html>
        """.strip()

        return html_template

    def _format_section_html(self, section: Dict[str, Any]) -> str:
        """Format a section for HTML email with enhanced blog-style formatting"""
        title = section.get("title", "")
        articles = section.get("articles", [])

        section_html = f'<div class="section"><h2>{title}</h2>'

        for article in articles:
            if isinstance(article, str):
                # Parse article content for better formatting
                article_html = self._format_article_html(article)
                section_html += f'<div class="article">{article_html}</div>'
            else:
                section_html += f'<div class="article">{str(article)}</div>'

        section_html += "</div>"
        return section_html

    def _format_article_html(self, article_content: str) -> str:
        """Format individual article content for HTML"""
        # Simple parsing to extract title and content
        lines = article_content.split("\n")

        if not lines:
            return article_content

        # Look for markdown-style links [title](url)
        import re

        link_pattern = r"\*\*\[(.*?)\]\((.*?)\)\*\*"
        match = re.search(link_pattern, lines[0])

        if match:
            title = match.group(1)
            url = match.group(2)
            content = "\n".join(lines[1:]).strip()

            return f'''
                <h3><a href="{url}" target="_blank">{title}</a></h3>
                <p>{content}</p>
            '''
        else:
            # Fallback formatting
            return f"<p>{article_content.replace(chr(10), '<br>')}</p>"

    def _generate_plain_text_email(self, newsletter: Dict[str, Any]) -> str:
        """Generate plain text version of newsletter"""

        title = newsletter.get("title", "Newsletter")
        introduction = newsletter.get("introduction", "")
        sections = newsletter.get("sections", [])
        conclusion = newsletter.get("conclusion", "")

        plain_text = f"{title}\n{'=' * len(title)}\n\n"
        plain_text += f"{introduction}\n\n"

        for section in sections:
            section_title = section.get("title", "")
            articles = section.get("articles", [])

            plain_text += f"{section_title}\n{'-' * len(section_title)}\n\n"

            for article in articles:
                # Strip HTML tags for plain text
                clean_article = (
                    article.replace("**", "")
                    .replace("[", "")
                    .replace("](", " - ")
                    .replace(")", "")
                )
                plain_text += f"{clean_article}\n"

            plain_text += "\n"

        plain_text += f"{conclusion}\n\n"
        plain_text += (
            f"Newsletter AI - Generated on {datetime.utcnow().strftime('%B %d, %Y')}"
        )

        return plain_text

    def _extract_themes(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Extract main themes from articles"""
        themes = []
        for article in articles:
            topic = article.get("topic", "")
            if topic and topic not in themes:
                themes.append(topic)
        return themes[:5]  # Return top 5 themes

    def _count_words(self, content: Dict[str, Any]) -> int:
        """Count words in newsletter content"""
        total_words = 0

        # Count words in introduction
        intro = content.get("introduction", "")
        total_words += len(intro.split())

        # Count words in sections
        sections = content.get("sections", [])
        for section in sections:
            articles = section.get("articles", [])
            for article in articles:
                total_words += len(str(article).split())

        # Count words in conclusion
        conclusion = content.get("conclusion", "")
        total_words += len(conclusion.split())

        return total_words

    def _estimate_read_time(self, content: Dict[str, Any]) -> int:
        """Estimate reading time in minutes"""
        word_count = self._count_words(content)
        # Average reading speed: 200-250 words per minute
        return max(1, round(word_count / 225))

    async def _embed_newsletter_for_rag(
        self, newsletter_id: str, user_id: str, content: str, metadata: Dict[str, Any]
    ) -> bool:
        """Embed newsletter content for RAG retrieval"""
        try:
            return await embedding_service.embed_newsletter(
                newsletter_id=newsletter_id,
                user_id=user_id,
                content=content,
                metadata=metadata,
            )
        except Exception as e:
            print(f"Failed to embed newsletter for RAG: {e}")
            return False

    async def _get_rag_context(
        self, user_id: str, query: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Get relevant context from user's newsletter history using RAG"""
        try:
            return await embedding_service.search_similar_content(
                query=query, user_id=user_id, top_k=top_k
            )
        except Exception as e:
            print(f"Failed to get RAG context: {e}")
            return []

    async def _get_personalized_suggestions(
        self, user_id: str, topics: List[str]
    ) -> List[str]:
        """Get personalized content suggestions based on RAG analysis"""
        try:
            return await embedding_service.get_user_content_suggestions(
                user_id=user_id, topics=topics
            )
        except Exception as e:
            print(f"Failed to get personalized suggestions: {e}")
            return []

    async def _enhance_content_with_rag(
        self, 
        user_id: str, 
        articles: List[Dict[str, Any]], 
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance content generation with RAG system insights"""
        try:
            if not user_id:
                return {"rag_available": False, "reason": "No user ID provided"}
            
            # Get user's newsletter history for context
            similar_newsletters = await rag_system.retrieve_similar_newsletters(
                user_id=user_id,
                query=" ".join([article.get("title", "") for article in articles[:3]]),
                top_k=5,
                similarity_threshold=0.5
            )
            
            # Get user preference analysis
            user_analysis = await rag_system.analyze_user_preferences(user_id)
            
            # Get content recommendations based on current articles
            current_topics = list(set([
                article.get("topic", "general") for article in articles
            ]))
            
            content_recommendations = await rag_system.get_content_recommendations(
                user_id=user_id,
                current_topics=current_topics,
                current_articles=articles
            )
            
            # Analyze reading patterns
            reading_patterns = user_analysis.get("content_patterns", {})
            topic_interests = user_analysis.get("topic_interests", {})
            
            # Generate content strategy based on RAG insights
            content_strategy = {
                "recommended_tone": self._get_recommended_tone_from_history(
                    similar_newsletters, user_preferences
                ),
                "preferred_structure": self._analyze_preferred_structure(
                    similar_newsletters
                ),
                "engagement_triggers": self._extract_engagement_patterns(
                    similar_newsletters
                ),
                "avoid_topics": self._identify_low_engagement_topics(
                    similar_newsletters, topic_interests
                )
            }
            
            # Generate personalization insights
            personalization_insights = []
            
            if similar_newsletters:
                personalization_insights.append(
                    f"Found {len(similar_newsletters)} similar newsletters in your history"
                )
            
            if reading_patterns.get("preferred_length") == "medium":
                personalization_insights.append(
                    "Optimizing for medium-length content based on your reading preferences"
                )
            
            # Check for topic alignment
            preferred_topics = list(topic_interests.keys())[:3] if topic_interests else []
            matching_topics = [topic for topic in current_topics if topic in preferred_topics]
            
            if matching_topics:
                personalization_insights.append(
                    f"Emphasizing {', '.join(matching_topics)} based on your interests"
                )
            
            return {
                "rag_available": True,
                "similar_content": similar_newsletters,
                "user_analysis": user_analysis,
                "recommendations": content_recommendations,
                "content_strategy": content_strategy,
                "personalization_insights": personalization_insights,
                "reading_patterns": reading_patterns,
                "topic_alignment": {
                    "current_topics": current_topics,
                    "preferred_topics": preferred_topics,
                    "matching_topics": matching_topics
                }
            }
            
        except Exception as e:
            print(f"RAG enhancement failed: {e}")
            return {
                "rag_available": False, 
                "error": str(e),
                "fallback_used": True
            }
    
    def _get_recommended_tone_from_history(
        self, 
        similar_newsletters: List[Dict[str, Any]], 
        user_preferences: Dict[str, Any]
    ) -> str:
        """Analyze user's newsletter history to recommend optimal tone"""
        if not similar_newsletters:
            return user_preferences.get("tone", "professional")
        
        # Count tone preferences from history
        tone_counts = {}
        for newsletter in similar_newsletters:
            metadata = newsletter.get("metadata", {})
            if isinstance(metadata, dict):
                tone = metadata.get("tone", "professional")
                tone_counts[tone] = tone_counts.get(tone, 0) + 1
        
        # Return most frequent tone, fallback to user preference
        if tone_counts:
            return max(tone_counts.items(), key=lambda x: x[1])[0]
        
        return user_preferences.get("tone", "professional")
    
    def _analyze_preferred_structure(
        self, similar_newsletters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze preferred newsletter structure from user history"""
        if not similar_newsletters:
            return {"sections": 3, "articles_per_section": 3}
        
        section_counts = []
        article_counts = []
        
        for newsletter in similar_newsletters:
            content = newsletter.get("content", "")
            if isinstance(content, str):
                # Simple heuristic: count markdown headers
                section_count = content.count("##")
                if section_count > 0:
                    section_counts.append(section_count)
                
                # Count article references
                article_count = content.count("**[") # Markdown links
                if article_count > 0:
                    article_counts.append(article_count)
        
        avg_sections = int(sum(section_counts) / len(section_counts)) if section_counts else 3
        avg_articles = int(sum(article_counts) / len(article_counts)) if article_counts else 8
        
        return {
            "sections": max(2, min(5, avg_sections)),
            "total_articles": max(5, min(12, avg_articles))
        }
    
    def _extract_engagement_patterns(
        self, similar_newsletters: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract patterns that drive engagement from user history"""
        patterns = []
        
        if not similar_newsletters:
            return ["Include actionable insights", "Use clear section headers"]
        
        # Analyze successful newsletter characteristics
        for newsletter in similar_newsletters:
            metadata = newsletter.get("metadata", {})
            if isinstance(metadata, dict):
                score = metadata.get("engagement_score", 0)
                if score > 0.7:  # High engagement
                    content = newsletter.get("content", "")
                    if "actionable" in content.lower():
                        patterns.append("Include actionable insights")
                    if "🚀" in content or "📊" in content:
                        patterns.append("Use engaging emojis")
                    if "takeaway" in content.lower():
                        patterns.append("Provide clear takeaways")
        
        # Remove duplicates and return top patterns
        return list(set(patterns))[:3] if patterns else [
            "Include actionable insights", 
            "Use clear section headers",
            "Provide key takeaways"
        ]
    
    def _identify_low_engagement_topics(
        self, 
        similar_newsletters: List[Dict[str, Any]], 
        topic_interests: Dict[str, int]
    ) -> List[str]:
        """Identify topics that historically have low engagement"""
        if not topic_interests:
            return []
        
        # Sort topics by interest level (lower scores = less engaging)
        sorted_topics = sorted(topic_interests.items(), key=lambda x: x[1])
        
        # Return bottom 20% as topics to avoid emphasizing
        cutoff = max(1, len(sorted_topics) // 5)
        return [topic for topic, _ in sorted_topics[:cutoff]]

    async def _apply_rag_content_strategy(
        self, content: Dict[str, Any], rag_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply RAG-based content strategy to enhance newsletter"""
        try:
            if not rag_context.get("rag_available"):
                return content

            content_strategy = rag_context.get("content_strategy", {})
            recommendations = rag_context.get("recommendations", {})

            # Apply tone recommendations
            recommended_tone = content_strategy.get("recommended_tone")
            if recommended_tone:
                content["metadata"] = content.get("metadata", {})
                content["metadata"]["applied_tone"] = recommended_tone

            # Add personalization insights to metadata
            personalization_insights = rag_context.get("personalization_insights", [])
            if personalization_insights:
                content["metadata"]["personalization_insights"] = (
                    personalization_insights
                )

            # Add content recommendations
            topic_suggestions = recommendations.get("topic_suggestions", [])
            if topic_suggestions:
                content["metadata"]["topic_recommendations"] = [
                    t["topic"] for t in topic_suggestions[:3]
                ]

            return content

        except Exception as e:
            print(f"Failed to apply RAG content strategy: {e}")
            return content

    def _create_blog_style_template(
        self, newsletter: Dict[str, Any], template_type: str = "modern"
    ) -> Dict[str, str]:
        """Create blog-style newsletter templates with proper structure"""

        title = newsletter.get("title", "Newsletter")
        introduction = newsletter.get("introduction", "")
        sections = newsletter.get("sections", [])
        conclusion = newsletter.get("conclusion", "")
        metadata = newsletter.get("metadata", {})

        if template_type == "modern":
            # Modern blog-style template with clean design
            html_template = self._generate_html_email(newsletter)

            # Create markdown version for blog-style reading
            markdown_template = f"""# {title}

{introduction}

---

"""

            for section in sections:
                section_title = section.get("title", "")
                articles = section.get("articles", [])

                markdown_template += f"## {section_title}\n\n"

                for article in articles:
                    markdown_template += f"{article}\n"

                markdown_template += "---\n\n"

            markdown_template += f"""## Conclusion

{conclusion}

---

*Generated on {metadata.get("generated_at", "Unknown")} | {metadata.get("word_count", 0)} words | {metadata.get("estimated_read_time", 5)} min read*
"""

            return {
                "html": html_template,
                "markdown": markdown_template,
                "plain_text": self._generate_plain_text_email(newsletter),
            }

        else:
            # Fallback to existing HTML generation
            return {
                "html": self._generate_html_email(newsletter),
                "markdown": "",
                "plain_text": self._generate_plain_text_email(newsletter),
            }

    def _generate_plain_text_email(self, newsletter: Dict[str, Any]) -> str:
        """Generate plain text version of newsletter"""

        title = newsletter.get("title", "Newsletter")
        introduction = newsletter.get("introduction", "")
        sections = newsletter.get("sections", [])
        conclusion = newsletter.get("conclusion", "")
        metadata = newsletter.get("metadata", {})

        plain_text = f"""{title}
{"=" * len(title)}

{introduction}

"""

        for section in sections:
            section_title = section.get("title", "")
            articles = section.get("articles", [])

            plain_text += f"{section_title}\n{'-' * len(section_title)}\n\n"

            for i, article in enumerate(articles, 1):
                # Clean up markdown formatting for plain text
                clean_article = str(article).replace("**", "").replace("*", "")
                plain_text += f"{i}. {clean_article}\n"

            plain_text += "\n"

        plain_text += f"""
{conclusion}

---
Generated: {metadata.get("generated_at", "Unknown")}
Articles: {metadata.get("article_count", 0)}
Reading time: {metadata.get("estimated_read_time", 5)} minutes
"""

        return plain_text


# Global writing agent instance
writing_agent = NewsletterWritingAgent()
