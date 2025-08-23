"""
Newsletter Mindmap Agent using Portia AI framework

This agent generates interactive mindmaps from newsletter content to provide
visual representations of the key topics, articles, and insights covered.

Features:
- Generates markdown-based mindmaps for markmap rendering
- Analyzes newsletter structure and content for mindmap creation
- Integrates with newsletter generation workflow
- Uses Portia AI for intelligent content analysis and mindmap structure generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from portia import Plan, PlanBuilder
from app.portia.base_agent import BaseNewsletterAgent
from app.services.memory import memory_service
import json
import uuid


class NewsletterMindmapAgent(BaseNewsletterAgent):
    """Portia agent for generating interactive mindmaps from newsletter content"""

    def __init__(self):
        super().__init__("mindmap_agent")
        self.memory = memory_service

    async def create_plan(self, context: Dict[str, Any]) -> Plan:
        """Create mindmap generation plan using Portia PlanBuilder"""
        user_id = context.get("user_id")
        newsletter_content = context.get("newsletter_content", {})
        articles = context.get("articles", [])
        topics = context.get("topics", [])
        
        builder = PlanBuilder()

        # Step 1: Analyze newsletter structure and content
        builder.add_step(
            "analyze_newsletter_structure",
            f"""
            Analyze the newsletter content to understand its structure and key themes:
            
            Newsletter Title: {newsletter_content.get('title', 'Newsletter')}
            Topics Covered: {', '.join(topics)}
            Number of Articles: {len(articles)}
            
            Content Structure:
            - Introduction: {newsletter_content.get('introduction', 'N/A')[:200]}...
            - Sections: {len(newsletter_content.get('sections', []))} sections
            - Conclusion: {newsletter_content.get('conclusion', 'N/A')[:200]}...
            
            Identify:
            1. Main topics and themes
            2. Key relationships between articles
            3. Hierarchical structure for mindmap
            4. Important insights and takeaways
            """,
        )

        # Step 2: Extract key concepts and relationships
        builder.add_step(
            "extract_key_concepts",
            f"""
            From the newsletter content, extract:
            
            1. Primary topics (main branches)
            2. Subtopics and categories
            3. Key articles and their main points
            4. Relationships between different articles/topics
            5. Important insights, trends, or patterns
            6. Action items or takeaways
            
            Articles to analyze:
            {self._format_articles_for_analysis(articles)}
            
            Focus on creating a logical hierarchy that would work well in a mindmap format.
            """,
        )

        # Step 3: Design mindmap structure
        builder.add_step(
            "design_mindmap_structure",
            """
            Design a hierarchical mindmap structure that:
            
            1. Has the newsletter title as the central node
            2. Uses main topics as primary branches
            3. Includes subtopics and specific articles as secondary branches
            4. Shows key insights and takeaways as leaf nodes
            5. Maintains logical grouping and flow
            6. Is suitable for markmap rendering
            
            Consider visual hierarchy and readability.
            """,
        )

        # Step 4: Generate markdown mindmap
        builder.add_step(
            "generate_markdown_mindmap",
            f"""
            Generate a mindmap in markdown format suitable for markmap rendering.
            
            Guidelines:
            1. Use markdown header levels (# ## ### ####) to create hierarchy
            2. Start with the newsletter title as the main header (#)
            3. Use emojis to make it visually appealing
            4. Include brief descriptions or key points
            5. Ensure proper nesting and structure
            6. Make it comprehensive but not overcrowded
            
            Example structure:
            # 📰 Newsletter Title
            ## 🔬 Technology
            ### AI & Machine Learning
            #### Article: "AI Breakthrough"
            ##### Key insight: Revolutionary approach
            ### Startups & Innovation
            #### Article: "Startup Success"
            ## 💼 Business
            ### Market Trends
            #### Key finding: Growth in sector
            ## 🎯 Key Takeaways
            ### Action Items
            ### Future Outlook
            
            User ID: {user_id}
            Generate comprehensive mindmap covering all newsletter content.
            """,
        )

        return builder.build()

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mindmap generation task"""
        try:
            if task == "generate_mindmap":
                return await self._generate_newsletter_mindmap(context)
            elif task == "analyze_content_structure":
                return await self._analyze_content_structure(context)
            elif task == "create_topic_mindmap":
                return await self._create_topic_mindmap(context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task: {task}",
                    "agent": self.name,
                }
        except Exception as e:
            return await self.handle_error(e, context)

    async def _generate_newsletter_mindmap(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive mindmap for newsletter content"""
        try:
            # Create and execute mindmap generation plan
            plan = await self.create_plan(context)
            result = await self.run_plan(plan)

            if not result["success"]:
                return result

            # Process the mindmap result
            mindmap_markdown = result.get("result", {}).get("markdown_mindmap", "")
            
            if not mindmap_markdown:
                # Fallback mindmap generation
                mindmap_markdown = await self._generate_fallback_mindmap(context)

            # Store mindmap in memory for future reference
            user_id = context.get("user_id")
            newsletter_id = context.get("newsletter_id", str(uuid.uuid4()))
            
            if user_id:
                await self._store_mindmap_in_memory(
                    user_id, newsletter_id, mindmap_markdown, context
                )

            return {
                "success": True,
                "mindmap_markdown": mindmap_markdown,
                "newsletter_id": newsletter_id,
                "agent": self.name,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "topics_count": len(context.get("topics", [])),
                    "articles_count": len(context.get("articles", [])),
                    "mindmap_length": len(mindmap_markdown),
                }
            }

        except Exception as e:
            return await self.handle_error(e, context)

    async def _analyze_content_structure(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze newsletter content structure for mindmap creation"""
        try:
            newsletter_content = context.get("newsletter_content", {})
            articles = context.get("articles", [])
            
            # Extract structure information
            structure = {
                "title": newsletter_content.get("title", "Newsletter"),
                "main_topics": context.get("topics", []),
                "sections": [],
                "total_articles": len(articles),
                "key_themes": []
            }
            
            # Analyze sections
            sections = newsletter_content.get("sections", [])
            for section in sections:
                section_info = {
                    "title": section.get("title", "Untitled Section"),
                    "article_count": len(section.get("articles", [])),
                    "topics": []
                }
                structure["sections"].append(section_info)
            
            # Extract key themes from articles
            for article in articles[:10]:  # Limit to first 10 articles
                if isinstance(article, dict) and article.get("title"):
                    structure["key_themes"].append(article["title"])
            
            return {
                "success": True,
                "structure": structure,
                "agent": self.name
            }
            
        except Exception as e:
            return await self.handle_error(e, context)

    async def _create_topic_mindmap(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a topic-focused mindmap"""
        try:
            topics = context.get("topics", [])
            articles = context.get("articles", [])
            
            # Create simplified topic-based mindmap
            mindmap_lines = [
                "# 📊 Newsletter Topics Overview",
                ""
            ]
            
            for topic in topics:
                mindmap_lines.append(f"## 🎯 {topic.title()}")
                
                # Find articles related to this topic
                topic_articles = [
                    article for article in articles 
                    if isinstance(article, dict) and 
                    topic.lower() in str(article.get("title", "")).lower()
                ][:3]  # Limit to 3 articles per topic
                
                for article in topic_articles:
                    title = article.get("title", "Article")
                    mindmap_lines.append(f"### 📰 {title[:50]}...")
                    
                    if article.get("summary"):
                        mindmap_lines.append(f"#### 💡 {article['summary'][:100]}...")
            
            mindmap_markdown = "\n".join(mindmap_lines)
            
            return {
                "success": True,
                "mindmap_markdown": mindmap_markdown,
                "agent": self.name
            }
            
        except Exception as e:
            return await self.handle_error(e, context)

    async def _generate_fallback_mindmap(self, context: Dict[str, Any]) -> str:
        """Generate a fallback mindmap when Portia AI is unavailable"""
        newsletter_content = context.get("newsletter_content", {})
        articles = context.get("articles", [])
        topics = context.get("topics", [])
        
        title = newsletter_content.get("title", "Newsletter Mindmap")
        
        mindmap_lines = [
            f"# 📰 {title}",
            "",
            "## 🎯 Main Topics"
        ]
        
        # Add topics as main branches
        for topic in topics[:5]:  # Limit to 5 topics
            mindmap_lines.append(f"### 🔖 {topic.title()}")
        
        # Add content sections
        if newsletter_content.get("sections"):
            mindmap_lines.append("")
            mindmap_lines.append("## 📝 Content Sections")
            
            for section in newsletter_content["sections"][:4]:  # Limit to 4 sections
                section_title = section.get("title", "Section")
                mindmap_lines.append(f"### 📄 {section_title}")
                
                section_articles = section.get("articles", [])[:2]  # Limit to 2 articles per section
                for article in section_articles:
                    if isinstance(article, dict) and article.get("title"):
                        mindmap_lines.append(f"#### 📰 {article['title'][:40]}...")
        
        # Add key insights
        mindmap_lines.extend([
            "",
            "## 💡 Key Insights",
            f"### 📊 {len(articles)} Articles Analyzed",
            f"### 🎯 {len(topics)} Topics Covered"
        ])
        
        if newsletter_content.get("summary"):
            mindmap_lines.append(f"### 📋 {newsletter_content['summary'][:50]}...")
        
        return "\n".join(mindmap_lines)

    def _format_articles_for_analysis(self, articles: List[Dict[str, Any]]) -> str:
        """Format articles for Portia AI analysis"""
        formatted_articles = []
        
        for i, article in enumerate(articles[:8]):  # Limit to 8 articles for analysis
            if isinstance(article, dict):
                title = article.get("title", f"Article {i+1}")
                content = article.get("content", "")[:200]  # First 200 chars
                summary = article.get("summary", "")
                
                formatted_articles.append(f"""
Article {i+1}: {title}
Content: {content}...
Summary: {summary}
---""")
        
        return "\n".join(formatted_articles)

    async def _store_mindmap_in_memory(
        self, 
        user_id: str, 
        newsletter_id: str, 
        mindmap_markdown: str, 
        context: Dict[str, Any]
    ):
        """Store generated mindmap in memory for future reference"""
        try:
            mindmap_data = {
                "newsletter_id": newsletter_id,
                "mindmap_markdown": mindmap_markdown,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "topics": context.get("topics", []),
                "articles_count": len(context.get("articles", [])),
                "context_metadata": {
                    "title": context.get("newsletter_content", {}).get("title"),
                    "sections_count": len(context.get("newsletter_content", {}).get("sections", []))
                }
            }
            
            memory_key = f"mindmap:{user_id}:{newsletter_id}"
            await self.memory.store_user_data(user_id, memory_key, mindmap_data)
            
        except Exception as e:
            # Don't fail the whole operation if memory storage fails
            print(f"Warning: Failed to store mindmap in memory: {e}")

    async def get_stored_mindmaps(self, user_id: str) -> Dict[str, Any]:
        """Retrieve stored mindmaps for a user"""
        try:
            # Get all mindmaps for the user
            mindmaps = []
            
            # This would need to be implemented based on your memory service structure
            # For now, return empty result
            return {
                "success": True,
                "mindmaps": mindmaps,
                "count": len(mindmaps)
            }
            
        except Exception as e:
            return await self.handle_error(e, {"user_id": user_id})

    async def regenerate_mindmap(
        self, 
        newsletter_id: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate mindmap for existing newsletter"""
        try:
            # Add regeneration context
            context["regeneration"] = True
            context["newsletter_id"] = newsletter_id
            
            return await self._generate_newsletter_mindmap(context)
            
        except Exception as e:
            return await self.handle_error(e, context)


# Global mindmap agent instance
mindmap_agent = NewsletterMindmapAgent()