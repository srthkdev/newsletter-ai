"""
Newsletter AI - User Preferences Dashboard
"""

import streamlit as st
import requests
import time
from typing import Dict, List, Any, Optional
import json

# Page configuration
st.set_page_config(
    page_title="Preferences - Newsletter AI", page_icon="⚙️", layout="wide"
)

# API Configuration
import os
API_BASE_URL = os.getenv("API_BASE_URL", "https://newsletter-ai-1ndi.onrender.com/api/v1")

# Custom CSS
st.markdown(
    """
<style>
    /* Hide Streamlit default elements */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    .preference-section {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        color: #1a202c;
    }
    
    .preference-section h3, .preference-section h4 {
        color: #1a202c;
    }
    
    .preference-section p {
        color: #2d3748;
    }
    
    .preference-section:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(102, 126, 234, 0.1);
        border-color: #667eea;
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
    
    .error-message {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        color: #991b1b;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #ef4444;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.1);
        animation: shake 0.5s ease;
    }
    
    .topic-chip {
        display: inline-block;
        background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
        color: #3730a3;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        margin: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .topic-chip:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff;
        border-color: #667eea;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(245, 158, 11, 0.1);
        color: #92400e;
    }
    
    .recommendation-card h4 {
        color: #92400e;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        color: #1a202c;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.15);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        display: block;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #2d3748;
        font-weight: 500;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* Enhanced form styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stSlider > div > div {
        background: linear-gradient(90deg, #e2e8f0, #667eea);
    }
    
    .stCheckbox > label {
        font-weight: 500;
        color: #374151;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Available options
AVAILABLE_TOPICS = [
    "Technology",
    "Artificial Intelligence",
    "Business",
    "Startups",
    "Science",
    "Health",
    "Finance",
    "Marketing",
    "Productivity",
    "Innovation",
    "Cybersecurity",
    "Data Science",
    "Software Development",
    "Climate Change",
    "Space",
    "Biotechnology",
    "Cryptocurrency",
    "E-commerce",
    "Social Media",
    "Gaming",
    "Education",
    "Travel",
]

TONE_OPTIONS = {
    "professional": {
        "label": "Professional",
        "description": "Formal, business-oriented tone suitable for workplace reading",
    },
    "casual": {
        "label": "Casual",
        "description": "Friendly, conversational tone for relaxed reading",
    },
    "technical": {
        "label": "Technical",
        "description": "Detailed, technical language for in-depth understanding",
    },
}

FREQUENCY_OPTIONS = {
    "daily": {"label": "Daily", "description": "Get fresh content every day"},
    "every_2_days": {
        "label": "Every 2 Days",
        "description": "Receive newsletters every other day",
    },
    "weekly": {
        "label": "Weekly",
        "description": "Weekly digest of the most important content",
    },
    "monthly": {"label": "Monthly", "description": "Monthly comprehensive overview"},
}


def get_auth_headers():
    """Get authentication headers for API requests"""
    session_token = st.session_state.get("session_token")
    if session_token:
        return {"Authorization": f"Bearer {session_token}"}
    return {}


def get_user_preferences() -> Optional[Dict[str, Any]]:
    """Get current user preferences from API"""
    try:
        auth_headers = get_auth_headers()
        if not auth_headers:
            st.error("Please log in to view your preferences")
            st.switch_page("streamlit_app.py")
            return None

        response = requests.get(
            f"{API_BASE_URL}/preferences/", 
            headers=auth_headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Your session has expired. Please log in again.")
            st.switch_page("streamlit_app.py")
            return None
        else:
            return None

    except Exception as e:
        st.error(f"Error loading preferences: {str(e)}")
        return None


def save_user_preferences(preferences: Dict[str, Any]) -> tuple[bool, str]:
    """Save user preferences to API"""
    try:
        auth_headers = get_auth_headers()
        if not auth_headers:
            return False, "Authentication required. Please log in."

        response = requests.put(
            f"{API_BASE_URL}/preferences/", 
            headers=auth_headers,
            json=preferences, 
            timeout=10
        )

        if response.status_code == 200:
            return True, "Preferences saved successfully!"
        elif response.status_code == 401:
            return False, "Your session has expired. Please log in again."
        else:
            error_data = response.json()
            return False, error_data.get("detail", "Failed to save preferences")

    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please make sure the API is running."
    except Exception as e:
        return False, f"Error saving preferences: {str(e)}"


def get_preference_recommendations() -> Optional[List[Dict[str, Any]]]:
    """Get AI-powered preference recommendations"""
    try:
        auth_headers = get_auth_headers()
        if not auth_headers:
            return None

        response = requests.get(
            f"{API_BASE_URL}/preferences/recommendations", 
            headers=auth_headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("recommendations", [])
        else:
            return None

    except Exception as e:
        return None


def calculate_setup_progress(preferences: Dict[str, Any]) -> float:
    """Calculate the setup progress based on completed preferences"""
    if not preferences or preferences.get("is_default", True):
        return 0.0
    
    progress_items = [
        len(preferences.get("topics", [])) > 0,  # Has topics
        preferences.get("tone") != "professional" or len(preferences.get("topics", [])) > 2,  # Has custom tone or multiple topics
        preferences.get("frequency") is not None,  # Has frequency
        preferences.get("max_articles", 0) > 0,  # Has article limit
        len(preferences.get("custom_instructions", "")) > 0 or preferences.get("include_trending", False),  # Has custom instructions or trending
    ]
    
    return sum(progress_items) / len(progress_items)


def main():
    """Enhanced main preferences page with modern UI and interactive features"""
    # Check authentication
    session_token = st.session_state.get("session_token")
    if not session_token:
        st.error("🔒 Please log in to access your preferences")
        if st.button("Go to Login", type="primary"):
            st.switch_page("streamlit_app.py")
        return

    # Header with modern styling
    st.markdown(
        """
    <div class="section-header">
        <h1>⚙️ Newsletter Preferences</h1>
        <p>Customize your AI-powered newsletter experience with advanced personalization</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Initialize session state for preferences
    if "preferences_changed" not in st.session_state:
        st.session_state.preferences_changed = False
    if "last_saved" not in st.session_state:
        st.session_state.last_saved = None

    # Load current preferences
    current_preferences = get_user_preferences()

    # If no preferences exist, use defaults
    if not current_preferences:
        current_preferences = {
            "topics": ["Technology", "Business"],
            "tone": "professional",
            "frequency": "weekly",
            "custom_instructions": "",
            "max_articles": 10,
            "include_trending": True,
        }

    # Show current stats if preferences exist
    if current_preferences and not current_preferences.get("is_default", True):
        st.markdown(
            f"""
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{len(current_preferences.get("topics", []))}</span>
                <div class="stat-label">Topics Selected</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">🎭</span>
                <div class="stat-label">{current_preferences.get("tone", "Not set").title()} Tone</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">⏰</span>
                <div class="stat-label">{current_preferences.get("frequency", "Not set").title()}</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{current_preferences.get("max_articles", 0)}</span>
                <div class="stat-label">Max Articles</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    
    # Progress indicator
    progress_value = calculate_setup_progress(current_preferences)
    if progress_value < 1.0:
        st.progress(progress_value)
        st.info(f"🚧 Setup Progress: {int(progress_value * 100)}% complete. Complete all sections for optimal experience.")
    else:
        st.success("✓ Your newsletter preferences are fully configured!")

    # Create tabs for different preference sections
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📚 Topics & Content",
            "🎨 Style & Tone",
            "⏰ Delivery",
            "🤖 AI Recommendations",
        ]
    )

    with tab1:
        show_topics_preferences(current_preferences)

    with tab2:
        show_style_preferences(current_preferences)

    with tab3:
        show_delivery_preferences(current_preferences)

    with tab4:
        show_ai_recommendations()

    # Save preferences button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button(
            "💾 Save All Preferences", type="primary", use_container_width=True
        ):
            # Collect all preferences from session state
            preferences_to_save = {
                "topics": st.session_state.get(
                    "selected_topics", current_preferences.get("topics", [])
                ),
                "tone": st.session_state.get(
                    "selected_tone", current_preferences.get("tone", "professional")
                ),
                "frequency": st.session_state.get(
                    "selected_frequency", current_preferences.get("frequency", "weekly")
                ),
                "custom_instructions": st.session_state.get(
                    "custom_instructions",
                    current_preferences.get("custom_instructions", ""),
                ),
                "max_articles": st.session_state.get(
                    "max_articles", current_preferences.get("max_articles", 10)
                ),
                "include_trending": st.session_state.get(
                    "include_trending",
                    current_preferences.get("include_trending", True),
                ),
                "preferred_length": st.session_state.get(
                    "preferred_length",
                    current_preferences.get("preferred_length", "medium"),
                ),
                "send_time": st.session_state.get(
                    "send_time", current_preferences.get("send_time", "09:00")
                ),
                "timezone": st.session_state.get(
                    "timezone", current_preferences.get("timezone", "UTC")
                ),
            }

            with st.spinner("Saving preferences..."):
                success, message = save_user_preferences(preferences_to_save)

            if success:
                st.success(f"✅ {message}")
                st.session_state.preferences_changed = False
                # Trigger a rerun to refresh the page
                st.rerun()
            else:
                st.error(f"❌ {message}")


def show_topics_preferences(current_preferences: Dict[str, Any]):
    """Show topics and content preferences"""

    st.markdown("### 📚 Topics & Content Preferences")

    # Topic selection
    st.markdown("#### Select Your Interests")
    st.markdown("Choose the topics you'd like to receive content about:")

    # Initialize selected topics in session state
    if "selected_topics" not in st.session_state:
        st.session_state.selected_topics = current_preferences.get("topics", [])

    # Create columns for topic selection
    cols = st.columns(3)

    for i, topic in enumerate(AVAILABLE_TOPICS):
        col_idx = i % 3
        with cols[col_idx]:
            is_selected = topic in st.session_state.selected_topics

            if st.checkbox(topic, value=is_selected, key=f"topic_{topic}"):
                if topic not in st.session_state.selected_topics:
                    st.session_state.selected_topics.append(topic)
                    st.session_state.preferences_changed = True
            else:
                if topic in st.session_state.selected_topics:
                    st.session_state.selected_topics.remove(topic)
                    st.session_state.preferences_changed = True

    # Show selected topics
    if st.session_state.selected_topics:
        st.markdown("#### Selected Topics:")
        topics_html = "".join(
            [
                f'<span class="topic-chip">{topic}</span>'
                for topic in st.session_state.selected_topics
            ]
        )
        st.markdown(topics_html, unsafe_allow_html=True)
    else:
        st.warning(
            "⚠️ Please select at least one topic to receive personalized content."
        )

    st.markdown("---")

    # Content preferences
    st.markdown("#### Content Preferences")

    col1, col2 = st.columns(2)

    with col1:
        max_articles = st.slider(
            "Maximum articles per newsletter",
            min_value=3,
            max_value=20,
            value=current_preferences.get("max_articles", 10),
            help="How many articles should be included in each newsletter?",
            key="max_articles",
        )

    with col2:
        preferred_length = st.selectbox(
            "Preferred article length",
            options=["short", "medium", "long"],
            index=["short", "medium", "long"].index(
                current_preferences.get("preferred_length", "medium")
            ),
            help="Short: Quick summaries, Medium: Balanced content, Long: In-depth articles",
            key="preferred_length",
        )

    # Additional content options
    include_trending = st.checkbox(
        "Include trending topics",
        value=current_preferences.get("include_trending", True),
        help="Include currently trending topics even if not in your selected interests",
        key="include_trending",
    )

    # Custom instructions
    st.markdown("#### Custom Instructions")
    custom_instructions = st.text_area(
        "Additional preferences or instructions",
        value=current_preferences.get("custom_instructions", ""),
        placeholder="e.g., 'Focus on practical applications', 'Avoid political content', 'Include more case studies'...",
        help="Tell our AI agents any specific preferences for your newsletter content",
        key="custom_instructions",
    )


def show_style_preferences(current_preferences: Dict[str, Any]):
    """Show style and tone preferences"""

    st.markdown("### 🎨 Style & Tone Preferences")

    # Tone selection
    st.markdown("#### Newsletter Tone")
    st.markdown("Choose the writing style that best fits your reading preference:")

    # Initialize selected tone in session state
    if "selected_tone" not in st.session_state:
        st.session_state.selected_tone = current_preferences.get("tone", "professional")

    # Single radio button for tone selection
    selected_tone = st.radio(
        "Select tone:",
        options=list(TONE_OPTIONS.keys()),
        format_func=lambda x: f"**{TONE_OPTIONS[x]['label']}** - {TONE_OPTIONS[x]['description']}",
        index=list(TONE_OPTIONS.keys()).index(st.session_state.selected_tone),
        key="tone_selection",
    )
    
    # Update session state if selection changed
    if selected_tone != st.session_state.selected_tone:
        st.session_state.selected_tone = selected_tone
        st.session_state.preferences_changed = True

    # Tone preview
    st.markdown("#### Tone Preview")

    tone_examples = {
        "professional": """
        **Professional Tone Example:**
        "This week's developments in artificial intelligence demonstrate significant progress in enterprise applications. 
        Companies are increasingly adopting AI-driven solutions to optimize operational efficiency and enhance customer experience."
        """,
        "casual": """
        **Casual Tone Example:**
        "AI is having a moment! This week we saw some pretty cool stuff happening in the tech world. 
        Companies are jumping on the AI bandwagon left and right, and honestly, it's making things way more interesting."
        """,
        "technical": """
        **Technical Tone Example:**
        "Recent advances in transformer architectures and attention mechanisms have yielded substantial improvements in model performance. 
        The implementation of sparse attention patterns has reduced computational complexity while maintaining accuracy metrics."
        """,
    }

    selected_tone = st.session_state.get("selected_tone", "professional")
    if selected_tone in tone_examples:
        st.markdown(tone_examples[selected_tone])


def show_delivery_preferences(current_preferences: Dict[str, Any]):
    """Show delivery and timing preferences"""

    st.markdown("### ⏰ Delivery Preferences")

    # Frequency selection
    st.markdown("#### Delivery Frequency")
    st.markdown("How often would you like to receive newsletters?")

    # Initialize selected frequency in session state
    if "selected_frequency" not in st.session_state:
        st.session_state.selected_frequency = current_preferences.get(
            "frequency", "weekly"
        )

    frequency_choice = st.radio(
        "Select frequency:",
        options=list(FREQUENCY_OPTIONS.keys()),
        format_func=lambda x: f"**{FREQUENCY_OPTIONS[x]['label']}** - {FREQUENCY_OPTIONS[x]['description']}",
        index=list(FREQUENCY_OPTIONS.keys()).index(st.session_state.selected_frequency),
        key="selected_frequency",
    )

    # Timing preferences
    st.markdown("#### Delivery Timing")

    col1, col2 = st.columns(2)

    with col1:
        send_time = st.time_input(
            "Preferred send time",
            value=None,  # Will use default from current_preferences
            help="What time would you like to receive your newsletters?",
            key="send_time",
        )

    with col2:
        timezone = st.selectbox(
            "Timezone",
            options=["UTC", "EST", "PST", "GMT", "CET", "JST", "AEST"],
            index=0,  # Default to UTC
            help="Your local timezone for delivery scheduling",
            key="timezone",
        )

    # Delivery summary
    st.markdown("#### Delivery Summary")

    frequency_label = FREQUENCY_OPTIONS[st.session_state.selected_frequency]["label"]

    st.info(f"""
    📅 **Your newsletter schedule:**
    - **Frequency:** {frequency_label}
    - **Time:** {send_time if send_time else "Not set"}
    - **Timezone:** {timezone}
    
    You can change these settings anytime!
    """)


def show_ai_recommendations():
    """Show AI-powered preference recommendations"""

    st.markdown("### 🤖 AI-Powered Recommendations")
    st.markdown("Get personalized suggestions to improve your newsletter experience")

    # Load recommendations
    with st.spinner("Getting AI recommendations..."):
        recommendations = get_preference_recommendations()

    if recommendations:
        st.markdown("#### Recommendations for You")

        for i, rec in enumerate(recommendations):
            rec_type = rec.get("type", "general")
            title = rec.get("title", "Recommendation")
            description = rec.get("description", "")
            priority = rec.get("priority", "medium")

            # Color code by priority
            if priority == "high":
                border_color = "#ef4444"
                bg_color = "#fee2e2"
            elif priority == "medium":
                border_color = "#f59e0b"
                bg_color = "#fef3c7"
            else:
                border_color = "#10b981"
                bg_color = "#d1fae5"

            st.markdown(
                f"""
            <div style="
                background: {bg_color};
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid {border_color};
                margin: 1rem 0;
            ">
                <h4 style="margin: 0 0 0.5rem 0;">{title}</h4>
                <p style="margin: 0;">{description}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Add action buttons for specific recommendations
            if rec_type == "topics" and "suggested_topics" in rec:
                st.markdown("**Suggested topics to add:**")
                suggested_topics = rec["suggested_topics"]

                cols = st.columns(len(suggested_topics))
                for j, topic in enumerate(suggested_topics):
                    with cols[j]:
                        if st.button(f"Add {topic}", key=f"add_topic_{i}_{j}"):
                            if "selected_topics" not in st.session_state:
                                st.session_state.selected_topics = []
                            if topic not in st.session_state.selected_topics:
                                st.session_state.selected_topics.append(topic)
                                st.success(f"Added {topic} to your topics!")
                                st.rerun()

    else:
        st.info("""
        🔍 **No recommendations available yet**
        
        AI recommendations will appear here once you:
        - Set up your initial preferences
        - Receive a few newsletters
        - Interact with the content
        
        Our AI agents will analyze your engagement patterns and suggest optimizations!
        """)

    # Manual preference analysis
    st.markdown("---")
    st.markdown("#### Analyze My Preferences")

    if st.button("🔍 Get Preference Analysis", use_container_width=True):
        with st.spinner("Analyzing your preferences..."):
            # This would call the preference agent for analysis
            st.info("""
            🧠 **Preference Analysis** (Demo)
            
            Based on your current settings:
            - **Topic Diversity:** Good variety of interests selected
            - **Engagement Potential:** High - your topics align with trending content
            - **Frequency Match:** Weekly frequency is optimal for your topic selection
            - **Tone Consistency:** Professional tone matches your topic preferences
            
            **Suggestions:**
            - Consider adding "Innovation" to complement your tech interests
            - Your current settings should provide excellent engagement
            """)


if __name__ == "__main__":
    main()
