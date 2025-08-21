"""
Newsletter AI - Custom Newsletter Creation
"""

import streamlit as st
import requests
from typing import Dict, List, Any, Optional
import json

# Page configuration
st.set_page_config(
    page_title="Create Newsletter - Newsletter AI", page_icon="✍️", layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS
st.markdown(
    """
<style>
    .prompt-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .example-prompt {
        background: #e0e7ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .example-prompt:hover {
        background: #c7d2fe;
    }
    .success-message {
        background: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    .info-message {
        background: #dbeafe;
        color: #1e40af;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Load example prompts from API
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_example_prompts():
    """Load example prompts from API"""
    examples_data = get_prompt_examples()
    if examples_data:
        return examples_data.get("examples", []), examples_data.get("placeholders", [])
    
    # Fallback examples if API is not available
    fallback_examples = [
        {
            "category": "Technology",
            "prompt": "Create a newsletter about AI breakthroughs this week with a technical tone",
            "description": "Focus on recent AI developments with detailed analysis",
            "tags": ["AI", "technical", "weekly"],
        },
        {
            "category": "Business",
            "prompt": "Focus on startup funding news with a casual, conversational style",
            "description": "Cover venture capital and startup news in an approachable way",
            "tags": ["startups", "funding", "casual"],
        },
    ]
    
    fallback_placeholders = [
        "Create a newsletter about AI breakthroughs this week with a technical tone",
        "Focus on startup funding news with a casual, conversational style",
    ]
    
    return fallback_examples, fallback_placeholders


def get_user_preferences() -> Optional[Dict[str, Any]]:
    """Get current user preferences"""
    try:
        user_id = st.session_state.get("user_id", "demo_user")
        response = requests.get(f"{API_BASE_URL}/preferences/{user_id}", timeout=10)

        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def validate_prompt(prompt: str) -> Optional[Dict[str, Any]]:
    """Validate a custom prompt"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/newsletters/validate-prompt",
            json={"prompt": prompt},
            timeout=10,
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def get_prompt_examples() -> Optional[Dict[str, Any]]:
    """Get prompt examples and placeholders"""
    try:
        response = requests.get(f"{API_BASE_URL}/newsletters/prompt-examples", timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def enhance_prompt_with_rag(
    prompt: str, user_id: str, preferences: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Enhance prompt using RAG system"""
    try:
        params = {
            "user_id": user_id,
            "prompt": prompt,
        }
        if preferences:
            params["user_preferences"] = preferences

        response = requests.post(
            f"{API_BASE_URL}/newsletters/enhance-prompt",
            params={"user_id": user_id, "prompt": prompt},
            json=preferences,
            timeout=15,
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def generate_custom_newsletter(
    prompt: str, preferences: Optional[Dict[str, Any]] = None
) -> tuple[bool, str, Optional[Dict[str, Any]]]:
    """Generate newsletter from custom prompt"""
    try:
        user_id = st.session_state.get("user_id", "demo_user")

        payload = {
            "user_id": user_id,
            "custom_prompt": prompt,
            "user_preferences": preferences,
            "use_rag": True,
            "send_immediately": False,  # Generate but don't send yet
        }

        response = requests.post(
            f"{API_BASE_URL}/newsletters/generate-custom",
            json=payload,
            timeout=60,  # Custom generation might take longer
        )

        if response.status_code == 200:
            data = response.json()
            return True, "Newsletter generated successfully!", data
        else:
            error_data = response.json()
            return (
                False,
                error_data.get("detail", "Failed to generate newsletter"),
                None,
            )

    except requests.exceptions.ConnectionError:
        return (
            False,
            "Cannot connect to server. Please make sure the API is running.",
            None,
        )
    except requests.exceptions.Timeout:
        return (
            False,
            "Request timed out. Newsletter generation is taking longer than expected.",
            None,
        )
    except Exception as e:
        return False, f"Error generating newsletter: {str(e)}", None


def send_newsletter(newsletter_id: str) -> tuple[bool, str]:
    """Send a generated newsletter"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/newsletters/{newsletter_id}/send", timeout=30
        )

        if response.status_code == 200:
            return True, "Newsletter sent successfully!"
        else:
            error_data = response.json()
            return False, error_data.get("detail", "Failed to send newsletter")

    except Exception as e:
        return False, f"Error sending newsletter: {str(e)}"


def main():
    """Main custom newsletter creation page"""

    # Header
    st.title("✍️ Create Custom Newsletter")
    st.markdown("Tell our AI exactly what kind of newsletter you want to receive")

    # Load user preferences
    preferences = get_user_preferences()

    # Initialize session state
    if "custom_prompt" not in st.session_state:
        st.session_state.custom_prompt = ""
    if "generated_newsletter" not in st.session_state:
        st.session_state.generated_newsletter = None

    # Main content tabs
    tab1, tab2, tab3 = st.tabs(
        ["✍️ Create Prompt", "📋 Examples", "🎯 Advanced Options"]
    )

    with tab1:
        show_prompt_creation(preferences)

    with tab2:
        show_example_prompts()

    with tab3:
        show_advanced_options(preferences)

    # Generation and preview section
    st.markdown("---")
    show_generation_section()


def show_prompt_creation(preferences: Optional[Dict[str, Any]]):
    """Show the main prompt creation interface"""

    st.markdown("### 💭 Describe Your Perfect Newsletter")

    # Current preferences context
    if preferences and not preferences.get("is_default", False):
        st.markdown(
            """
        <div class="info-message">
            <strong>📋 Your current preferences will be combined with your custom prompt:</strong><br>
            <strong>Topics:</strong> {}<br>
            <strong>Tone:</strong> {}<br>
            <strong>Frequency:</strong> {}
        </div>
        """.format(
                ", ".join(preferences.get("topics", [])),
                preferences.get("tone", "Not set").title(),
                preferences.get("frequency", "Not set").replace("_", " ").title(),
            ),
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            "⚠️ You haven't set up preferences yet. Your custom prompt will use default settings."
        )

    # Main prompt input
    st.markdown("#### What would you like your newsletter to focus on?")

    # Load placeholders from API
    _, placeholders = load_example_prompts()
    
    # Create placeholder text
    placeholder_text = "Example prompts:\n\n"
    for i, placeholder in enumerate(placeholders[:4], 1):
        placeholder_text += f"• \"{placeholder}\"\n"
    
    placeholder_text += "\nBe specific about:\n- Topics you want covered\n- Tone/style preferences\n- Number of articles\n- Any special focus areas"

    custom_prompt = st.text_area(
        "Custom Newsletter Prompt",
        value=st.session_state.custom_prompt,
        height=150,
        placeholder=placeholder_text,
        help="Describe exactly what you want in your newsletter. Be as specific as possible!",
        key="prompt_input",
    )

    # Update session state
    st.session_state.custom_prompt = custom_prompt

    # Real-time prompt analysis and enhancement
    if custom_prompt:
        st.markdown("#### 🔍 Prompt Analysis & Enhancement")

        # Get validation from API
        validation_result = validate_prompt(custom_prompt)
        
        if validation_result:
            # Display validation results
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                score = validation_result.get("score", 0)
                color = "green" if score >= 40 else "orange" if score >= 25 else "red"
                st.metric("Quality Score", f"{score}/60", help="Overall prompt quality score")

            with col2:
                word_count = len(custom_prompt.split())
                status = "✅" if word_count >= 10 else "⚠️"
                st.metric("Word Count", word_count, help="Aim for 10+ words for better results")

            with col3:
                is_valid = validation_result.get("is_valid", False)
                st.markdown(f"**Valid Prompt**\n{'✅ Yes' if is_valid else '❌ No'}")

            with col4:
                feedback_count = len(validation_result.get("feedback", []))
                st.markdown(f"**Feedback Items**\n📝 {feedback_count}")

            # Show feedback
            feedback = validation_result.get("feedback", [])
            if feedback:
                st.markdown("**✅ Positive feedback:**")
                for item in feedback:
                    st.markdown(f"• {item}")

            # Show suggestions
            suggestions = validation_result.get("suggestions", [])
            if suggestions:
                st.markdown("**💡 Suggestions for improvement:**")
                for suggestion in suggestions:
                    st.markdown(f"• {suggestion}")

            # Show warnings
            warnings = validation_result.get("warnings", [])
            if warnings:
                st.markdown("**⚠️ Warnings:**")
                for warning in warnings:
                    st.markdown(f"• {warning}")

        # RAG Enhancement Section
        if preferences and not preferences.get("is_default", False):
            st.markdown("---")
            st.markdown("#### 🧠 AI Enhancement (RAG)")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🚀 Enhance with AI", help="Use your reading history to improve this prompt"):
                    with st.spinner("Enhancing prompt with your reading history..."):
                        user_id = st.session_state.get("user_id", "demo_user")
                        enhancement_result = enhance_prompt_with_rag(
                            custom_prompt, user_id, preferences
                        )
                    
                    if enhancement_result:
                        st.session_state.rag_enhancement = enhancement_result
                        if enhancement_result.get("rag_available"):
                            st.success("✅ Prompt enhanced with your reading history!")
                        else:
                            st.info("💡 No reading history available yet, but prompt was analyzed.")
                    else:
                        st.error("❌ Enhancement failed. Please try again.")

            with col2:
                if st.button("🔄 Reset to Original"):
                    if "rag_enhancement" in st.session_state:
                        del st.session_state.rag_enhancement
                        st.success("✅ Reset to original prompt")

            # Show enhancement results
            if "rag_enhancement" in st.session_state:
                enhancement = st.session_state.rag_enhancement
                
                if enhancement.get("enhanced_prompt") != custom_prompt:
                    st.markdown("**🎯 Enhanced Prompt:**")
                    st.info(enhancement["enhanced_prompt"])
                    
                    # Show what was enhanced
                    enhancements = enhancement.get("enhancements_applied", [])
                    if enhancements:
                        st.markdown("**✨ Enhancements applied:**")
                        for enhancement_item in enhancements:
                            st.markdown(f"• {enhancement_item}")
                    
                    # Show RAG insights
                    insights = enhancement.get("rag_insights", [])
                    if insights:
                        st.markdown("**🔍 Personalization insights:**")
                        for insight in insights:
                            st.markdown(f"• {insight}")
                    
                    # Option to use enhanced prompt
                    if st.button("✅ Use Enhanced Prompt"):
                        st.session_state.custom_prompt = enhancement["enhanced_prompt"]
                        st.success("✅ Enhanced prompt applied!")
                        st.rerun()
        else:
            st.info("💡 Set up your preferences to unlock AI-powered prompt enhancement based on your reading history!")


def show_example_prompts():
    """Show example prompts that users can use"""

    st.markdown("### 📋 Example Prompts")
    st.markdown(
        "Click on any example to use it as a starting point for your custom newsletter"
    )

    # Load examples from API
    examples, placeholders = load_example_prompts()

    # Group examples by category
    categories = {}
    for example in examples:
        category = example.get("category", "General")
        if category not in categories:
            categories[category] = []
        categories[category].append(example)

    # Display examples by category
    for category, category_examples in categories.items():
        st.markdown(f"#### {category}")

        for example in category_examples:
            with st.container():
                # Show tags if available
                tags = example.get("tags", [])
                tags_html = ""
                if tags:
                    tags_html = " ".join([f"<span style='background: #e0e7ff; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-right: 4px;'>{tag}</span>" for tag in tags[:3]])

                st.markdown(
                    f"""
                <div class="example-prompt">
                    <h5 style="margin: 0 0 0.5rem 0;">{example.get("description", "Example Prompt")}</h5>
                    <p style="margin: 0 0 0.5rem 0; color: #6b7280;">{example["prompt"]}</p>
                    <div style="margin-top: 0.5rem;">{tags_html}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"Use This", key=f"use_{example['prompt'][:20]}"):
                        st.session_state.custom_prompt = example["prompt"]
                        st.success(f"✅ Loaded example prompt!")
                        st.rerun()

    # Custom prompt builder
    st.markdown("---")
    st.markdown("#### 🛠️ Prompt Builder")
    st.markdown("Build your prompt step by step:")

    col1, col2 = st.columns(2)

    with col1:
        topic_focus = st.selectbox(
            "Main topic focus",
            [
                "",
                "Technology",
                "Business",
                "Science",
                "Health",
                "Finance",
                "Marketing",
                "Innovation",
            ],
            help="What should be the main focus?",
        )

        tone_preference = st.selectbox(
            "Tone preference",
            ["", "professional", "casual", "technical", "friendly", "formal"],
            help="How should the newsletter sound?",
        )

    with col2:
        article_count = st.selectbox(
            "Number of articles",
            ["", "3-5 articles", "5-7 articles", "7-10 articles", "10+ articles"],
            help="How many articles should be included?",
        )

        special_focus = st.text_input(
            "Special focus (optional)",
            placeholder="e.g., 'practical applications', 'recent developments', 'case studies'",
            help="Any specific angle or focus?",
        )

    if st.button("🔨 Build Prompt"):
        built_prompt = f"Create a newsletter about {topic_focus.lower() if topic_focus else '[topic]'}"

        if special_focus:
            built_prompt += f" focusing on {special_focus}"

        if tone_preference:
            built_prompt += f". Use a {tone_preference} tone"

        if article_count:
            built_prompt += f" and include {article_count.lower()}"

        built_prompt += "."

        st.session_state.custom_prompt = built_prompt
        st.success("✅ Prompt built! Check the Create Prompt tab.")
        st.rerun()


def show_advanced_options(preferences: Optional[Dict[str, Any]]):
    """Show advanced options for newsletter generation"""

    st.markdown("### 🎯 Advanced Options")
    st.markdown("Fine-tune your custom newsletter generation")

    # Override preferences for this newsletter
    st.markdown("#### 🔧 Override Preferences (for this newsletter only)")

    col1, col2 = st.columns(2)

    with col1:
        override_tone = st.selectbox(
            "Override tone",
            ["Use default", "professional", "casual", "technical"],
            help="Override your default tone setting for this newsletter",
        )

        override_length = st.selectbox(
            "Override article length",
            ["Use default", "short", "medium", "long"],
            help="Override your default length preference",
        )

    with col2:
        override_max_articles = st.number_input(
            "Override max articles",
            min_value=1,
            max_value=20,
            value=preferences.get("max_articles", 10) if preferences else 10,
            help="Override your default max articles setting",
        )

        include_trending_override = st.selectbox(
            "Include trending topics",
            ["Use default", "Yes", "No"],
            help="Override your trending topics setting",
        )

    # Content filtering options
    st.markdown("#### 🔍 Content Filtering")

    col1, col2 = st.columns(2)

    with col1:
        exclude_keywords = st.text_input(
            "Exclude keywords (comma-separated)",
            placeholder="politics, sports, celebrity",
            help="Keywords to avoid in content selection",
        )

    with col2:
        include_keywords = st.text_input(
            "Must include keywords (comma-separated)",
            placeholder="innovation, breakthrough, research",
            help="Keywords that must be present in selected content",
        )

    # Time range for content
    st.markdown("#### ⏰ Content Time Range")

    col1, col2 = st.columns(2)

    with col1:
        content_age = st.selectbox(
            "Content age",
            ["Last 24 hours", "Last 3 days", "Last week", "Last 2 weeks", "Last month"],
            index=2,  # Default to "Last week"
            help="How recent should the content be?",
        )

    with col2:
        priority_sources = st.text_input(
            "Priority sources (comma-separated)",
            placeholder="techcrunch.com, wired.com, nature.com",
            help="Preferred news sources (optional)",
        )

    # Store advanced options in session state
    st.session_state.advanced_options = {
        "override_tone": override_tone if override_tone != "Use default" else None,
        "override_length": override_length
        if override_length != "Use default"
        else None,
        "override_max_articles": override_max_articles,
        "include_trending_override": include_trending_override
        if include_trending_override != "Use default"
        else None,
        "exclude_keywords": [
            k.strip() for k in exclude_keywords.split(",") if k.strip()
        ]
        if exclude_keywords
        else [],
        "include_keywords": [
            k.strip() for k in include_keywords.split(",") if k.strip()
        ]
        if include_keywords
        else [],
        "content_age": content_age,
        "priority_sources": [
            s.strip() for s in priority_sources.split(",") if s.strip()
        ]
        if priority_sources
        else [],
    }


def show_generation_section():
    """Show newsletter generation and preview section"""

    st.markdown("### 🚀 Generate Your Newsletter")

    # Check if we have a prompt
    if not st.session_state.custom_prompt.strip():
        st.warning("⚠️ Please enter a custom prompt in the 'Create Prompt' tab first.")
        return

    # Show current prompt
    st.markdown("#### 📝 Your Prompt:")
    st.info(st.session_state.custom_prompt)

    # Generation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button(
            "🔍 Preview Newsletter", type="secondary", use_container_width=True
        ):
            with st.spinner("Generating preview..."):
                preferences = get_user_preferences()
                advanced_options = st.session_state.get("advanced_options", {})

                # Combine preferences with advanced options
                combined_preferences = preferences.copy() if preferences else {}
                if advanced_options.get("override_tone"):
                    combined_preferences["tone"] = advanced_options["override_tone"]
                if advanced_options.get("override_length"):
                    combined_preferences["preferred_length"] = advanced_options[
                        "override_length"
                    ]
                if advanced_options.get("override_max_articles"):
                    combined_preferences["max_articles"] = advanced_options[
                        "override_max_articles"
                    ]

                success, message, newsletter_data = generate_custom_newsletter(
                    st.session_state.custom_prompt, combined_preferences
                )

            if success:
                st.session_state.generated_newsletter = newsletter_data
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")

    with col2:
        if st.button("📧 Generate & Send", type="primary", use_container_width=True):
            with st.spinner("Generating and sending newsletter..."):
                preferences = get_user_preferences()
                advanced_options = st.session_state.get("advanced_options", {})

                # Combine preferences with advanced options
                combined_preferences = preferences.copy() if preferences else {}
                if advanced_options.get("override_tone"):
                    combined_preferences["tone"] = advanced_options["override_tone"]

                success, message, newsletter_data = generate_custom_newsletter(
                    st.session_state.custom_prompt, combined_preferences
                )

            if success and newsletter_data:
                # Send the newsletter
                newsletter_id = newsletter_data.get("newsletter_id")
                if newsletter_id:
                    send_success, send_message = send_newsletter(newsletter_id)
                    if send_success:
                        st.success(
                            f"✅ Newsletter generated and sent! Check your email."
                        )
                        st.balloons()
                    else:
                        st.error(
                            f"❌ Newsletter generated but sending failed: {send_message}"
                        )
                else:
                    st.error("❌ Newsletter generated but no ID returned")
            else:
                st.error(f"❌ {message}")

    with col3:
        if st.button("🔄 Clear & Start Over", use_container_width=True):
            st.session_state.custom_prompt = ""
            st.session_state.generated_newsletter = None
            if "advanced_options" in st.session_state:
                del st.session_state.advanced_options
            st.rerun()

    # Show preview if available
    if st.session_state.generated_newsletter:
        st.markdown("---")
        st.markdown("### 👁️ Newsletter Preview")

        newsletter = st.session_state.generated_newsletter

        # Newsletter metadata
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Articles", newsletter.get("article_count", 0))

        with col2:
            st.metric("Estimated Read Time", f"{newsletter.get('read_time', 5)} min")

        with col3:
            st.metric("Word Count", newsletter.get("word_count", 0))

        # Newsletter content preview
        if "content" in newsletter:
            st.markdown("#### 📄 Content Preview:")

            # Show title
            if "title" in newsletter:
                st.markdown(f"**{newsletter['title']}**")

            # Show summary or first few lines
            content = newsletter.get("content", "")
            if len(content) > 500:
                st.markdown(content[:500] + "...")
                st.markdown("*Preview truncated - full content will be in your email*")
            else:
                st.markdown(content)

        # Action buttons for preview
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📧 Send This Newsletter", type="primary"):
                newsletter_id = newsletter.get("newsletter_id")
                if newsletter_id:
                    with st.spinner("Sending newsletter..."):
                        success, message = send_newsletter(newsletter_id)

                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ No newsletter ID available")

        with col2:
            if st.button("📊 View Full Content"):
                st.info("🚧 Full content viewer coming soon!")


if __name__ == "__main__":
    main()
