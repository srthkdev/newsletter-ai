"""
Newsletter AI - Analytics and User Insights Page
"""

import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Analytics - Newsletter AI", page_icon="📈", layout="wide"
)

# API Configuration
import os
API_BASE_URL = os.getenv("API_BASE_URL", "https://newsletter-ai-1ndi.onrender.com/api/v1")

# Custom CSS for analytics page
st.markdown(
    """
<style>
    /* Hide Streamlit default elements */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    .analytics-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .insight-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
        color: #1a202c;
    }
    
    .insight-card h3, .insight-card h4 {
        color: #1a202c;
    }
    
    .insight-card p {
        color: #2d3748;
    }
    
    .insight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .metric-highlight {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #22c55e;
        margin: 0.5rem 0;
    }
    
    .trend-up {
        color: #22c55e;
        font-weight: bold;
    }
    
    .trend-down {
        color: #ef4444;
        font-weight: bold;
    }
    
    .trend-neutral {
        color: #6b7280;
        font-weight: bold;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
        color: #92400e;
    }
    
    .recommendation-card h4 {
        color: #92400e;
    }
    
    .rag-insight {
        background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #6366f1;
        margin: 1rem 0;
        color: #3730a3;
    }
    
    .rag-insight h4 {
        color: #3730a3;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        display: block;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #2d3748;
        font-weight: 500;
    }
    
    .export-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1.5rem 0;
        color: #1a202c;
    }
    
    .export-section h3, .export-section h4 {
        color: #1a202c;
    }
</style>
""",
    unsafe_allow_html=True,
)


def get_user_analytics() -> Optional[Dict[str, Any]]:
    """Get comprehensive user analytics from RAG system"""
    try:
        user_id = st.session_state.get("user_id", "demo_user")
        response = requests.get(
            f"{API_BASE_URL}/newsletters/analytics/{user_id}", timeout=15
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Failed to load analytics: {str(e)}")
        return None


def get_mock_analytics() -> Dict[str, Any]:
    """Generate mock analytics data for demonstration"""
    return {
        "user_id": "demo_user",
        "analysis": {
            "total_newsletters": 12,
            "preferred_tones": {"professional": 8, "casual": 3, "technical": 1},
            "topic_interests": {
                "Technology": 10,
                "Business": 8,
                "AI": 7,
                "Startups": 5,
                "Science": 3
            },
            "content_patterns": {
                "avg_articles_per_newsletter": 8.5,
                "preferred_length": "medium",
                "consistency_score": 0.85
            },
            "engagement_insights": [
                "Prefers professional tone in newsletters",
                "Most interested in: Technology, Business, AI",
                "Consistent engagement with medium-length content"
            ]
        },
        "recommendations": {
            "topic_suggestions": [
                {"topic": "Machine Learning", "frequency": 6, "relevance": 0.75},
                {"topic": "Innovation", "frequency": 4, "relevance": 0.65},
                {"topic": "Product Management", "frequency": 3, "relevance": 0.55}
            ],
            "tone_recommendations": {"preferred_tone": "professional"},
            "content_insights": [
                "You've shown interest in 8 different topics",
                "Your most engaging newsletters had 9 articles on average",
                "Based on 12 similar newsletters in your history"
            ],
            "personalization_level": "high"
        },
        "rag_status": "active"
    }


def create_engagement_chart(analytics_data: Dict[str, Any]) -> go.Figure:
    """Create engagement trend chart"""
    # Mock engagement data
    dates = pd.date_range(start='2024-01-01', periods=12, freq='W')
    open_rates = [85, 78, 92, 88, 76, 89, 94, 82, 87, 91, 85, 88]
    click_rates = [12, 15, 18, 14, 11, 16, 19, 13, 15, 17, 14, 16]

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Open Rates Over Time', 'Click Rates Over Time'),
        vertical_spacing=0.1
    )

    # Open rates
    fig.add_trace(
        go.Scatter(
            x=dates, y=open_rates,
            mode='lines+markers',
            name='Open Rate (%)',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )

    # Click rates
    fig.add_trace(
        go.Scatter(
            x=dates, y=click_rates,
            mode='lines+markers',
            name='Click Rate (%)',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8)
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=500,
        showlegend=False,
        title_text="Newsletter Engagement Trends",
        title_x=0.5
    )

    return fig


def create_topic_distribution_chart(topic_interests: Dict[str, int]) -> go.Figure:
    """Create topic interest distribution chart"""
    topics = list(topic_interests.keys())
    values = list(topic_interests.values())

    fig = go.Figure(data=[
        go.Bar(
            x=topics,
            y=values,
            marker_color=['#667eea', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
            text=values,
            textposition='auto',
        )
    ])

    fig.update_layout(
        title="Topic Interest Distribution",
        title_x=0.5,
        xaxis_title="Topics",
        yaxis_title="Newsletter Count",
        height=400
    )

    return fig


def create_tone_preference_chart(tone_preferences: Dict[str, int]) -> go.Figure:
    """Create tone preference pie chart"""
    labels = list(tone_preferences.keys())
    values = list(tone_preferences.values())

    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            marker_colors=['#667eea', '#10b981', '#f59e0b'],
            textinfo='label+percent',
            textposition='inside'
        )
    ])

    fig.update_layout(
        title="Writing Tone Preferences",
        title_x=0.5,
        height=400
    )

    return fig


def show_performance_metrics(analytics_data: Dict[str, Any]):
    """Display key performance metrics"""
    analysis = analytics_data.get("analysis", {})
    
    st.markdown(
        f"""
    <div class="stats-grid">
        <div class="stat-card">
            <span class="stat-number">{analysis.get("total_newsletters", 0)}</span>
            <div class="stat-label">Total Newsletters</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{len(analysis.get("topic_interests", {}))}</span>
            <div class="stat-label">Topics Explored</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{analysis.get("content_patterns", {}).get("avg_articles_per_newsletter", 0):.1f}</span>
            <div class="stat-label">Avg Articles/Newsletter</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{int(analysis.get("content_patterns", {}).get("consistency_score", 0) * 100)}%</span>
            <div class="stat-label">Consistency Score</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def show_ai_insights(analytics_data: Dict[str, Any]):
    """Display AI-powered insights from RAG system"""
    recommendations = analytics_data.get("recommendations", {})
    analysis = analytics_data.get("analysis", {})
    
    st.markdown("### 🤖 AI-Powered Insights")
    
    # Personalization level
    personalization_level = recommendations.get("personalization_level", "basic")
    level_color = {"high": "#22c55e", "medium": "#f59e0b", "basic": "#6b7280"}
    
    st.markdown(
        f"""
    <div class="rag-insight">
        <h4>🧠 RAG System Analysis</h4>
        <p><strong>Personalization Level:</strong> 
        <span style="color: {level_color.get(personalization_level, '#6b7280')}; font-weight: bold;">
        {personalization_level.title()}
        </span></p>
        <p><strong>Status:</strong> {analytics_data.get("rag_status", "unknown").title()}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Content insights
    content_insights = recommendations.get("content_insights", [])
    if content_insights:
        st.markdown("#### 📊 Content Insights")
        for insight in content_insights:
            st.markdown(f"• {insight}")
    
    # Topic suggestions
    topic_suggestions = recommendations.get("topic_suggestions", [])
    if topic_suggestions:
        st.markdown("#### 💡 Recommended Topics")
        
        cols = st.columns(len(topic_suggestions[:3]))
        for i, suggestion in enumerate(topic_suggestions[:3]):
            with cols[i]:
                relevance_color = "#22c55e" if suggestion["relevance"] > 0.7 else "#f59e0b"
                st.markdown(
                    f"""
                <div class="insight-card">
                    <h5>{suggestion["topic"]}</h5>
                    <p><strong>Relevance:</strong> 
                    <span style="color: {relevance_color};">{suggestion["relevance"]:.0%}</span></p>
                    <p><strong>Frequency:</strong> {suggestion["frequency"]}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )


def show_reading_patterns(analytics_data: Dict[str, Any]):
    """Display reading pattern analysis"""
    analysis = analytics_data.get("analysis", {})
    engagement_insights = analysis.get("engagement_insights", [])
    
    st.markdown("### 📚 Reading Patterns & Behavior")
    
    # Engagement insights
    if engagement_insights:
        for insight in engagement_insights:
            st.markdown(
                f"""
            <div class="metric-highlight">
                <strong>📈 Insight:</strong> {insight}
            </div>
            """,
                unsafe_allow_html=True,
            )
    
    # Content patterns
    content_patterns = analysis.get("content_patterns", {})
    if content_patterns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Preferred Length",
                content_patterns.get("preferred_length", "Unknown").title(),
                delta=None
            )
            
        with col2:
            consistency = content_patterns.get("consistency_score", 0)
            st.metric(
                "Reading Consistency",
                f"{consistency:.0%}",
                delta=f"{'+' if consistency > 0.8 else ''}{consistency - 0.8:.1%}" if consistency > 0 else None
            )


def show_improvement_suggestions(analytics_data: Dict[str, Any]):
    """Display improvement suggestions"""
    recommendations = analytics_data.get("recommendations", {})
    
    st.markdown("### 🎯 Personalization Recommendations")
    
    suggestions = [
        {
            "title": "Optimize Content Mix",
            "description": "Based on your reading patterns, try including more technical content alongside business news",
            "priority": "High",
            "impact": "Engagement +15%"
        },
        {
            "title": "Adjust Newsletter Frequency",
            "description": "Your engagement is highest with weekly newsletters - consider switching from daily",
            "priority": "Medium", 
            "impact": "Retention +12%"
        },
        {
            "title": "Explore New Topics",
            "description": "AI suggests adding 'Innovation' and 'Product Management' to your interests",
            "priority": "Low",
            "impact": "Discovery +8%"
        }
    ]
    
    for suggestion in suggestions:
        priority_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}
        
        st.markdown(
            f"""
        <div class="recommendation-card">
            <h4>{suggestion["title"]} 
            <span style="color: {priority_color.get(suggestion['priority'], '#6b7280')}; font-size: 0.8em;">
            [{suggestion["priority"]} Priority]
            </span></h4>
            <p>{suggestion["description"]}</p>
            <p><strong>Expected Impact:</strong> {suggestion["impact"]}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def show_export_options():
    """Display data export options"""
    st.markdown("### 📥 Export Your Data")
    
    st.markdown(
        """
    <div class="export-section">
        <h4>Export Options</h4>
        <p>Download your newsletter analytics and reading data</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Analytics (CSV)", use_container_width=True):
            st.info("📁 CSV export feature coming soon!")
            
    with col2:
        if st.button("📈 Export Charts (PDF)", use_container_width=True):
            st.info("📄 PDF export feature coming soon!")
            
    with col3:
        if st.button("📋 Export Insights (JSON)", use_container_width=True):
            st.info("💾 JSON export feature coming soon!")


def main():
    """Main analytics page"""
    
    # Header
    st.markdown(
        """
    <div class="analytics-header">
        <h1>📈 Newsletter Analytics</h1>
        <p>Personal insights powered by AI and RAG technology</p>
        <p><strong>Deep learning from your reading patterns and preferences</strong></p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Load analytics data
    analytics_data = get_user_analytics()
    
    if not analytics_data:
        st.warning("⚠️ Unable to load analytics data. Using demo data for display.")
        analytics_data = get_mock_analytics()
    
    # Performance metrics
    show_performance_metrics(analytics_data)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "🤖 AI Insights", 
        "📚 Reading Patterns",
        "📥 Export Data"
    ])
    
    with tab1:
        # Engagement trends
        engagement_chart = create_engagement_chart(analytics_data)
        st.plotly_chart(engagement_chart, use_container_width=True)
        
        # Topic and tone charts
        col1, col2 = st.columns(2)
        
        with col1:
            topic_chart = create_topic_distribution_chart(
                analytics_data.get("analysis", {}).get("topic_interests", {})
            )
            st.plotly_chart(topic_chart, use_container_width=True)
            
        with col2:
            tone_chart = create_tone_preference_chart(
                analytics_data.get("analysis", {}).get("preferred_tones", {})
            )
            st.plotly_chart(tone_chart, use_container_width=True)
    
    with tab2:
        show_ai_insights(analytics_data)
        
    with tab3:
        show_reading_patterns(analytics_data)
        show_improvement_suggestions(analytics_data)
        
    with tab4:
        show_export_options()
    
    # Quick actions
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Update Preferences", use_container_width=True):
            st.switch_page("pages/⚙️_Preferences.py")
            
    with col2:
        if st.button("✍️ Create Newsletter", use_container_width=True):
            st.switch_page("pages/✍️_Create_Newsletter.py")
            
    with col3:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.switch_page("pages/📊_Dashboard.py")


if __name__ == "__main__":
    main()