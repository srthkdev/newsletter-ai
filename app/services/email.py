"""
Email service using Resend API for OTP and newsletter delivery
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings


class EmailService:
    """Email service using Resend API"""

    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = "Newsletter AI <noreply@newsletter-ai.com>"

    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code"""
        digits = string.digits
        return "".join(secrets.choice(digits) for _ in range(length))

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
                """.strip(),
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

    async def send_welcome_email(
        self, email: str, first_name: Optional[str] = None
    ) -> bool:
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
                """.strip(),
            }

            email_response = resend.Emails.send(params)
            print(f"✅ Welcome email sent to {email}: {email_response}")
            return True

        except Exception as e:
            print(f"❌ Failed to send welcome email: {e}")
            return False

    async def send_newsletter_email(
        self,
        email: str,
        newsletter_data: Dict[str, Any],
        subject_line: Optional[str] = None,
    ) -> bool:
        """Send newsletter email using Resend API"""
        if not self.api_key:
            print("⚠️  Resend API key not configured")
            return False

        try:
            import resend

            resend.api_key = self.api_key

            # Extract newsletter content
            title = newsletter_data.get("title", "Your Newsletter")
            html_content = newsletter_data.get("html_content", "")
            plain_text = newsletter_data.get("plain_text", "")

            # Use provided subject line or generate from title
            subject = subject_line or f"📧 {title}"

            # If no HTML content provided, create basic template
            if not html_content:
                html_content = self._create_basic_newsletter_template(newsletter_data)

            # If no plain text provided, create from HTML
            if not plain_text:
                plain_text = self._html_to_plain_text(html_content)

            params = {
                "from": self.from_email,
                "to": [email],
                "subject": subject,
                "html": html_content,
                "text": plain_text,
            }

            email_response = resend.Emails.send(params)
            print(f"✅ Newsletter sent to {email}: {email_response}")
            return True

        except ImportError:
            print("⚠️  Resend package not installed. Install with: pip install resend")
            return False
        except Exception as e:
            print(f"❌ Failed to send newsletter: {e}")
            return False

    def _create_basic_newsletter_template(self, newsletter_data: Dict[str, Any]) -> str:
        """Create basic HTML template for newsletter"""
        title = newsletter_data.get("title", "Your Newsletter")
        introduction = newsletter_data.get("introduction", "")
        sections = newsletter_data.get("sections", [])
        conclusion = newsletter_data.get("conclusion", "")

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    line-height: 1.6; 
                    color: #333; 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background-color: #f8fafc;
                }}
                .container {{ 
                    background-color: white; 
                    border-radius: 8px; 
                    overflow: hidden; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px 20px; 
                    text-align: center; 
                }}
                .header h1 {{ 
                    color: white; 
                    margin: 0; 
                    font-size: 24px; 
                    font-weight: 600; 
                }}
                .content {{ 
                    padding: 30px 20px; 
                }}
                .intro {{ 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 20px 0; 
                    border-left: 4px solid #3498db;
                }}
                .section {{ 
                    margin: 30px 0; 
                    padding: 20px 0; 
                    border-bottom: 1px solid #e9ecef;
                }}
                .section:last-child {{ 
                    border-bottom: none; 
                }}
                .section h2 {{ 
                    color: #2c3e50; 
                    font-size: 20px; 
                    margin-bottom: 15px;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 5px;
                }}
                .article {{ 
                    margin: 15px 0; 
                    padding: 15px; 
                    background-color: #f8f9fa; 
                    border-radius: 6px;
                    border-left: 3px solid #3498db;
                }}
                .article h3 {{ 
                    color: #2c3e50; 
                    font-size: 16px; 
                    margin: 0 0 10px 0; 
                }}
                .article p {{ 
                    color: #555; 
                    margin: 0; 
                    font-size: 14px;
                }}
                a {{ 
                    color: #3498db; 
                    text-decoration: none; 
                }}
                a:hover {{ 
                    text-decoration: underline; 
                }}
                .conclusion {{ 
                    background-color: #e8f4f8; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 30px 0; 
                }}
                .footer {{ 
                    background-color: #2c3e50; 
                    color: white; 
                    padding: 20px; 
                    text-align: center; 
                    font-size: 12px;
                }}
                .footer a {{ 
                    color: #3498db; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 {title}</h1>
                    <p style="color: #e2e8f0; margin: 10px 0 0 0;">
                        {datetime.now().strftime("%B %d, %Y")}
                    </p>
                </div>
                <div class="content">
                    {f'<div class="intro">{introduction}</div>' if introduction else ""}
                    
                    {"".join([self._format_section_for_email(section) for section in sections])}
                    
                    {f'<div class="conclusion">{conclusion}</div>' if conclusion else ""}
                </div>
                <div class="footer">
                    <p><strong>Newsletter AI</strong> - Personalized content powered by AI</p>
                    <p>
                        <a href="#">Manage Preferences</a> | 
                        <a href="#">View Online</a> | 
                        <a href="#">Unsubscribe</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """.strip()

        return html_template

    def _format_section_for_email(self, section: Dict[str, Any]) -> str:
        """Format a newsletter section for email"""
        title = section.get("title", "")
        articles = section.get("articles", [])

        section_html = f'<div class="section">'
        if title:
            section_html += f"<h2>{title}</h2>"

        for article in articles:
            if isinstance(article, dict):
                article_title = article.get("title", "")
                article_content = article.get("content", "")
                article_url = article.get("url", "")

                section_html += f"""
                <div class="article">
                    <h3>{f'<a href="{article_url}">{article_title}</a>' if article_url else article_title}</h3>
                    <p>{article_content[:200]}...</p>
                </div>
                """
            else:
                # Handle string articles (from writing agent)
                section_html += f'<div class="article">{str(article)}</div>'

        section_html += "</div>"
        return section_html

    def _html_to_plain_text(self, html_content: str) -> str:
        """Convert HTML content to plain text"""
        # Simple HTML to text conversion
        import re

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", html_content)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text


# Global email service instance
email_service = EmailService()
