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
    initial_sidebar_state="collapsed"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
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
    .info-message {
        background: #dbeafe;
        color: #1e40af;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    .otp-input {
        font-size: 24px;
        text-align: center;
        letter-spacing: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_otp_request(email: str) -> tuple[bool, str]:
    """Send OTP request to API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json={"email": email},
            timeout=10
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
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, data.get("message", "OTP verified successfully"), data
        else:
            error_data = response.json()
            return False, error_data.get("detail", "OTP verification failed"), None
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please make sure the API is running.", None
    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again.", None
    except Exception as e:
        return False, f"An error occurred: {str(e)}", None

def main():
    """Main application"""
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 'landing'
    if 'email' not in st.session_state:
        st.session_state.email = ''
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    # Landing Page
    if st.session_state.step == 'landing':
        show_landing_page()
    
    # OTP Verification Page
    elif st.session_state.step == 'otp_verification':
        show_otp_verification()
    
    # Success Page
    elif st.session_state.step == 'success':
        show_success_page()

def show_landing_page():
    """Show the landing page with email signup"""
    
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Newsletter AI</h1>
        <h3>Intelligent Newsletter Creation Powered by AI</h3>
        <p>Get personalized, AI-generated newsletters tailored to your interests</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content in columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Welcome to the Future of Newsletters")
        
        st.markdown("""
        Newsletter AI uses advanced AI agents to research, curate, and write personalized newsletters just for you. 
        Our intelligent system learns your preferences and delivers content that matters most to you.
        """)
        
        # Email signup form
        st.markdown("#### Get Started")
        st.markdown("Enter your email address to receive your verification code:")
        
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            key="email_input",
            help="We'll send you a 6-digit verification code"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("Send Verification Code", type="primary", use_container_width=True):
                if not email:
                    st.error("Please enter your email address")
                elif not validate_email(email):
                    st.error("Please enter a valid email address")
                else:
                    with st.spinner("Sending verification code..."):
                        success, message = send_otp_request(email)
                        
                    if success:
                        st.session_state.email = email
                        st.session_state.step = 'otp_verification'
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # Features section
    st.markdown("---")
    st.markdown("### ✨ What You'll Get")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 Personalized Content</h4>
            <p>AI agents research and curate content based on your specific interests and preferences</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 Smart Writing</h4>
            <p>Advanced AI writes engaging, blog-style newsletters in your preferred tone and style</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>⚡ Custom Prompts</h4>
            <p>Tell us exactly what you want to read about with custom newsletter prompts</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works
    st.markdown("### 🔄 How It Works")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **1. Set Preferences**  
        Choose your topics, tone, and frequency
        """)
    
    with col2:
        st.markdown("""
        **2. AI Research**  
        Our agents find the latest relevant content
        """)
    
    with col3:
        st.markdown("""
        **3. Smart Writing**  
        AI writes personalized newsletters for you
        """)
    
    with col4:
        st.markdown("""
        **4. Delivered**  
        Receive beautiful newsletters in your inbox
        """)

def show_otp_verification():
    """Show OTP verification page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📧 Check Your Email</h1>
        <h3>Enter Your Verification Code</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="info-message">
            <strong>📨 Verification code sent to:</strong><br>
            {st.session_state.email}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("Enter the 6-digit code from your email:")
        
        otp_code = st.text_input(
            "Verification Code",
            placeholder="123456",
            max_chars=6,
            key="otp_input",
            help="Enter the 6-digit code sent to your email"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn1:
            if st.button("← Back", use_container_width=True):
                st.session_state.step = 'landing'
                st.rerun()
        
        with col_btn2:
            if st.button("Verify Code", type="primary", use_container_width=True):
                if not otp_code:
                    st.error("Please enter the verification code")
                elif len(otp_code) != 6 or not otp_code.isdigit():
                    st.error("Please enter a valid 6-digit code")
                else:
                    with st.spinner("Verifying code..."):
                        success, message, user_data = verify_otp_request(st.session_state.email, otp_code)
                    
                    if success:
                        st.session_state.user_data = user_data
                        st.session_state.step = 'success'
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
    
    st.markdown("""
    <div class="main-header">
        <h1>🎉 Welcome to Newsletter AI!</h1>
        <h3>Your account is now active</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="success-message">
            <strong>✅ Email verified successfully!</strong><br>
            Your Newsletter AI account is now ready to use.
        </div>
        """, unsafe_allow_html=True)
        
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
            if st.button("📊 Go to Dashboard", type="primary", use_container_width=True):
                st.info("🚧 Dashboard coming soon! This will redirect to your personalized dashboard.")
        
        with col_btn2:
            if st.button("⚙️ Set Preferences", use_container_width=True):
                st.info("🚧 Preferences page coming soon! This will let you customize your newsletter settings.")
        
        st.markdown("---")
        
        # User info
        if st.session_state.user_data:
            user_data = st.session_state.user_data
            st.markdown("### 👤 Account Information")
            st.write(f"**Email:** {st.session_state.email}")
            st.write(f"**User ID:** {user_data.get('user_id', 'N/A')}")
            st.write(f"**Session Token:** {user_data.get('session_token', 'N/A')[:20]}...")
        
        # Reset button for testing
        if st.button("🔄 Start Over (for testing)", type="secondary"):
            st.session_state.step = 'landing'
            st.session_state.email = ''
            st.session_state.user_data = None
            st.rerun()

if __name__ == "__main__":
    main()