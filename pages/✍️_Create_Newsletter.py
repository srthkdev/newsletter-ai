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

# Example prompts
EXAMPLE_PROMPTS = [
    {
        "title": "AI Breakthroughs Focus",
        "prompt": "Create a newsletter about the latest AI breakthroughs this week, focusing on practical applications and business impact. Use a professional tone and include 5-7 key articles.",
        "category": "Technology",
    },
    {
        "title": "Startup Funding Roundup",
        "prompt": "Generate a newsletter covering recent startup funding rounds and investment trends. Keep it casual and conversational, highlighting interesting companies and their stories.",
        "category": "Business",
    },
    {
        "title": "Climate Tech Innovation",
        "prompt": "Focus on climate technology innovations and sustainability breakthroughs. Include both scientific developments and business applications. Use a technical but accessible tone.",
        "category": "Science",
    },
    {
        "title": "Developer Tools & Trends",
        "prompt": "Create a newsletter for software developers covering new tools, frameworks, and programming trends. Include practical tips and code examples where relevant.",
        "category": "Technology",
    },
    {
        "title": "Health & Biotech Updates",
        "prompt": "Cover the latest in healthcare technology and biotechnology research. Focus on breakthrough treatments, medical devices, and health innovations that could impact patients.",
        "category": "Health",
    },
    {
        "title": "Fintech & Crypto News",
        "prompt": "Generate a newsletter about financial technology developments and cryptocurrency trends. Include regulatory updates and market analysis with a professional tone.",
        "category": "Finance",
    },
]


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


def generate_custom_newsletter(
    prompt: str, preferences: Optional[Dict[str, Any]] = None
) -> tuple[bool, str, Optional[Dict[str, Any]]]:
    """Generate newsletter from custom prompt"""
    try:
        user_id = st.session_state.get("user_id", "demo_user")

        payload = {
            "user_id": user_id,
            "custom_prompt": prompt,
            "send_immediately": False,  # Generate but don't send yet
        }

        if preferences:
            payload["preferences_override"] = preferences

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

    custom_prompt = st.text_area(
        "Custom Newsletter Prompt",
        value=st.session_state.custom_prompt,
        height=150,
        placeholder="""Example prompts:
        
• "Create a newsletter about AI breakthroughs this week with a technical tone"
• "Focus on startup funding news with a casual, conversational style"  
• "Cover cybersecurity trends with practical tips for developers"
• "Generate content about renewable energy innovations for business professionals"

Be specific about:
- Topics you want covered
- Tone/style preferences  
- Number of articles
- Any special focus areas""",
        help="Describe exactly what you want in your newsletter. Be as specific as possible!",
        key="prompt_input",
    )

    # Update session state
    st.session_state.custom_prompt = custom_prompt

    # Prompt enhancement suggestions
    if custom_prompt:
        st.markdown("#### 🔍 Prompt Analysis")

        # Simple analysis of the prompt
        word_count = len(custom_prompt.split())
        has_tone = any(
            tone in custom_prompt.lower()
            for tone in ["professional", "casual", "technical", "formal", "friendly"]
        )
        has_topics = any(
            topic in custom_prompt.lower()
            for topic in ["ai", "tech", "business", "startup", "science", "health"]
        )
        has_specifics = any(
            word in custom_prompt.lower()
            for word in ["focus", "include", "cover", "about", "regarding"]
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status = "✅" if word_count >= 10 else "⚠️"
            st.metric(
                "Word Count", word_count, help="Aim for 10+ words for better results"
            )
            st.markdown(
                f"{status} {'Good length' if word_count >= 10 else 'Could be longer'}"
            )

        with col2:
            status = "✅" if has_tone else "💡"
            st.markdown(
                f"**Tone Specified**\n{status} {'Yes' if has_tone else 'Consider adding tone'}"
            )

        with col3:
            status = "✅" if has_topics else "💡"
            st.markdown(
                f"**Topics Clear**\n{status} {'Yes' if has_topics else 'Be more specific'}"
            )

        with col4:
            status = "✅" if has_specifics else "💡"
            st.markdown(
                f"**Specific Focus**\n{status} {'Yes' if has_specifics else 'Add more details'}"
            )

        # Suggestions for improvement
        suggestions = []
        if word_count < 10:
            suggestions.append("Add more details about what you want to read")
        if not has_tone:
            suggestions.append("Specify a tone (professional, casual, technical)")
        if not has_topics:
            suggestions.append("Mention specific topics or industries")
        if not has_specifics:
            suggestions.append("Include specific focus areas or requirements")

        if suggestions:
            st.markdown("**💡 Suggestions to improve your prompt:**")
            for suggestion in suggestions:
                st.markdown(f"• {suggestion}")


def show_example_prompts():
    """Show example prompts that users can use"""

    st.markdown("### 📋 Example Prompts")
    st.markdown(
        "Click on any example to use it as a starting point for your custom newsletter"
    )

    # Group examples by category
    categories = {}
    for example in EXAMPLE_PROMPTS:
        category = example["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(example)

    # Display examples by category
    for category, examples in categories.items():
        st.markdown(f"#### {category}")

        for example in examples:
            with st.container():
                st.markdown(
                    f"""
                <div class="example-prompt">
                    <h5 style="margin: 0 0 0.5rem 0;">{example["title"]}</h5>
                    <p style="margin: 0; color: #6b7280;">{example["prompt"]}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"Use This", key=f"use_{example['title']}"):
                        st.session_state.custom_prompt = example["prompt"]
                        st.success(f"✅ Loaded: {example['title']}")
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
