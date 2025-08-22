"""
Newsletter AI - Custom Newsletter Creation
"""

import streamlit as st
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
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
    /* Hide Streamlit default elements */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    .create-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .prompt-section {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .prompt-section:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(102, 126, 234, 0.1);
        border-color: #667eea;
    }
    
    .example-prompt {
        background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .example-prompt:hover {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff;
        transform: scale(1.02);
        border-color: #667eea;
        box-shadow: 0 6px 15px rgba(102, 126, 234, 0.3);
    }
    
    .example-category {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .success-message {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #10b981;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.1);
        animation: slideIn 0.3s ease;
    }
    
    .info-message {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        color: #1e40af;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
    }
    
    .warning-message {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #92400e;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(245, 158, 11, 0.1);
    }
    
    .generation-status {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .preview-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .stats-row {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-item {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        text-align: center;
        min-width: 120px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .prompt-tips {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #22c55e;
        margin: 1rem 0;
    }
    
    .advanced-option {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .advanced-option:hover {
        border-color: #667eea;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.1);
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Enhanced text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem;
        font-size: 1rem;
        line-height: 1.6;
        transition: border-color 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button enhancements */
    .stButton > button {
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .create-header {
            padding: 1.5rem;
        }
        
        .prompt-section {
            padding: 1.5rem;
        }
        
        .stats-row {
            flex-direction: column;
        }
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
    """Enhanced custom newsletter creation page with modern UI"""

    # Enhanced header
    st.markdown(
        """
    <div class="create-header">
        <h1>✍️ Create Custom Newsletter</h1>
        <p>Tell our AI agents exactly what kind of newsletter you want to receive</p>
        <p><strong>Powered by Portia AI</strong> • Research • Writing • Custom Prompt Processing</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Load user preferences
    preferences = get_user_preferences()

    # Initialize session state
    if "custom_prompt" not in st.session_state:
        st.session_state.custom_prompt = ""
    if "generated_newsletter" not in st.session_state:
        st.session_state.generated_newsletter = None
    if "prompt_history" not in st.session_state:
        st.session_state.prompt_history = []
    if "generation_progress" not in st.session_state:
        st.session_state.generation_progress = 0

    # Progress indicator for newsletter creation
    if st.session_state.generation_progress > 0:
        progress_col1, progress_col2 = st.columns([3, 1])
        
        with progress_col1:
            st.progress(st.session_state.generation_progress)
        
        with progress_col2:
            st.write(f"{int(st.session_state.generation_progress * 100)}%")
        
        if st.session_state.generation_progress < 1.0:
            st.info("🤖 AI agents are working on your newsletter...")

    # Main content tabs with enhanced UI
    tab1, tab2, tab3, tab4 = st.tabs(
        ["✍️ Create Prompt", "📚 Examples", "🎯 Advanced Options", "📊 Prompt History"]
    )

    with tab1:
        show_prompt_creation(preferences)

    with tab2:
        show_example_prompts()

    with tab3:
        show_advanced_options(preferences)
        
    with tab4:
        show_prompt_history()

    # Generation and preview section
    st.markdown("---")
    show_generation_section()


def show_prompt_creation(preferences: Optional[Dict[str, Any]]):
    """Show the enhanced prompt creation interface"""

    st.markdown(
        """
    <div class="prompt-section">
        <h3>💭 Describe Your Perfect Newsletter</h3>
        <p>Our AI agents will use your description to research, curate, and write a personalized newsletter just for you.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Current preferences context with enhanced display
    if preferences and not preferences.get("is_default", False):
        st.markdown(
            f"""
        <div class="info-message">
            <strong>📋 Your Current Preferences</strong><br>
            <strong>Topics:</strong> {', '.join(preferences.get('topics', []))}<br>
            <strong>Tone:</strong> {preferences.get('tone', 'Not set').title()}<br>
            <strong>Frequency:</strong> {preferences.get('frequency', 'Not set').replace('_', ' ').title()}<br>
            <strong>Max Articles:</strong> {preferences.get('max_articles', 'Not set')}<br>
            <em>These preferences will be combined with your custom prompt for optimal results.</em>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
        <div class="warning-message">
            <strong>⚠️ No Preferences Set</strong><br>
            You haven't set up preferences yet. Your custom prompt will use default settings.
            <a href="/pages/⚙️_Preferences.py" target="_self">Set up preferences first</a> for better results.
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Enhanced prompt input with tips
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🎯 What would you like your newsletter to focus on?")

        # Load placeholders from API
        _, placeholders = load_example_prompts()
        
        # Create enhanced placeholder text
        placeholder_text = "Examples:\n\n"
        for i, placeholder in enumerate(placeholders[:3], 1):
            placeholder_text += f"\u2022 \"{placeholder}\"\n"
        
        placeholder_text += "\nBe specific about topics, tone, focus areas, and any special requirements..."

        custom_prompt = st.text_area(
            "Your Custom Prompt",
            value=st.session_state.custom_prompt,
            height=200,
            placeholder=placeholder_text,
            help="Describe exactly what you want in your newsletter. Be as specific as possible!",
            key="prompt_textarea",
        )

        # Update session state
        if custom_prompt != st.session_state.custom_prompt:
            st.session_state.custom_prompt = custom_prompt
            
        # Character counter and validation
        char_count = len(custom_prompt)
        if char_count > 0:
            if char_count < 20:
                st.warning(f"📏 {char_count} characters - Try to be more specific for better results")
            elif char_count > 500:
                st.warning(f"📏 {char_count} characters - Consider making your prompt more concise")
            else:
                st.success(f"✓ {char_count} characters - Good prompt length!")
    
    with col2:
        st.markdown(
            """
        <div class="prompt-tips">
            <h4>💡 Writing Tips</h4>
            <ul>
                <li><strong>Be Specific:</strong> Mention exact topics or themes</li>
                <li><strong>Set the Tone:</strong> Professional, casual, technical, etc.</li>
                <li><strong>Mention Sources:</strong> Prefer certain websites or publications</li>
                <li><strong>Time Frame:</strong> This week, recent, trending, etc.</li>
                <li><strong>Length:</strong> Brief summaries or in-depth articles</li>
                <li><strong>Special Focus:</strong> Startups, research, industry news</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )
        
        # Quick topic buttons
        st.markdown("#### ⚡ Quick Topic Ideas")
        
        quick_topics = [
            "AI breakthroughs this week",
            "Startup funding news", 
            "Tech product launches",
            "Science discoveries",
            "Business trends"
        ]
        
        for topic in quick_topics:
            if st.button(f"🔄 {topic}", key=f"quick_{topic}", use_container_width=True):
                st.session_state.custom_prompt = topic
                st.rerun()

    # Real-time prompt enhancement preview
    if custom_prompt and len(custom_prompt) > 10:
        with st.expander("🤖 AI Enhancement Preview", expanded=False):
            st.info("🚧 This feature shows how our Custom Prompt Agent will enhance your prompt")
            
            # Simulate prompt enhancement
            enhanced_preview = f"""
            **Original Prompt:** {custom_prompt}
            
            **Enhanced by AI:**
            Based on your request and preferences, I'll create a newsletter focusing on {custom_prompt.lower()}. 
            I'll research the latest developments, filter for quality content, and present it in a 
            {preferences.get('tone', 'professional') if preferences else 'professional'} tone 
            suitable for your interests.
            
            **Research Strategy:** Tavily API search + content filtering
            **Writing Style:** {preferences.get('tone', 'Professional') if preferences else 'Professional'} tone with clear structure
            **Content Focus:** Recent articles (last 3 days) with high relevance scores
            """
            
            st.markdown(enhanced_preview)


def show_prompt_history():
    """Show prompt history and allow reuse of previous prompts"""
    
    st.markdown(
        """
    <div class="prompt-section">
        <h3>📊 Your Prompt History</h3>
        <p>Review and reuse your previous newsletter prompts</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    if not st.session_state.prompt_history:
        st.info("📜 No prompt history yet. Create your first custom newsletter to see your prompts here!")
        return
    
    st.markdown(f"### 🗓️ {len(st.session_state.prompt_history)} Previous Prompts")
    
    for i, prompt_data in enumerate(reversed(st.session_state.prompt_history), 1):
        with st.expander(f"Prompt #{i}: {prompt_data.get('preview', 'Custom Newsletter')[:50]}..."):
            st.markdown(f"**Prompt:** {prompt_data.get('prompt', 'N/A')}")
            st.markdown(f"**Created:** {prompt_data.get('created_at', 'Unknown')}")
            
            if prompt_data.get('success', False):
                st.success("✓ Successfully generated")
            else:
                st.error("❌ Generation failed")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"🔄 Reuse Prompt", key=f"reuse_{i}"):
                    st.session_state.custom_prompt = prompt_data.get('prompt', '')
                    st.success("✓ Prompt loaded! Switch to 'Create Prompt' tab to use it.")
            
            with col2:
                if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                    st.session_state.prompt_history.remove(prompt_data)
                    st.rerun()

    # Get current custom prompt
    custom_prompt = st.session_state.custom_prompt

    # Only show analysis if we have a prompt and we're in the right context
    if custom_prompt and len(custom_prompt.strip()) > 10:
        st.markdown("#### 🔍 Quick Analysis")
        
        char_count = len(custom_prompt)
        word_count = len(custom_prompt.split())
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Characters", char_count)
        with col2:
            st.metric("Words", word_count)
            
        if word_count < 5:
            st.warning("⚠️ This prompt seems quite short for optimal results")
        elif word_count > 100:
            st.info("📝 This is a detailed prompt - good for specific requests")
        else:
            st.success("✅ Good prompt length for newsletter generation")


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
