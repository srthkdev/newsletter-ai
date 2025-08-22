"""
Newsletter AI - Streamlit Landing Page and Dashboard
"""

import streamlit as st
import requests
import time
from typing import Optional
import re

# Page configuration
st.set_page_config(
    page_title="Newsletter AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for modern, responsive styling
st.markdown(
    """
<style>
    /* Hide Streamlit default elements for cleaner look */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Modern header styling */
    .main-header {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header h3 {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.8;
        margin: 0;
    }
    
    /* Feature cards with hover effects */
    .feature-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .feature-card h4 {
        color: #1a202c;
        margin-bottom: 1rem;
        font-size: 1.25rem;
        font-weight: 600;
    }
    
    .feature-card p {
        color: #4a5568;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Message styling */
    .success-message {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #10b981;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.1);
    }
    
    .error-message {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        color: #991b1b;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #ef4444;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.1);
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
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
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
    
    /* Process steps styling */
    .process-step {
        text-align: center;
        padding: 1.5rem;
        background: #f8fafc;
        border-radius: 12px;
        margin: 0.5rem;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .process-step:hover {
        border-color: #667eea;
        background: #f1f5f9;
    }
    
    .process-step h4 {
        color: #667eea;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .process-step p {
        color: #4a5568;
        margin: 0;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Mobile responsive styling */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header h3 {
            font-size: 1.25rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
        
        .process-step {
            padding: 1rem;
        }
    }
    
    /* OTP input special styling */
    .otp-input input {
        font-size: 24px !important;
        text-align: center !important;
        letter-spacing: 8px !important;
        font-weight: bold !important;
        font-family: monospace !important;
    }
    
    /* Section dividers */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 3rem 0;
        border: none;
    }
    
    /* Stats counter styling */
    .stats-container {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
    }
    
    .stat-item {
        padding: 1rem;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        display: block;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #4a5568;
        font-weight: 500;
    }
</style>
""",
    unsafe_allow_html=True,
)


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def send_otp_request(email: str) -> tuple[bool, str]:
    """Send OTP request to API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup", json={"email": email}, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return True, data.get("message", "OTP sent successfully")
        else:
            error_data = response.json()
            return False, error_data.get("detail", "Failed to send OTP")

    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please make sure the API is running."
    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"


def verify_otp_request(email: str, otp_code: str) -> tuple[bool, str, Optional[dict]]:
    """Verify OTP with API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/verify-otp",
            json={"email": email, "otp_code": otp_code},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return True, data.get("message", "OTP verified successfully"), data
        else:
            error_data = response.json()
            return False, error_data.get("detail", "OTP verification failed"), None

    except requests.exceptions.ConnectionError:
        return (
            False,
            "Cannot connect to server. Please make sure the API is running.",
            None,
        )
    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again.", None
    except Exception as e:
        return False, f"An error occurred: {str(e)}", None


def main():
    """Main application"""

    # Initialize session state
    if "step" not in st.session_state:
        st.session_state.step = "landing"
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "user_data" not in st.session_state:
        st.session_state.user_data = None

    # Landing Page
    if st.session_state.step == "landing":
        show_landing_page()

    # OTP Verification Page
    elif st.session_state.step == "otp_verification":
        show_otp_verification()

    # Success Page
    elif st.session_state.step == "success":
        show_success_page()


def show_landing_page():
    """Show the enhanced landing page with modern design"""

    # Hero Section
    st.markdown(
        """
    <div class="main-header">
        <h1>🚀 Newsletter AI</h1>
        <h3>Intelligent Newsletter Creation Powered by AI Agents</h3>
        <p>Get personalized, AI-researched, and expertly written newsletters tailored to your interests using cutting-edge Portia AI technology</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Stats Section
    st.markdown(
        """
    <div class="stats-container">
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div class="stat-item">
                <span class="stat-number">🤖</span>
                <div class="stat-label">AI-Powered Agents</div>
            </div>
            <div class="stat-item">
                <span class="stat-number">⚡</span>
                <div class="stat-label">Real-time Research</div>
            </div>
            <div class="stat-item">
                <span class="stat-number">🎯</span>
                <div class="stat-label">Personalized Content</div>
            </div>
            <div class="stat-item">
                <span class="stat-number">📧</span>
                <div class="stat-label">Beautiful Emails</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Main content in columns
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🌟 Welcome to the Future of Newsletters")

        st.markdown("""
        Newsletter AI revolutionizes how you consume information by using **advanced AI agents** to:
        
        - **🔍 Research** the latest content from trusted sources using Tavily API
        - **✍️ Write** engaging, blog-style newsletters with Portia AI framework  
        - **🎨 Personalize** content based on your reading history and preferences
        - **📊 Learn** from your interactions to continuously improve recommendations
        
        Our system combines **research agents**, **writing agents**, and **preference agents** to create 
        newsletters that feel like they were written by your personal AI assistant.
        """)

        # Email signup form
        st.markdown("---")
        st.markdown("#### 🚀 Get Started in Seconds")
        st.markdown("Enter your email address to receive your verification code and unlock personalized AI newsletters:")

        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            key="email_input",
            help="We'll send you a secure 6-digit verification code",
        )

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button(
                "🚀 Send Verification Code", type="primary", use_container_width=True
            ):
                if not email:
                    st.error("Please enter your email address")
                elif not validate_email(email):
                    st.error("Please enter a valid email address")
                else:
                    with st.spinner("Sending verification code..."):
                        success, message = send_otp_request(email)

                    if success:
                        st.session_state.email = email
                        st.session_state.step = "otp_verification"
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

    # Section divider
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # Enhanced Features section
    st.markdown("### ✨ Powerful AI-Driven Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="feature-card">
            <h4>🎯 Smart Research Agent</h4>
            <p>Our Portia AI research agent scours the web using Tavily API to find the most relevant, 
            timely content based on your specific interests and topics. No more information overload!</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="feature-card">
            <h4>✍️ Expert Writing Agent</h4>
            <p>Advanced Portia AI writing agent crafts engaging, blog-style newsletters with perfect tone, 
            structure, and personalization using RAG technology and your reading history.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="feature-card">
            <h4>🧠 Memory & Learning</h4>
            <p>Built-in RAG system and Upstash Vector storage remember your preferences, learn from 
            your interactions, and continuously improve content recommendations.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Second row of features
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="feature-card">
            <h4>⚡ Custom Prompts</h4>
            <p>Tell our Custom Prompt Agent exactly what you want to read about. From "AI breakthroughs this week" 
            to "startup funding with casual tone" - your wish is our command!</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="feature-card">
            <h4>📧 Beautiful Delivery</h4>
            <p>Newsletters are delivered via Resend API with responsive HTML templates. 
            Schedule daily, weekly, or monthly - or use "Send Now" for instant gratification.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="feature-card">
            <h4>📊 Smart Analytics</h4>
            <p>Track your reading patterns, engagement metrics, and content preferences. 
            Our system learns what you love and delivers more of it.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Section divider
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # How it works section with better styling
    st.markdown("### 🔄 How Our AI Agents Work Together")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        <div class="process-step">
            <h4>1. 🎯 Preferences</h4>
            <p>Set your topics, tone, and frequency. Our Preference Agent learns your style.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="process-step">
            <h4>2. 🔍 Research</h4>
            <p>Research Agent uses Tavily API to find the latest, most relevant content.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="process-step">
            <h4>3. ✍️ Writing</h4>
            <p>Writing Agent crafts personalized newsletters using RAG and your history.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
        <div class="process-step">
            <h4>4. 📧 Deliver</h4>
            <p>Beautiful newsletters delivered to your inbox via Resend API.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    
    # Technology showcase
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    st.markdown("### 🛠️ Powered by Cutting-Edge Technology")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🤖 AI & Machine Learning**
        - **Portia AI** - Advanced agent framework
        - **Google Gemini** - Latest LLM technology  
        - **OpenAI Embeddings** - Semantic understanding
        - **RAG System** - Retrieval-augmented generation
        """)
        
    with col2:
        st.markdown("""
        **☁️ Cloud Infrastructure**
        - **Upstash Vector** - High-performance vector storage
        - **Upstash Redis** - Lightning-fast caching
        - **Tavily API** - Real-time web research
        - **Resend API** - Reliable email delivery
        """)
    
    # Footer section
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔒 Privacy & Security**
        - Secure OTP authentication
        - No spam, ever
        - Unsubscribe anytime
        """)
        
    with col2:
        st.markdown("""
        **⚡ Performance**
        - Real-time content research
        - Instant newsletter generation
        - Reliable email delivery
        """)
        
    with col3:
        st.markdown("""
        **🎯 Personalization**
        - Learning from your preferences
        - Adaptive content curation
        - Continuous improvement
        """)


def show_otp_verification():
    """Show OTP verification page"""

    st.markdown(
        """
    <div class="main-header">
        <h1>📧 Check Your Email</h1>
        <h3>Enter Your Verification Code</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            f"""
        <div class="info-message">
            <strong>📨 Verification code sent to:</strong><br>
            {st.session_state.email}
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("Enter the 6-digit code from your email:")

        otp_code = st.text_input(
            "Verification Code",
            placeholder="123456",
            max_chars=6,
            key="otp_input",
            help="Enter the 6-digit code sent to your email",
        )

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

        with col_btn1:
            if st.button("← Back", use_container_width=True):
                st.session_state.step = "landing"
                st.rerun()

        with col_btn2:
            if st.button("Verify Code", type="primary", use_container_width=True):
                if not otp_code:
                    st.error("Please enter the verification code")
                elif len(otp_code) != 6 or not otp_code.isdigit():
                    st.error("Please enter a valid 6-digit code")
                else:
                    with st.spinner("Verifying code..."):
                        success, message, user_data = verify_otp_request(
                            st.session_state.email, otp_code
                        )

                    if success:
                        st.session_state.user_data = user_data
                        st.session_state.step = "success"
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

        with col_btn3:
            if st.button("Resend Code", use_container_width=True):
                with st.spinner("Resending verification code..."):
                    success, message = send_otp_request(st.session_state.email)

                if success:
                    st.success("✅ New verification code sent!")
                else:
                    st.error(f"❌ {message}")

        st.markdown("---")
        st.markdown("""
        **Didn't receive the code?**
        - Check your spam/junk folder
        - Make sure you entered the correct email address
        - Click "Resend Code" to get a new one
        - The code expires in 10 minutes
        """)


def show_success_page():
    """Show success page after verification"""

    st.markdown(
        """
    <div class="main-header">
        <h1>🎉 Welcome to Newsletter AI!</h1>
        <h3>Your account is now active</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
        <div class="success-message">
            <strong>✅ Email verified successfully!</strong><br>
            Your Newsletter AI account is now ready to use.
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🚀 What's Next?")

        st.markdown("""
        1. **Set Your Preferences** - Choose topics, tone, and frequency
        2. **Get Your First Newsletter** - Use the "Send Now" feature  
        3. **Create Custom Prompts** - Tell us exactly what you want to read about
        4. **Track Your History** - View all your newsletters in one place
        """)

        st.markdown("### 🎯 Ready to Start?")

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button(
                "📊 Go to Dashboard", type="primary", use_container_width=True
            ):
                st.switch_page("pages/📊_Dashboard.py")

        with col_btn2:
            if st.button("⚙️ Set Preferences", use_container_width=True):
                st.switch_page("pages/⚙️_Preferences.py")

        st.markdown("---")

        # User info
        if st.session_state.user_data:
            user_data = st.session_state.user_data
            st.markdown("### 👤 Account Information")
            st.write(f"**Email:** {st.session_state.email}")
            st.write(f"**User ID:** {user_data.get('user_id', 'N/A')}")
            st.write(
                f"**Session Token:** {user_data.get('session_token', 'N/A')[:20]}..."
            )

        # Reset button for testing
        if st.button("🔄 Start Over (for testing)", type="secondary"):
            st.session_state.step = "landing"
            st.session_state.email = ""
            st.session_state.user_data = None
            st.rerun()


if __name__ == "__main__":
    main()
