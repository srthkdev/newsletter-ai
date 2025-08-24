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
        
        try:
            builder = PlanBuilder()

            # Check if builder has add_step method (version compatibility)
            if not hasattr(builder, 'add_step'):
                print("⚠️ PlanBuilder version incompatibility - using fallback")
                raise AttributeError("PlanBuilder missing add_step method")

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

            # Step 4: Generate mermaid mindmap
            builder.add_step(
                "generate_mermaid_mindmap",
                f"""
                Generate a mindmap in Mermaid format suitable for rendering.
                
                Guidelines:
                1. Use Mermaid mindmap syntax starting with 'mindmap'
                2. Use proper indentation for hierarchy
                3. Start with the newsletter title as root
                4. Use clear, concise labels
                5. Include main topics as primary branches
                6. Add articles and insights as sub-branches
                7. Keep it comprehensive but readable
                
                Example Mermaid mindmap structure:
                ```
                mindmap
                  root)Newsletter Title(
                    Technology
                      AI Development
                        Article 1
                        Article 2
                      Startups
                        Article 3
                    Business
                      Market Trends
                        Article 4
                      Investment
                        Article 5
                    Key Takeaways
                      Insight 1
                      Insight 2
                ```
                
                User ID: {user_id}
                Generate comprehensive Mermaid mindmap covering all newsletter content.
                """,
            )

            return builder.build()
            
        except (AttributeError, ImportError, Exception) as e:
            print(f"⚠️ PlanBuilder error: {e} - using direct fallback")
            # Return a mock plan that will trigger fallback in _generate_newsletter_mindmap
            return None

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
            mindmap_markdown = ""
            
            # Try Portia AI first
            try:
                plan = await self.create_plan(context)
                
                # If plan creation failed, skip to fallback
                if plan is None:
                    print("⚠️ Plan creation failed - using fallback")
                    raise Exception("Plan creation failed")
                    
                result = await self.run_plan(plan)
                
                if result["success"] and result.get("result"):
                    # Extract mindmap from different possible result structures
                    result_data = result.get("result", {})
                    if isinstance(result_data, dict):
                        mindmap_markdown = (
                            result_data.get("mermaid_mindmap") or 
                            result_data.get("mindmap_markdown") or
                            result_data.get("final_result") or
                            ""
                        )
                    elif isinstance(result_data, str):
                        mindmap_markdown = result_data
                    
                    # Ensure it's in Mermaid format
                    if mindmap_markdown and not mindmap_markdown.strip().startswith("mindmap"):
                        # Convert markdown to Mermaid if needed
                        mindmap_markdown = self._convert_to_mermaid(mindmap_markdown)
                        
            except Exception as portia_error:
                print(f"⚠️ Portia AI mindmap generation failed: {portia_error}")
                print("🔄 Falling back to local mindmap generation...")
            
            # Always use fallback if Portia didn't produce a good mindmap
            if not mindmap_markdown or len(mindmap_markdown.strip()) < 50:
                print("🔄 Using enhanced fallback mindmap generation...")
                mindmap_markdown = await self._generate_fallback_mindmap(context)

            # Store mindmap in memory for future reference
            user_id = context.get("user_id")
            newsletter_id = context.get("newsletter_id", str(uuid.uuid4()))
            
            if user_id and mindmap_markdown:
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
                    "generation_method": "portia_ai" if len(mindmap_markdown) > 200 else "fallback"
                }
            }

        except Exception as e:
            # Final fallback - generate basic mindmap
            print(f"⚠️ Mindmap generation error: {e}")
            print("🔄 Using basic fallback mindmap...")
            
            basic_mindmap = await self._generate_basic_mindmap(context)
            
            return {
                "success": True,
                "mindmap_markdown": basic_mindmap,
                "newsletter_id": context.get("newsletter_id", str(uuid.uuid4())),
                "agent": self.name,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "metadata": {
                    "topics_count": len(context.get("topics", [])),
                    "articles_count": len(context.get("articles", [])),
                    "mindmap_length": len(basic_mindmap),
                    "generation_method": "basic_fallback"
                }
            }

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
        """Generate fallback mindmap when keyword extraction fails"""
        return await self._generate_basic_mindmap(context)

    async def _generate_keyword_based_mindmap(self, context: Dict[str, Any], keywords_data: Dict[str, Any]) -> str:
        """Generate enhanced keyword-based mindmap"""
        try:
            newsletter_content = context.get("newsletter_content", {})
            title = newsletter_content.get("title", "Newsletter")
            
            # Get top keywords and related terms
            primary_keywords = keywords_data.get("primary_keywords", [])
            related_terms = keywords_data.get("related_terms", {})
            
            # Start building the Mermaid mindmap
            title_clean = title.replace(" ", "_").replace("-", "_")
            mindmap_lines = [
                "mindmap",
                f"  root){title_clean}("
            ]
            
            # Add keyword branches with related terms
            for i, keyword in enumerate(primary_keywords[:6]):  # Limit to 6 main keywords
                keyword_clean = keyword.replace(" ", "_").replace("-", "_")
                
                # Add emoji based on keyword type
                emoji = self._get_keyword_emoji(keyword)
                mindmap_lines.append(f"    {emoji} {keyword_clean}")
                
                # Add related terms
                terms = related_terms.get(keyword, [])
                for term in terms[:3]:  # Max 3 related terms per keyword
                    term_clean = term.replace(" ", "_").replace("-", "_")
                    mindmap_lines.append(f"      {term_clean}")
            
            return "\n".join(mindmap_lines)
            
        except Exception as e:
            print(f"Error generating keyword mindmap: {e}")
            return await self._generate_basic_keyword_mindmap(context, keywords_data)
    
    async def _generate_basic_keyword_mindmap(self, context: Dict[str, Any], keywords_data: Dict[str, Any]) -> str:
        """Generate simple keyword mindmap as final fallback"""
        newsletter_content = context.get("newsletter_content", {})
        title = newsletter_content.get("title", "Newsletter")
        keywords = keywords_data.get("primary_keywords", ["Technology", "Business", "Innovation"])
        
        title_clean = title.replace(" ", "_")
        
        basic_lines = [
            "mindmap",
            f"  root){title_clean}("
        ]
        
        for keyword in keywords[:5]:
            keyword_clean = keyword.replace(" ", "_")
            emoji = self._get_keyword_emoji(keyword)
            basic_lines.append(f"    {emoji} {keyword_clean}")
            basic_lines.append(f"      Related_{keyword_clean}")
        
        return "\n".join(basic_lines)
    
    def _get_keyword_emoji(self, keyword: str) -> str:
        """Get appropriate emoji for keyword"""
        keyword_lower = keyword.lower()
        
        if any(tech in keyword_lower for tech in ['ai', 'tech', 'software', 'digital', 'data']):
            return '🤖'
        elif any(biz in keyword_lower for biz in ['business', 'market', 'finance', 'economy']):
            return '💼'
        elif any(sci in keyword_lower for sci in ['research', 'science', 'study', 'innovation']):
            return '🔬'
        elif any(health in keyword_lower for health in ['health', 'medical', 'pharma', 'bio']):
            return '🏥'
        elif any(energy in keyword_lower for energy in ['energy', 'climate', 'environment']):
            return '🌱'
        else:
            return '📊'

    async def _generate_basic_mindmap(self, context: Dict[str, Any]) -> str:
        """Generate a basic mindmap in Mermaid format as final fallback"""
        newsletter_content = context.get("newsletter_content", {})
        articles = context.get("articles", [])
        topics = context.get("topics", ["General"])
        
        title = newsletter_content.get("title", "Newsletter")
        
        basic_lines = [
            "mindmap",
            f"  root){title.replace(' ', '_')}(",
            "    📊 Content",
            f"      Articles_{len(articles)}",
            f"      Topics_{len(topics)}"
        ]
        
        # Add simple topic structure
        for topic in topics[:3]:
            topic_clean = topic.replace(" ", "_")
            basic_lines.append(f"    📂 {topic_clean}")
        
        # Add simple article list
        if articles:
            basic_lines.append("    📰 Articles")
            for i, article in enumerate(articles[:3]):  # Top 3 articles
                if isinstance(article, dict) and article.get("title"):
                    article_name = article["title"][:30].replace(" ", "_")
                    basic_lines.append(f"      {article_name}")
        
        basic_lines.extend([
            "    🤖 AI_Generated",
            "      Newsletter_AI"
        ])
        
        return "\n".join(basic_lines)
    def _convert_to_mermaid(self, markdown_content: str) -> str:
        """Convert markdown mindmap to Mermaid format"""
        try:
            lines = markdown_content.strip().split('\n')
            mermaid_lines = ["mindmap"]
            
            root_found = False
            for line in lines:
                if not line.strip():
                    continue
                    
                # Count heading level
                level = 0
                while level < len(line) and line[level] == '#':
                    level += 1
                
                if level > 0:
                    text = line[level:].strip()
                    # Clean text for Mermaid
                    clean_text = text.replace("**", "").replace("*", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "")
                    clean_text = ''.join(c if c.isalnum() or c in ' _' else '_' for c in clean_text)
                    clean_text = clean_text.replace(" ", "_")
                    
                    if level == 1 and not root_found:
                        mermaid_lines.append(f"  root){clean_text}(")
                        root_found = True
                    else:
                        indent = "  " * level
                        mermaid_lines.append(f"{indent}{clean_text}")
            
            return "\n".join(mermaid_lines)
        except:
            # Fallback to basic mindmap
            return self._generate_basic_mindmap({"newsletter_content": {"title": "Newsletter"}, "articles": [], "topics": ["General"]})

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