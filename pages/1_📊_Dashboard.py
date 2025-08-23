"""
Newsletter AI - Main Dashboard
"""

import streamlit as st
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Dashboard - Newsletter AI", page_icon="📊", layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS
st.markdown(
    """
<style>
    .dashboard-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        color: #1a202c;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
        color: #1a202c;
    }
    .newsletter-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        color: #1a202c;
    }
    .newsletter-item h4 {
        color: #1a202c;
        margin-bottom: 0.5rem;
    }
    .newsletter-item p {
        color: #2d3748;
        margin: 0.25rem 0;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .status-sent {
        background: #d1fae5;
        color: #065f46;
    }
    .status-draft {
        background: #fef3c7;
        color: #92400e;
    }
    .status-scheduled {
        background: #dbeafe;
        color: #1e40af;
    }
</style>
""",
    unsafe_allow_html=True,
)


def get_auth_headers():
    """Get authentication headers for API requests"""
    session_token = st.session_state.get("session_token")
    if session_token:
        return {"Authorization": f"Bearer {session_token}"}
    return {}


def get_user_info() -> Optional[Dict[str, Any]]:
    """Get current user information"""
    try:
        auth_headers = get_auth_headers()
        if not auth_headers:
            st.error("Please log in to view your dashboard")
            st.switch_page("streamlit_app.py")
            return None
            
        response = requests.get(
            f"{API_BASE_URL}/users/me", 
            headers=auth_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Your session has expired. Please log in again.")
            st.switch_page("streamlit_app.py")
            return None
        return None
    except Exception:
        return None


def get_user_preferences() -> Optional[Dict[str, Any]]:
    try:
        auth_headers = get_auth_headers()
        if not auth_headers:
            return None
            
        response = requests.get(
            f"{API_BASE_URL}/preferences/", 
            headers=auth_headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def get_newsletter_history() -> List[Dict[str, Any]]:
    """Get user's newsletter history from API"""
    try:
        auth_headers = get_auth_headers()
        if not auth_headers:
            return []
            
        response = requests.get(
            f"{API_BASE_URL}/newsletters/", 
            headers=auth_headers,
            params={"limit": 20},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            newsletters = data.get("newsletters", [])
            
            # Process the newsletter data
            processed_newsletters = []
            for newsletter in newsletters:
                processed = {
                    "id": newsletter.get("id"),
                    "title": newsletter.get("title", "Untitled Newsletter"),
                    "status": newsletter.get("status", "unknown"),
                    "sent_date": newsletter.get("sent_at") or newsletter.get("created_at"),
                    "topics": newsletter.get("topics", []),
                    "article_count": newsletter.get("article_count", 0),
                    "open_rate": newsletter.get("open_rate", 0.0),
                    "click_rate": newsletter.get("click_rate", 0.0),
                    "summary": newsletter.get("summary", "")
                }
                processed_newsletters.append(processed)
            
            return processed_newsletters
        elif response.status_code == 401:
            st.error("Your session has expired. Please log in again.")
            st.switch_page("streamlit_app.py")
            return []
        else:
            st.error(f"Failed to fetch newsletters: {response.status_code}")
            return []
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to server. Please make sure the API is running.")
        return []
    except Exception as e:
        st.error(f"Error fetching newsletters: {str(e)}")
        return []


def get_dashboard_metrics() -> Dict[str, Any]:
    """Get dashboard metrics"""
    newsletters = get_newsletter_history()

    if not newsletters:
        return {
            "total_newsletters": 0,
            "avg_open_rate": 0,
            "avg_click_rate": 0,
            "total_articles": 0,
        }

    total_newsletters = len(newsletters)
    avg_open_rate = sum(n.get("open_rate", 0) for n in newsletters) / total_newsletters
    avg_click_rate = (
        sum(n.get("click_rate", 0) for n in newsletters) / total_newsletters
    )
    total_articles = sum(n.get("article_count", 0) for n in newsletters)

    return {
        "total_newsletters": total_newsletters,
        "avg_open_rate": round(avg_open_rate, 1),
        "avg_click_rate": round(avg_click_rate, 1),
        "total_articles": total_articles,
    }


def send_newsletter_now() -> tuple[bool, str]:
    """Trigger immediate newsletter generation and sending"""
    try:
        auth_headers = get_auth_headers()
        if not auth_headers:
            return False, "Authentication required. Please log in."

        response = requests.post(
            f"{API_BASE_URL}/newsletters/generate?send_immediately=true",
            headers=auth_headers,
            timeout=60,  # Increased timeout for newsletter generation
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return True, data.get("message", "Newsletter generated and sent successfully!")
            else:
                return False, data.get("error", "Failed to generate newsletter")
        elif response.status_code == 401:
            return False, "Your session has expired. Please log in again."
        else:
            error_data = response.json()
            return False, error_data.get("detail", "Failed to generate newsletter")

    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please make sure the API is running."
    except Exception as e:
        return False, f"Error generating newsletter: {str(e)}"


def rate_newsletter(newsletter_id: str, rating: int, feedback: str = None) -> tuple[bool, str]:
    """Rate a newsletter"""
    try:
        user_id = st.session_state.get("user_id", 1)  # Default to 1 for demo
        
        response = requests.post(
            f"{API_BASE_URL}/newsletters/rate",
            params={
                "user_id": user_id,
                "newsletter_id": newsletter_id,
                "rating": rating,
                "feedback": feedback
            },
            timeout=10,
        )
        
        if response.status_code == 200:
            return True, "Newsletter rated successfully!"
        else:
            error_data = response.json()
            return False, error_data.get("detail", "Failed to rate newsletter")
            
    except Exception as e:
        return False, f"Error rating newsletter: {str(e)}"


def get_newsletter_rating(newsletter_id: str) -> Optional[Dict[str, Any]]:
    """Get existing rating for a newsletter"""
    try:
        user_id = st.session_state.get("user_id", 1)
        
        response = requests.get(
            f"{API_BASE_URL}/newsletters/rating/{user_id}/{newsletter_id}",
            timeout=10,
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("rating")
        return None
        
    except Exception:
        return None


def display_star_rating(newsletter_id: str, current_rating: int = 0) -> Optional[int]:
    """Display interactive star rating"""
    stars = ["⭐" if i < current_rating else "☆" for i in range(5)]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    rating = None
    
    with col1:
        if st.button(f"{'⭐' if current_rating >= 1 else '☆'}", key=f"star1_{newsletter_id}", help="1 star"):
            rating = 1
    with col2:
        if st.button(f"{'⭐' if current_rating >= 2 else '☆'}", key=f"star2_{newsletter_id}", help="2 stars"):
            rating = 2
    with col3:
        if st.button(f"{'⭐' if current_rating >= 3 else '☆'}", key=f"star3_{newsletter_id}", help="3 stars"):
            rating = 3
    with col4:
        if st.button(f"{'⭐' if current_rating >= 4 else '☆'}", key=f"star4_{newsletter_id}", help="4 stars"):
            rating = 4
    with col5:
        if st.button(f"{'⭐' if current_rating >= 5 else '☆'}", key=f"star5_{newsletter_id}", help="5 stars"):
            rating = 5
    
    return rating


def main():
    """Main dashboard page"""
    # Check authentication
    session_token = st.session_state.get("session_token")
    if not session_token:
        st.error("🔒 Please log in to access your dashboard")
        if st.button("Go to Login", type="primary"):
            st.switch_page("streamlit_app.py")
        return

    # Get user information
    user_info = get_user_info()
    
    # Header with user information
    if user_info:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.title("📊 Newsletter Dashboard")
            st.markdown("Your personalized newsletter command center")
        
        with col2:
            user_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            if not user_name:
                user_name = user_info.get('email', 'User')
            
            st.markdown(
                f"""
            <div style="text-align: right; padding: 1rem; background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 10px; margin-bottom: 1rem;">
                <h4 style="color: #1a202c; margin: 0;">👋 Welcome, {user_name}!</h4>
                <p style="color: #6b7280; margin: 0.25rem 0 0 0; font-size: 0.9rem;">{user_info.get('email', '')}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        st.title("📊 Newsletter Dashboard")
        st.markdown("Your personalized newsletter command center")

    # Load user preferences
    preferences = get_user_preferences()

    if not preferences or preferences.get("is_default", False):
        st.warning("""
        ⚠️ **Setup Required**
        
        You haven't set up your preferences yet! Visit the **Preferences** page to:
        - Choose your topics of interest
        - Set your preferred tone and frequency
        - Customize your newsletter experience
        """)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(
                "⚙️ Set Up Preferences", type="primary", use_container_width=True
            ):
                st.switch_page("pages/⚙️_Preferences.py")

    # Dashboard metrics
    st.markdown("### 📈 Your Newsletter Stats")

    metrics = get_dashboard_metrics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="margin: 0; color: #667eea;">{}</h3>
            <p style="margin: 0; color: #6b7280;">Total Newsletters</p>
        </div>
        """.format(metrics["total_newsletters"]),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="margin: 0; color: #10b981;">{}%</h3>
            <p style="margin: 0; color: #6b7280;">Avg Open Rate</p>
        </div>
        """.format(metrics["avg_open_rate"]),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="margin: 0; color: #f59e0b;">{}%</h3>
            <p style="margin: 0; color: #6b7280;">Avg Click Rate</p>
        </div>
        """.format(metrics["avg_click_rate"]),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="margin: 0; color: #8b5cf6;">{}</h3>
            <p style="margin: 0; color: #6b7280;">Articles Read</p>
        </div>
        """.format(metrics["total_articles"]),
            unsafe_allow_html=True,
        )

    # Quick actions
    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "📧 Send Newsletter Now", type="primary", use_container_width=True
        ):
            with st.spinner("Generating your newsletter..."):
                success, message = send_newsletter_now()

            if success:
                st.success(f"✅ {message}")
                st.balloons()
                # Refresh the page to show new newsletter
                st.rerun()
            else:
                st.error(f"❌ {message}")

    with col2:
        if st.button("⚙️ Update Preferences", use_container_width=True):
            st.switch_page("pages/⚙️_Preferences.py")

    with col3:
        if st.button("✍️ Custom Newsletter", use_container_width=True):
            st.switch_page("pages/✍️_Create_Newsletter.py")

    # Current preferences summary
    if preferences and not preferences.get("is_default", False):
        st.markdown("### 🎯 Your Current Preferences")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"""
            <div class="dashboard-card">
                <h4>📚 Topics ({len(preferences.get("topics", []))})</h4>
                <p>{", ".join(preferences.get("topics", ["None selected"]))}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
            <div class="dashboard-card">
                <h4>🎨 Writing Style</h4>
                <p><strong>Tone:</strong> {preferences.get("tone", "Not set").title()}</p>
                <p><strong>Length:</strong> {preferences.get("preferred_length", "Not set").title()}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div class="dashboard-card">
                <h4>⏰ Delivery Settings</h4>
                <p><strong>Frequency:</strong> {preferences.get("frequency", "Not set").replace("_", " ").title()}</p>
                <p><strong>Time:</strong> {preferences.get("send_time", "Not set")} {preferences.get("timezone", "")}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
            <div class="dashboard-card">
                <h4>📊 Content Settings</h4>
                <p><strong>Max Articles:</strong> {preferences.get("max_articles", "Not set")}</p>
                <p><strong>Include Trending:</strong> {"Yes" if preferences.get("include_trending", False) else "No"}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Newsletter history
    st.markdown("### 📰 Newsletter History")

    newsletters = get_newsletter_history()

    if newsletters:
        # Search and filter
        col1, col2 = st.columns([2, 1])

        with col1:
            search_term = st.text_input(
                "🔍 Search newsletters", placeholder="Search by title or topic..."
            )

        with col2:
            status_filter = st.selectbox(
                "Filter by status", ["All", "Sent", "Draft", "Scheduled"]
            )

        # Filter newsletters
        filtered_newsletters = newsletters

        if search_term:
            filtered_newsletters = [
                n
                for n in filtered_newsletters
                if search_term.lower() in n.get("title", "").lower()
                or any(
                    search_term.lower() in topic.lower()
                    for topic in n.get("topics", [])
                )
            ]

        if status_filter != "All":
            filtered_newsletters = [
                n
                for n in filtered_newsletters
                if n.get("status", "").lower() == status_filter.lower()
            ]

        # Display newsletters
        for newsletter in filtered_newsletters:
            status = newsletter.get("status", "unknown")
            status_class = f"status-{status}"

            sent_date = newsletter.get("sent_date", "")
            if sent_date:
                try:
                    date_obj = datetime.fromisoformat(sent_date.replace("Z", "+00:00"))
                    formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")
                except:
                    formatted_date = sent_date
            else:
                formatted_date = "Not sent"

            topics_str = ", ".join(newsletter.get("topics", []))
            newsletter_id = newsletter.get("id")
            has_mindmap = bool(newsletter.get("mindmap_markdown"))

            # Get existing rating
            existing_rating = get_newsletter_rating(newsletter_id)
            current_rating = existing_rating.get("overall_rating", 0) if existing_rating else 0

            st.markdown(
                f"""
            <div class="newsletter-item">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0;">{newsletter.get("title", "Untitled")}</h4>
                    <span class="status-badge {status_class}">{status.upper()}</span>
                </div>
                <p style="margin: 0.25rem 0; color: #6b7280;"><strong>Topics:</strong> {topics_str}</p>
                <p style="margin: 0.25rem 0; color: #6b7280;"><strong>Sent:</strong> {formatted_date}</p>
                <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                    <span style="color: #6b7280;">📊 {newsletter.get("article_count", 0)} articles</span>
                    <span style="color: #6b7280;">👁️ {newsletter.get("open_rate", 0)}% opened</span>
                    <span style="color: #6b7280;">🔗 {newsletter.get("click_rate", 0)}% clicked</span>
                    {f'<span style="color: #f59e0b;">⭐ {current_rating}/5 rated</span>' if current_rating > 0 else '<span style="color: #9ca3af;">⭐ Not rated</span>'}
                    <span style="color: {'#16a34a' if has_mindmap else '#9ca3af'};">🎨 {'Mindmap' if has_mindmap else 'No mindmap'}</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Rating section
            if status == "sent":
                st.markdown(f"**Rate this newsletter:**")
                
                # Display star rating
                rating_col, feedback_col = st.columns([1, 2])
                
                with rating_col:
                    new_rating = display_star_rating(newsletter_id, current_rating)
                
                with feedback_col:
                    feedback_key = f"feedback_{newsletter_id}"
                    current_feedback = existing_rating.get("feedback_text", "") if existing_rating else ""
                    feedback = st.text_input(
                        "Optional feedback:", 
                        value=current_feedback,
                        key=feedback_key,
                        placeholder="What did you think about this newsletter?"
                    )
                
                # Process rating if changed
                if new_rating and new_rating != current_rating:
                    with st.spinner("Saving your rating..."):
                        success, message = rate_newsletter(newsletter_id, new_rating, feedback)
                    
                    if success:
                        st.success(f"✅ Rated {new_rating} stars!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                
                # Update feedback if changed
                if feedback != current_feedback and current_rating > 0:
                    if st.button(f"💭 Update Feedback", key=f"update_feedback_{newsletter_id}"):
                        with st.spinner("Updating feedback..."):
                            success, message = rate_newsletter(newsletter_id, current_rating, feedback)
                        
                        if success:
                            st.success("✅ Feedback updated!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

            # Action buttons for each newsletter
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

            with col1:
                if st.button(f"👁️ View Full", key=f"view_{newsletter['id']}"):
                    # Navigate to dedicated newsletter detail page
                    st.session_state.newsletter_id = newsletter['id']
                    st.switch_page("pages/📄_Newsletter_Detail.py")

            with col2:
                if st.button(f"📧 Resend", key=f"resend_{newsletter['id']}"):
                    st.info("🚧 Resend functionality coming soon!")

            with col3:
                if st.button(f"📊 Analytics", key=f"analytics_{newsletter['id']}"):
                    st.switch_page("pages/📈_Analytics.py")

            with col4:
                if st.button(f"🔄 Create Similar", key=f"similar_{newsletter['id']}"):
                    st.info("🚧 Create similar newsletter coming soon!")
            
            st.markdown("---")

    else:
        # No newsletters exist - show create first newsletter flow
        st.markdown(
            """
        <div class="newsletter-item" style="text-align: center; padding: 3rem 2rem;">
            <h3 style="color: #667eea; margin-bottom: 1rem;">📰 Welcome to Newsletter AI!</h3>
            <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
                You haven't created your first newsletter yet. Let's get started!
            </p>
            <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding: 2rem; border-radius: 12px; margin: 1.5rem 0;">
                <h4 style="color: #1e40af; margin-bottom: 1rem;">🚀 Ready to create your first AI-powered newsletter?</h4>
                <p style="color: #1e40af; margin-bottom: 1.5rem;">
                    Our AI agents will research the latest content, write engaging articles, and create a personalized newsletter just for you.
                </p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        
        # Action buttons for first newsletter
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button(
                "🚀 Create Your First Newsletter", 
                type="primary", 
                use_container_width=True,
                help="Generate a newsletter based on your preferences"
            ):
                with st.spinner("🤖 AI agents are working on your newsletter..."):
                    success, message = send_newsletter_now()

                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    st.info("🔄 Refreshing to show your new newsletter...")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            if st.button(
                "⚙️ Set Up Preferences First", 
                use_container_width=True,
                help="Configure your topics and preferences before creating a newsletter"
            ):
                st.switch_page("pages/⚙️_Preferences.py")
            
            st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
            
            if st.button(
                "✍️ Create Custom Newsletter", 
                use_container_width=True,
                help="Use a custom prompt to create a specific type of newsletter"
            ):
                st.switch_page("pages/✍️_Create_Newsletter.py")
        
        # Getting started tips
        st.markdown("---")
        st.markdown("### 💡 Getting Started Tips")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                """
            <div class="dashboard-card">
                <h4>1. 🎯 Set Your Preferences</h4>
                <p>Choose topics you're interested in, set your preferred tone, and configure delivery settings.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
            
            st.markdown(
                """
            <div class="dashboard-card">
                <h4>3. 📊 Track Performance</h4>
                <p>Monitor open rates, click rates, and adjust your preferences based on what you enjoy most.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
        
        with col2:
            st.markdown(
                """
            <div class="dashboard-card">
                <h4>2. 🚀 Generate Newsletter</h4>
                <p>Use AI agents to research and write personalized content, or create custom newsletters with specific prompts.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
            
            st.markdown(
                """
            <div class="dashboard-card">
                <h4>4. ⚡ Automate Delivery</h4>
                <p>Set up scheduled delivery and let our AI create and send newsletters automatically.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Tips and help
    st.markdown("---")
    st.markdown("### 💡 Tips & Help")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🚀 Getting Started:**
        1. Set up your preferences first
        2. Use "Send Now" for your first newsletter
        3. Check your email for the result
        4. Adjust preferences based on what you receive
        """)

    with col2:
        st.markdown("""
        **📈 Improving Performance:**
        - Try different topics to find what interests you most
        - Experiment with tone settings
        - Use custom prompts for specific content
        - Check analytics to see what works best
        """)


if __name__ == "__main__":
    main()
