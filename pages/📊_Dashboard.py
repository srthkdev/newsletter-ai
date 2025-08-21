"""
Newsletter AI - Main Dashboard
"""
import streamlit as st
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Dashboard - Newsletter AI",
    page_icon="📊",
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS
st.markdown("""
<style>
    .dashboard-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
    .newsletter-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
""", unsafe_allow_html=True)

def get_user_preferences() -> Optional[Dict[str, Any]]:
    """Get current user preferences"""
    try:
        user_id = st.session_state.get('user_id', 'demo_user')
        response = requests.get(f"{API_BASE_URL}/preferences/{user_id}", timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def get_newsletter_history() -> List[Dict[str, Any]]:
    """Get user's newsletter history"""
    # Mock data for now - in real implementation this would call the API
    return [
        {
            "id": "1",
            "title": "Weekly Tech Digest - AI Breakthroughs",
            "status": "sent",
            "sent_date": "2024-01-15T09:00:00Z",
            "topics": ["Technology", "Artificial Intelligence"],
            "article_count": 8,
            "open_rate": 85.2,
            "click_rate": 12.4
        },
        {
            "id": "2", 
            "title": "Business Innovation Weekly",
            "status": "sent",
            "sent_date": "2024-01-08T09:00:00Z",
            "topics": ["Business", "Innovation"],
            "article_count": 10,
            "open_rate": 78.9,
            "click_rate": 15.6
        },
        {
            "id": "3",
            "title": "Tech & Startup News Roundup",
            "status": "sent", 
            "sent_date": "2024-01-01T09:00:00Z",
            "topics": ["Technology", "Startups"],
            "article_count": 12,
            "open_rate": 92.1,
            "click_rate": 18.3
        }
    ]

def get_dashboard_metrics() -> Dict[str, Any]:
    """Get dashboard metrics"""
    newsletters = get_newsletter_history()
    
    if not newsletters:
        return {
            "total_newsletters": 0,
            "avg_open_rate": 0,
            "avg_click_rate": 0,
            "total_articles": 0
        }
    
    total_newsletters = len(newsletters)
    avg_open_rate = sum(n.get('open_rate', 0) for n in newsletters) / total_newsletters
    avg_click_rate = sum(n.get('click_rate', 0) for n in newsletters) / total_newsletters
    total_articles = sum(n.get('article_count', 0) for n in newsletters)
    
    return {
        "total_newsletters": total_newsletters,
        "avg_open_rate": round(avg_open_rate, 1),
        "avg_click_rate": round(avg_click_rate, 1),
        "total_articles": total_articles
    }

def send_newsletter_now() -> tuple[bool, str]:
    """Trigger immediate newsletter generation and sending"""
    try:
        user_id = st.session_state.get('user_id', 'demo_user')
        
        response = requests.post(
            f"{API_BASE_URL}/newsletters/generate",
            json={"user_id": user_id, "send_immediately": True},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Newsletter generated and sent successfully!"
        else:
            error_data = response.json()
            return False, error_data.get("detail", "Failed to generate newsletter")
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please make sure the API is running."
    except Exception as e:
        return False, f"Error generating newsletter: {str(e)}"

def main():
    """Main dashboard page"""
    
    # Header
    st.title("📊 Newsletter Dashboard")
    st.markdown("Your personalized newsletter command center")
    
    # Load user preferences
    preferences = get_user_preferences()
    
    if not preferences or preferences.get('is_default', False):
        st.warning("""
        ⚠️ **Setup Required**
        
        You haven't set up your preferences yet! Visit the **Preferences** page to:
        - Choose your topics of interest
        - Set your preferred tone and frequency
        - Customize your newsletter experience
        """)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("⚙️ Set Up Preferences", type="primary", use_container_width=True):
                st.switch_page("pages/⚙️_Preferences.py")
    
    # Dashboard metrics
    st.markdown("### 📈 Your Newsletter Stats")
    
    metrics = get_dashboard_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #667eea;">{}</h3>
            <p style="margin: 0; color: #6b7280;">Total Newsletters</p>
        </div>
        """.format(metrics['total_newsletters']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #10b981;">{}%</h3>
            <p style="margin: 0; color: #6b7280;">Avg Open Rate</p>
        </div>
        """.format(metrics['avg_open_rate']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #f59e0b;">{}%</h3>
            <p style="margin: 0; color: #6b7280;">Avg Click Rate</p>
        </div>
        """.format(metrics['avg_click_rate']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #8b5cf6;">{}</h3>
            <p style="margin: 0; color: #6b7280;">Articles Read</p>
        </div>
        """.format(metrics['total_articles']), unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Send Newsletter Now", type="primary", use_container_width=True):
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
    if preferences and not preferences.get('is_default', False):
        st.markdown("### 🎯 Your Current Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="dashboard-card">
                <h4>📚 Topics ({len(preferences.get('topics', []))})</h4>
                <p>{', '.join(preferences.get('topics', ['None selected']))}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="dashboard-card">
                <h4>🎨 Writing Style</h4>
                <p><strong>Tone:</strong> {preferences.get('tone', 'Not set').title()}</p>
                <p><strong>Length:</strong> {preferences.get('preferred_length', 'Not set').title()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="dashboard-card">
                <h4>⏰ Delivery Settings</h4>
                <p><strong>Frequency:</strong> {preferences.get('frequency', 'Not set').replace('_', ' ').title()}</p>
                <p><strong>Time:</strong> {preferences.get('send_time', 'Not set')} {preferences.get('timezone', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="dashboard-card">
                <h4>📊 Content Settings</h4>
                <p><strong>Max Articles:</strong> {preferences.get('max_articles', 'Not set')}</p>
                <p><strong>Include Trending:</strong> {'Yes' if preferences.get('include_trending', False) else 'No'}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Newsletter history
    st.markdown("### 📰 Newsletter History")
    
    newsletters = get_newsletter_history()
    
    if newsletters:
        # Search and filter
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search newsletters", placeholder="Search by title or topic...")
        
        with col2:
            status_filter = st.selectbox("Filter by status", ["All", "Sent", "Draft", "Scheduled"])
        
        # Filter newsletters
        filtered_newsletters = newsletters
        
        if search_term:
            filtered_newsletters = [
                n for n in filtered_newsletters 
                if search_term.lower() in n.get('title', '').lower() or 
                   any(search_term.lower() in topic.lower() for topic in n.get('topics', []))
            ]
        
        if status_filter != "All":
            filtered_newsletters = [
                n for n in filtered_newsletters 
                if n.get('status', '').lower() == status_filter.lower()
            ]
        
        # Display newsletters
        for newsletter in filtered_newsletters:
            status = newsletter.get('status', 'unknown')
            status_class = f"status-{status}"
            
            sent_date = newsletter.get('sent_date', '')
            if sent_date:
                try:
                    date_obj = datetime.fromisoformat(sent_date.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")
                except:
                    formatted_date = sent_date
            else:
                formatted_date = "Not sent"
            
            topics_str = ", ".join(newsletter.get('topics', []))
            
            st.markdown(f"""
            <div class="newsletter-item">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0;">{newsletter.get('title', 'Untitled')}</h4>
                    <span class="status-badge {status_class}">{status.upper()}</span>
                </div>
                <p style="margin: 0.25rem 0; color: #6b7280;"><strong>Topics:</strong> {topics_str}</p>
                <p style="margin: 0.25rem 0; color: #6b7280;"><strong>Sent:</strong> {formatted_date}</p>
                <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                    <span style="color: #6b7280;">📊 {newsletter.get('article_count', 0)} articles</span>
                    <span style="color: #6b7280;">👁️ {newsletter.get('open_rate', 0)}% opened</span>
                    <span style="color: #6b7280;">🔗 {newsletter.get('click_rate', 0)}% clicked</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons for each newsletter
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                if st.button(f"👁️ View", key=f"view_{newsletter['id']}"):
                    st.info("🚧 Newsletter viewer coming soon!")
            
            with col2:
                if st.button(f"📧 Resend", key=f"resend_{newsletter['id']}"):
                    st.info("🚧 Resend functionality coming soon!")
            
            with col3:
                if st.button(f"📊 Analytics", key=f"analytics_{newsletter['id']}"):
                    st.info("🚧 Detailed analytics coming soon!")
            
            with col4:
                if st.button(f"🔄 Create Similar", key=f"similar_{newsletter['id']}"):
                    st.info("🚧 Create similar newsletter coming soon!")
    
    else:
        st.info("""
        📭 **No newsletters yet**
        
        You haven't generated any newsletters yet. Click "Send Newsletter Now" to create your first one!
        
        Once you have newsletters, you'll see them here with:
        - 📊 Performance metrics
        - 🔍 Search and filtering
        - 👁️ Full content viewing
        - 📧 Resend options
        """)
    
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