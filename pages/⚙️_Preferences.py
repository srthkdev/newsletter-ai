"""
Newsletter AI - User Preferences Dashboard
"""
import streamlit as st
import requests
from typing import Dict, List, Any, Optional
import json

# Page configuration
st.set_page_config(
    page_title="Preferences - Newsletter AI",
    page_icon="⚙️",
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS
st.markdown("""
<style>
    .preference-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-message {
        background: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    .error-message {
        background: #fee2e2;
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ef4444;
        margin: 1rem 0;
    }
    .topic-chip {
        display: inline-block;
        background: #e0e7ff;
        color: #3730a3;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Available options
AVAILABLE_TOPICS = [
    "Technology", "Artificial Intelligence", "Business", "Startups",
    "Science", "Health", "Finance", "Marketing", "Productivity",
    "Innovation", "Cybersecurity", "Data Science", "Software Development",
    "Climate Change", "Space", "Biotechnology", "Cryptocurrency",
    "E-commerce", "Social Media", "Gaming", "Education", "Travel"
]

TONE_OPTIONS = {
    "professional": {
        "label": "Professional",
        "description": "Formal, business-oriented tone suitable for workplace reading"
    },
    "casual": {
        "label": "Casual",
        "description": "Friendly, conversational tone for relaxed reading"
    },
    "technical": {
        "label": "Technical",
        "description": "Detailed, technical language for in-depth understanding"
    }
}

FREQUENCY_OPTIONS = {
    "daily": {
        "label": "Daily",
        "description": "Get fresh content every day"
    },
    "every_2_days": {
        "label": "Every 2 Days",
        "description": "Receive newsletters every other day"
    },
    "weekly": {
        "label": "Weekly",
        "description": "Weekly digest of the most important content"
    },
    "monthly": {
        "label": "Monthly",
        "description": "Monthly comprehensive overview"
    }
}

def get_user_preferences() -> Optional[Dict[str, Any]]:
    """Get current user preferences from API"""
    try:
        # For now, we'll use session state to simulate user authentication
        # In a real app, this would use proper authentication
        user_id = st.session_state.get('user_id', 'demo_user')
        
        response = requests.get(
            f"{API_BASE_URL}/preferences/{user_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        st.error(f"Error loading preferences: {str(e)}")
        return None

def save_user_preferences(preferences: Dict[str, Any]) -> tuple[bool, str]:
    """Save user preferences to API"""
    try:
        user_id = st.session_state.get('user_id', 'demo_user')
        
        response = requests.put(
            f"{API_BASE_URL}/preferences/{user_id}",
            json=preferences,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Preferences saved successfully!"
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
        user_id = st.session_state.get('user_id', 'demo_user')
        
        response = requests.get(
            f"{API_BASE_URL}/preferences/{user_id}/recommendations",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("recommendations", [])
        else:
            return None
            
    except Exception as e:
        return None

def main():
    """Main preferences page"""
    
    # Header
    st.title("⚙️ Newsletter Preferences")
    st.markdown("Customize your newsletter experience with AI-powered personalization")
    
    # Initialize session state for preferences
    if 'preferences_changed' not in st.session_state:
        st.session_state.preferences_changed = False
    
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
            "include_trending": True
        }
    
    # Create tabs for different preference sections
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Topics & Content", "🎨 Style & Tone", "⏰ Delivery", "🤖 AI Recommendations"])
    
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
        if st.button("💾 Save All Preferences", type="primary", use_container_width=True):
            # Collect all preferences from session state
            preferences_to_save = {
                "topics": st.session_state.get('selected_topics', current_preferences.get('topics', [])),
                "tone": st.session_state.get('selected_tone', current_preferences.get('tone', 'professional')),
                "frequency": st.session_state.get('selected_frequency', current_preferences.get('frequency', 'weekly')),
                "custom_instructions": st.session_state.get('custom_instructions', current_preferences.get('custom_instructions', '')),
                "max_articles": st.session_state.get('max_articles', current_preferences.get('max_articles', 10)),
                "include_trending": st.session_state.get('include_trending', current_preferences.get('include_trending', True)),
                "preferred_length": st.session_state.get('preferred_length', current_preferences.get('preferred_length', 'medium')),
                "send_time": st.session_state.get('send_time', current_preferences.get('send_time', '09:00')),
                "timezone": st.session_state.get('timezone', current_preferences.get('timezone', 'UTC'))
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
    if 'selected_topics' not in st.session_state:
        st.session_state.selected_topics = current_preferences.get('topics', [])
    
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
        topics_html = "".join([f'<span class="topic-chip">{topic}</span>' for topic in st.session_state.selected_topics])
        st.markdown(topics_html, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please select at least one topic to receive personalized content.")
    
    st.markdown("---")
    
    # Content preferences
    st.markdown("#### Content Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_articles = st.slider(
            "Maximum articles per newsletter",
            min_value=3,
            max_value=20,
            value=current_preferences.get('max_articles', 10),
            help="How many articles should be included in each newsletter?",
            key='max_articles'
        )
    
    with col2:
        preferred_length = st.selectbox(
            "Preferred article length",
            options=["short", "medium", "long"],
            index=["short", "medium", "long"].index(current_preferences.get('preferred_length', 'medium')),
            help="Short: Quick summaries, Medium: Balanced content, Long: In-depth articles",
            key='preferred_length'
        )
    
    # Additional content options
    include_trending = st.checkbox(
        "Include trending topics",
        value=current_preferences.get('include_trending', True),
        help="Include currently trending topics even if not in your selected interests",
        key='include_trending'
    )
    
    # Custom instructions
    st.markdown("#### Custom Instructions")
    custom_instructions = st.text_area(
        "Additional preferences or instructions",
        value=current_preferences.get('custom_instructions', ''),
        placeholder="e.g., 'Focus on practical applications', 'Avoid political content', 'Include more case studies'...",
        help="Tell our AI agents any specific preferences for your newsletter content",
        key='custom_instructions'
    )

def show_style_preferences(current_preferences: Dict[str, Any]):
    """Show style and tone preferences"""
    
    st.markdown("### 🎨 Style & Tone Preferences")
    
    # Tone selection
    st.markdown("#### Newsletter Tone")
    st.markdown("Choose the writing style that best fits your reading preference:")
    
    # Initialize selected tone in session state
    if 'selected_tone' not in st.session_state:
        st.session_state.selected_tone = current_preferences.get('tone', 'professional')
    
    for tone_key, tone_info in TONE_OPTIONS.items():
        is_selected = st.session_state.selected_tone == tone_key
        
        if st.radio(
            "Select tone:",
            options=list(TONE_OPTIONS.keys()),
            format_func=lambda x: f"**{TONE_OPTIONS[x]['label']}** - {TONE_OPTIONS[x]['description']}",
            index=list(TONE_OPTIONS.keys()).index(st.session_state.selected_tone),
            key='selected_tone'
        ):
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
        """
    }
    
    selected_tone = st.session_state.get('selected_tone', 'professional')
    if selected_tone in tone_examples:
        st.markdown(tone_examples[selected_tone])

def show_delivery_preferences(current_preferences: Dict[str, Any]):
    """Show delivery and timing preferences"""
    
    st.markdown("### ⏰ Delivery Preferences")
    
    # Frequency selection
    st.markdown("#### Delivery Frequency")
    st.markdown("How often would you like to receive newsletters?")
    
    # Initialize selected frequency in session state
    if 'selected_frequency' not in st.session_state:
        st.session_state.selected_frequency = current_preferences.get('frequency', 'weekly')
    
    frequency_choice = st.radio(
        "Select frequency:",
        options=list(FREQUENCY_OPTIONS.keys()),
        format_func=lambda x: f"**{FREQUENCY_OPTIONS[x]['label']}** - {FREQUENCY_OPTIONS[x]['description']}",
        index=list(FREQUENCY_OPTIONS.keys()).index(st.session_state.selected_frequency),
        key='selected_frequency'
    )
    
    # Timing preferences
    st.markdown("#### Delivery Timing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        send_time = st.time_input(
            "Preferred send time",
            value=None,  # Will use default from current_preferences
            help="What time would you like to receive your newsletters?",
            key='send_time'
        )
    
    with col2:
        timezone = st.selectbox(
            "Timezone",
            options=["UTC", "EST", "PST", "GMT", "CET", "JST", "AEST"],
            index=0,  # Default to UTC
            help="Your local timezone for delivery scheduling",
            key='timezone'
        )
    
    # Delivery summary
    st.markdown("#### Delivery Summary")
    
    frequency_label = FREQUENCY_OPTIONS[st.session_state.selected_frequency]['label']
    
    st.info(f"""
    📅 **Your newsletter schedule:**
    - **Frequency:** {frequency_label}
    - **Time:** {send_time if send_time else 'Not set'}
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
            rec_type = rec.get('type', 'general')
            title = rec.get('title', 'Recommendation')
            description = rec.get('description', '')
            priority = rec.get('priority', 'medium')
            
            # Color code by priority
            if priority == 'high':
                border_color = '#ef4444'
                bg_color = '#fee2e2'
            elif priority == 'medium':
                border_color = '#f59e0b'
                bg_color = '#fef3c7'
            else:
                border_color = '#10b981'
                bg_color = '#d1fae5'
            
            st.markdown(f"""
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
            """, unsafe_allow_html=True)
            
            # Add action buttons for specific recommendations
            if rec_type == 'topics' and 'suggested_topics' in rec:
                st.markdown("**Suggested topics to add:**")
                suggested_topics = rec['suggested_topics']
                
                cols = st.columns(len(suggested_topics))
                for j, topic in enumerate(suggested_topics):
                    with cols[j]:
                        if st.button(f"Add {topic}", key=f"add_topic_{i}_{j}"):
                            if 'selected_topics' not in st.session_state:
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