"""
Email service using Resend API for OTP and newsletter delivery
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings

class EmailService:
    """Email service using Resend API"""
    
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = "Newsletter AI <noreply@newsletter-ai.com>"
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code"""
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(length))
    
    async def send_otp_email(self, email: str, otp_code: str) -> bool:
        """Send OTP verification email"""
        if not self.api_key:
            print("⚠️  Resend API key not configured")
            return False
        
        try:
            import resend
            resend.api_key = self.api_key
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Newsletter AI - Verification Code</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; }}
                    .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 600; }}
                    .content {{ padding: 40px 20px; }}
                    .otp-code {{ background-color: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0; }}
                    .otp-code h2 {{ color: #1e293b; font-size: 32px; font-weight: 700; margin: 0; letter-spacing: 4px; }}
                    .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; color: #64748b; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Newsletter AI</h1>
                        <p style="color: #e2e8f0; margin: 10px 0 0 0;">Your verification code is ready</p>
                    </div>
                    <div class="content">
                        <h2 style="color: #1e293b; margin-bottom: 20px;">Welcome to Newsletter AI!</h2>
                        <p style="color: #475569; line-height: 1.6; margin-bottom: 30px;">
                            We're excited to have you join our intelligent newsletter platform. 
                            Please use the verification code below to complete your signup:
                        </p>
                        <div class="otp-code">
                            <h2>{otp_code}</h2>
                            <p style="color: #64748b; margin: 10px 0 0 0; font-size: 14px;">This code expires in 10 minutes</p>
                        </div>
                        <p style="color: #475569; line-height: 1.6;">
                            Once verified, you'll be able to:
                        </p>
                        <ul style="color: #475569; line-height: 1.8;">
                            <li>Set your newsletter preferences and topics</li>
                            <li>Receive AI-generated personalized newsletters</li>
                            <li>Create custom newsletter prompts</li>
                            <li>Track your newsletter history</li>
                        </ul>
                        <p style="color: #64748b; font-size: 14px; margin-top: 30px;">
                            If you didn't request this code, you can safely ignore this email.
                        </p>
                    </div>
                    <div class="footer">
                        <p>Newsletter AI - Intelligent newsletter creation powered by AI</p>
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": self.from_email,
                "to": [email],
                "subject": f"Newsletter AI - Your verification code: {otp_code}",
                "html": html_content,
                "text": f"""
Newsletter AI - Verification Code

Welcome to Newsletter AI!

Your verification code is: {otp_code}

This code expires in 10 minutes.

Once verified, you'll be able to set your preferences and receive personalized AI-generated newsletters.

If you didn't request this code, you can safely ignore this email.

Newsletter AI - Intelligent newsletter creation powered by AI
                """.strip()
            }
            
            email_response = resend.Emails.send(params)
            print(f"✅ OTP email sent to {email}: {email_response}")
            return True
            
        except ImportError:
            print("⚠️  Resend package not installed. Install with: pip install resend")
            return False
        except Exception as e:
            print(f"❌ Failed to send OTP email: {e}")
            return False
    
    async def send_welcome_email(self, email: str, first_name: Optional[str] = None) -> bool:
        """Send welcome email after successful registration"""
        if not self.api_key:
            return False
        
        try:
            import resend
            resend.api_key = self.api_key
            
            name = first_name or "there"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to Newsletter AI</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; }}
                    .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 600; }}
                    .content {{ padding: 40px 20px; }}
                    .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
                    .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; color: #64748b; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Welcome to Newsletter AI!</h1>
                        <p style="color: #e2e8f0; margin: 10px 0 0 0;">Your account is now active</p>
                    </div>
                    <div class="content">
                        <h2 style="color: #1e293b; margin-bottom: 20px;">Hi {name}!</h2>
                        <p style="color: #475569; line-height: 1.6; margin-bottom: 30px;">
                            Welcome to Newsletter AI! Your account has been successfully created and you're ready to start receiving personalized, AI-generated newsletters.
                        </p>
                        <h3 style="color: #1e293b;">What's next?</h3>
                        <ul style="color: #475569; line-height: 1.8;">
                            <li><strong>Set your preferences:</strong> Choose topics, tone, and frequency</li>
                            <li><strong>Get your first newsletter:</strong> Use the "Send Now" feature</li>
                            <li><strong>Create custom prompts:</strong> Tell us exactly what you want to read about</li>
                            <li><strong>Track your history:</strong> View all your past newsletters in one place</li>
                        </ul>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" class="cta-button">Go to Dashboard</a>
                        </div>
                        <p style="color: #64748b; font-size: 14px; margin-top: 30px;">
                            Our AI agents are ready to research, curate, and write personalized content just for you!
                        </p>
                    </div>
                    <div class="footer">
                        <p>Newsletter AI - Intelligent newsletter creation powered by AI</p>
                        <p>You can manage your preferences and unsubscribe at any time from your dashboard.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": self.from_email,
                "to": [email],
                "subject": "🎉 Welcome to Newsletter AI - Your account is ready!",
                "html": html_content,
                "text": f"""
Welcome to Newsletter AI!

Hi {name}!

Your account has been successfully created and you're ready to start receiving personalized, AI-generated newsletters.

What's next?
- Set your preferences: Choose topics, tone, and frequency
- Get your first newsletter: Use the "Send Now" feature  
- Create custom prompts: Tell us exactly what you want to read about
- Track your history: View all your past newsletters in one place

Our AI agents are ready to research, curate, and write personalized content just for you!

Newsletter AI - Intelligent newsletter creation powered by AI
                """.strip()
            }
            
            email_response = resend.Emails.send(params)
            print(f"✅ Welcome email sent to {email}: {email_response}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send welcome email: {e}")
            return False

# Global email service instance
email_service = EmailService()