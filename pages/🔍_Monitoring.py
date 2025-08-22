"""
Newsletter AI - Portia Agent Monitoring and Error Handling Page
Real-time monitoring of AI agents and system health
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
    page_title="Monitoring - Newsletter AI", page_icon="🔍", layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for monitoring page
st.markdown(
    """
<style>
    /* Hide Streamlit default elements */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    .monitoring-header {
        background: linear-gradient(135deg, #1e293b, #475569);
        color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(30, 41, 59, 0.3);
    }
    
    .health-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
        color: #1a202c;
    }
    
    .health-card h3, .health-card h4 {
        color: #1a202c;
    }
    
    .health-card p {
        color: #2d3748;
    }
    
    .health-card.healthy {
        border-left: 4px solid #22c55e;
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    }
    
    .health-card.warning {
        border-left: 4px solid #f59e0b;
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
    }
    
    .health-card.error {
        border-left: 4px solid #ef4444;
        background: linear-gradient(135deg, #fef2f2, #fecaca);
    }
    
    .health-card.offline {
        border-left: 4px solid #6b7280;
        background: linear-gradient(135deg, #f9fafb, #f3f4f6);
    }
    
    .agent-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    .status-healthy {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-error {
        background-color: #fecaca;
        color: #991b1b;
    }
    
    .status-offline {
        background-color: #f3f4f6;
        color: #374151;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        color: #1a202c;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #2d3748;
        font-weight: 500;
    }
    
    .error-item {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .error-critical {
        border-left: 4px solid #dc2626;
    }
    
    .error-high {
        border-left: 4px solid #ea580c;
    }
    
    .error-medium {
        border-left: 4px solid #d97706;
    }
    
    .error-low {
        border-left: 4px solid #65a30d;
    }
    
    .control-panel {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1.5rem 0;
        color: #1a202c;
    }
    
    .control-panel h3, .control-panel h4 {
        color: #1a202c;
    }
    
    .real-time-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 0.5rem;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""",
    unsafe_allow_html=True,
)


def get_monitoring_dashboard() -> Optional[Dict[str, Any]]:
    """Get monitoring dashboard data from API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/newsletters/monitoring/dashboard", timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Failed to load monitoring data: {str(e)}")
        return None


def get_system_health() -> Optional[Dict[str, Any]]:
    """Get system health status"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/newsletters/monitoring/health", timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Failed to load health data: {str(e)}")
        return None


def get_agent_report(agent_name: str) -> Optional[Dict[str, Any]]:
    """Get detailed agent performance report"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/newsletters/monitoring/agent/{agent_name}", timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Failed to load agent report: {str(e)}")
        return None


def start_monitoring_system() -> bool:
    """Start the monitoring system"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/newsletters/monitoring/start", timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def stop_monitoring_system() -> bool:
    """Stop the monitoring system"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/newsletters/monitoring/stop", timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def resolve_error(error_index: int) -> bool:
    """Resolve a monitoring error"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/newsletters/monitoring/resolve-error/{error_index}", 
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def show_system_overview(dashboard_data: Dict[str, Any]):
    """Display system overview metrics"""
    system_health = dashboard_data.get("system_health", {})
    error_summary = dashboard_data.get("error_summary", {})
    
    # Health status header
    status = system_health.get("status", "unknown")
    score = system_health.get("overall_score", 0)
    monitoring_active = system_health.get("monitoring_active", False)
    
    status_color = {
        "healthy": "#22c55e",
        "warning": "#f59e0b", 
        "critical": "#ef4444"
    }.get(status, "#6b7280")
    
    st.markdown(
        f"""
    <div class="monitoring-header">
        <h1>🔍 Portia Agent Monitoring</h1>
        <p>Real-time monitoring and error handling for AI agents</p>
        <div style="margin-top: 1rem;">
            <span class="real-time-indicator"></span>
            <strong>System Status: </strong>
            <span style="color: {status_color}; font-weight: bold; text-transform: uppercase;">
                {status}
            </span>
            <span style="margin-left: 2rem;">
                <strong>Health Score: </strong>{score}%
            </span>
            <span style="margin-left: 2rem;">
                <strong>Monitoring: </strong>{'🟢 Active' if monitoring_active else '🔴 Inactive'}
            </span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">{error_summary.get('total_errors_24h', 0)}</div>
            <div class="metric-label">Errors (24h)</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    
    with col2:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">{error_summary.get('critical_errors', 0)}</div>
            <div class="metric-label">Critical Errors</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    
    with col3:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">{error_summary.get('unresolved_errors', 0)}</div>
            <div class="metric-label">Unresolved</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    
    with col4:
        agents = dashboard_data.get("agents", {})
        healthy_count = sum(1 for agent in agents.values() if agent.get("status") == "healthy")
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">{healthy_count}/{len(agents)}</div>
            <div class="metric-label">Healthy Agents</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def show_agent_status(dashboard_data: Dict[str, Any]):
    """Display status of all Portia agents"""
    st.markdown("### 🤖 Portia Agent Status")
    
    agents = dashboard_data.get("agents", {})
    
    if not agents:
        st.warning("No agent data available")
        return
    
    # Create agent status cards
    cols = st.columns(min(len(agents), 3))
    for i, (agent_name, agent_data) in enumerate(agents.items()):
        with cols[i % 3]:
            status = agent_data.get("status", "unknown")
            health_score = agent_data.get("health_score", 0)
            success_rate = agent_data.get("success_rate", 0)
            total_executions = agent_data.get("total_executions", 0)
            avg_execution_time = agent_data.get("average_execution_time", 0)
            
            st.markdown(
                f"""
            <div class="health-card {status}">
                <h4>{agent_name.replace('_', ' ').title()}</h4>
                <span class="agent-status status-{status}">{status}</span>
                <p style="margin: 1rem 0;"><strong>Health:</strong> {health_score}%</p>
                <p><strong>Success Rate:</strong> {success_rate:.1f}%</p>
                <p><strong>Executions:</strong> {total_executions}</p>
                <p><strong>Avg Time:</strong> {avg_execution_time:.2f}s</p>
            </div>
            """,
                unsafe_allow_html=True,
            )


def show_performance_charts(dashboard_data: Dict[str, Any]):
    """Display performance charts"""
    st.markdown("### 📊 Performance Analytics")
    
    agents = dashboard_data.get("agents", {})
    
    if not agents:
        return
    
    # Agent health scores
    agent_names = list(agents.keys())
    health_scores = [agents[name].get("health_score", 0) for name in agent_names]
    success_rates = [agents[name].get("success_rate", 0) for name in agent_names]
    execution_times = [agents[name].get("average_execution_time", 0) for name in agent_names]
    
    # Health scores chart
    fig_health = go.Figure(data=[
        go.Bar(
            x=[name.replace('_', ' ').title() for name in agent_names],
            y=health_scores,
            marker_color=['#22c55e' if score >= 90 else '#f59e0b' if score >= 70 else '#ef4444' for score in health_scores],
            text=[f"{score}%" for score in health_scores],
            textposition='auto',
        )
    ])
    
    fig_health.update_layout(
        title="Agent Health Scores",
        title_x=0.5,
        yaxis_title="Health Score (%)",
        height=400
    )
    
    # Success rates chart
    fig_success = go.Figure(data=[
        go.Bar(
            x=[name.replace('_', ' ').title() for name in agent_names],
            y=success_rates,
            marker_color='#10b981',
            text=[f"{rate:.1f}%" for rate in success_rates],
            textposition='auto',
        )
    ])
    
    fig_success.update_layout(
        title="Success Rates",
        title_x=0.5,
        yaxis_title="Success Rate (%)",
        height=400
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_health, use_container_width=True)
    with col2:
        st.plotly_chart(fig_success, use_container_width=True)


def show_recent_errors(dashboard_data: Dict[str, Any]):
    """Display recent errors"""
    st.markdown("### ⚠️ Recent Errors")
    
    recent_errors = dashboard_data.get("recent_errors", [])
    
    if not recent_errors:
        st.success("🎉 No recent errors! All systems running smoothly.")
        return
    
    for i, error in enumerate(recent_errors):
        severity = error.get("severity", "low")
        timestamp = error.get("timestamp", "")
        component = error.get("component", "Unknown")
        message = error.get("message", "")
        resolved = error.get("resolved", False)
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp
        
        severity_emoji = {
            "critical": "🚨",
            "high": "⚠️", 
            "medium": "⚠️",
            "low": "ℹ️"
        }.get(severity, "ℹ️")
        
        status_text = "✅ Resolved" if resolved else "🔴 Active"
        
        st.markdown(
            f"""
        <div class="error-item error-{severity}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong>{severity_emoji} {component} - {severity.upper()}</strong>
                <span>{status_text}</span>
            </div>
            <p style="margin: 0.5rem 0;"><strong>Time:</strong> {time_str}</p>
            <p style="margin: 0;"><strong>Message:</strong> {message}</p>
            {"" if resolved else f'<button onclick="resolve_error({i})" style="margin-top: 0.5rem; padding: 0.25rem 0.5rem; background: #dc2626; color: white; border: none; border-radius: 4px; cursor: pointer;">Mark as Resolved</button>'}
        </div>
        """,
            unsafe_allow_html=True,
        )


def show_control_panel():
    """Display monitoring control panel"""
    st.markdown("### ⚙️ Monitoring Controls")
    
    st.markdown(
        """
    <div class="control-panel">
        <h4>System Controls</h4>
        <p>Start, stop, and manage the Portia agent monitoring system</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚀 Start Monitoring", use_container_width=True):
            if start_monitoring_system():
                st.success("✅ Monitoring system started")
                st.rerun()
            else:
                st.error("❌ Failed to start monitoring")
    
    with col2:
        if st.button("🛑 Stop Monitoring", use_container_width=True):
            if stop_monitoring_system():
                st.success("✅ Monitoring system stopped")
                st.rerun()
            else:
                st.error("❌ Failed to stop monitoring")
    
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col4:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/📈_Analytics.py")


def show_agent_details():
    """Show detailed agent information"""
    st.markdown("### 🔍 Agent Details")
    
    agent_options = [
        "research_agent",
        "writing_agent", 
        "preference_agent",
        "custom_prompt_agent",
        "agent_orchestrator"
    ]
    
    selected_agent = st.selectbox(
        "Select agent for detailed analysis:",
        agent_options,
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    if selected_agent:
        agent_report = get_agent_report(selected_agent)
        
        if agent_report and agent_report.get("success"):
            report_data = agent_report.get("report", {})
            
            # Agent status summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Current Status")
                performance = report_data.get("performance", {})
                st.write(f"**Status:** {report_data.get('current_status', 'Unknown')}")
                st.write(f"**Health Score:** {report_data.get('health_score', 0)}%")
                st.write(f"**Total Executions:** {performance.get('total_executions', 0)}")
                st.write(f"**Success Rate:** {performance.get('success_rate', 0):.1f}%")
            
            with col2:
                st.markdown("#### Performance Metrics")
                st.write(f"**Successful:** {performance.get('successful_executions', 0)}")
                st.write(f"**Failed:** {performance.get('failed_executions', 0)}")
                st.write(f"**Avg Execution Time:** {performance.get('average_execution_time', 0):.2f}s")
            
            # Recent activity
            recent_activity = report_data.get("recent_activity", {})
            if recent_activity:
                st.markdown("#### Recent Activity")
                last_execution = recent_activity.get("last_execution")
                if last_execution:
                    st.write(f"**Last Execution:** {last_execution}")
                
                last_error = recent_activity.get("last_error")
                if last_error:
                    st.write(f"**Last Error:** {last_error.get('timestamp', 'Unknown')}")
                    st.write(f"**Error Message:** {last_error.get('message', 'Unknown')}")
            
            # Recommendations
            recommendations = report_data.get("recommendations", [])
            if recommendations:
                st.markdown("#### Recommendations")
                for rec in recommendations:
                    st.write(f"• {rec}")
        else:
            st.error("Failed to load agent report")


def main():
    """Main monitoring page"""
    
    # Get monitoring data
    dashboard_data = get_monitoring_dashboard()
    
    if not dashboard_data or not dashboard_data.get("success"):
        st.error("⚠️ Unable to load monitoring data. Please ensure the monitoring system is running.")
        
        # Show control panel even if data loading fails
        show_control_panel()
        return
    
    dashboard = dashboard_data.get("dashboard", {})
    
    # System overview
    show_system_overview(dashboard)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🤖 Agents", 
        "📊 Performance", 
        "⚠️ Errors",
        "🔍 Details",
        "⚙️ Controls"
    ])
    
    with tab1:
        show_agent_status(dashboard)
    
    with tab2:
        show_performance_charts(dashboard)
    
    with tab3:
        show_recent_errors(dashboard)
    
    with tab4:
        show_agent_details()
    
    with tab5:
        show_control_panel()
    
    # Auto-refresh notice
    st.markdown("---")
    st.markdown("💡 **Pro Tip:** This page shows real-time data. Use the refresh button to update the display.")
    
    # Quick navigation
    st.markdown("### 🚀 Quick Navigation")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.switch_page("pages/📊_Dashboard.py")
    
    with col2:
        if st.button("📈 View Analytics", use_container_width=True):
            st.switch_page("pages/📈_Analytics.py")
    
    with col3:
        if st.button("⚙️ Preferences", use_container_width=True):
            st.switch_page("pages/⚙️_Preferences.py")


if __name__ == "__main__":
    main()