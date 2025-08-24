"""
Email service using Resend API for OTP and newsletter delivery
Enhanced with delivery tracking, retry mechanisms, and personalized templates
"""

import secrets
import string
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from app.core.config import settings
from app.services.email_templates import template_manager, NewsletterType


class EmailStatus(Enum):
    """Email delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    FAILED = "failed"
    RETRY = "retry"


class EmailService:
    """Enhanced email service using Resend API with delivery tracking and retry mechanisms"""

    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        # Use custom domain if configured, otherwise use Resend sandbox domain
        self.from_email = getattr(settings, 'RESEND_FROM_EMAIL', None) or "Newsletter AI <onboarding@resend.dev>"
        self.max_retries = 3
        self.retry_delays = [1, 5, 15]  # seconds

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
        user_preferences: Optional[Dict[str, Any]] = None,
        subject_line: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Send newsletter email using Resend API with delivery tracking and retry mechanisms
        
        Returns:
            Tuple[bool, Dict[str, Any]]: (success, delivery_info)
        """
        delivery_info = {
            "email": email,
            "status": EmailStatus.PENDING.value,
            "attempts": 0,
            "sent_at": None,
            "resend_id": None,
            "error": None
        }

        if not self.api_key:
            delivery_info["status"] = EmailStatus.FAILED.value
            delivery_info["error"] = "Resend API key not configured"
            print("⚠️  Resend API key not configured")
            return False, delivery_info

        # Try sending with retry mechanism
        for attempt in range(self.max_retries):
            delivery_info["attempts"] = attempt + 1
            
            try:
                import resend
                resend.api_key = self.api_key

                # Create personalized newsletter content
                html_content, plain_text, subject = self._create_personalized_newsletter(
                    newsletter_data, user_preferences, subject_line
                )

                params = {
                    "from": self.from_email,
                    "to": [email],
                    "subject": subject,
                    "html": html_content,
                    "text": plain_text,
                    "tags": [
                        {"name": "type", "value": "newsletter"},
                        {"name": "user_id", "value": email.replace("@", "_at_").replace(".", "_dot_").replace("-", "_dash_")[:50]}
                    ]
                }

                email_response = resend.Emails.send(params)
                
                # Extract Resend ID for tracking
                resend_id = email_response.get("id") if isinstance(email_response, dict) else str(email_response)
                
                delivery_info.update({
                    "status": EmailStatus.SENT.value,
                    "sent_at": datetime.utcnow().isoformat(),
                    "resend_id": resend_id,
                    "error": None
                })
                
                print(f"✅ Newsletter sent to {email} (attempt {attempt + 1}): {resend_id}")
                return True, delivery_info

            except ImportError:
                error_msg = "Resend package not installed. Install with: pip install resend"
                delivery_info["error"] = error_msg
                print(f"⚠️  {error_msg}")
                break  # Don't retry for import errors
                
            except Exception as e:
                error_msg = f"Failed to send newsletter (attempt {attempt + 1}): {str(e)}"
                delivery_info["error"] = error_msg
                print(f"❌ {error_msg}")
                
                # If not the last attempt, wait before retrying
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
                    delivery_info["status"] = EmailStatus.RETRY.value
                    continue

        # All attempts failed
        delivery_info["status"] = EmailStatus.FAILED.value
        return False, delivery_info

    async def send_newsletter_batch(
        self,
        recipients: List[Dict[str, Any]],
        newsletter_data: Dict[str, Any],
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Send newsletter to multiple recipients in batches
        
        Args:
            recipients: List of dicts with 'email' and optional 'preferences'
            newsletter_data: Newsletter content data
            batch_size: Number of emails to send concurrently
            
        Returns:
            Dict with batch results and statistics
        """
        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "delivery_info": []
        }
        
        # Process recipients in batches
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            # Send batch concurrently
            tasks = []
            for recipient in batch:
                email = recipient["email"]
                preferences = recipient.get("preferences", {})
                
                task = self.send_newsletter_email(
                    email=email,
                    newsletter_data=newsletter_data,
                    user_preferences=preferences
                )
                tasks.append(task)
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results["failed"] += 1
                    results["delivery_info"].append({
                        "email": batch[j]["email"],
                        "status": EmailStatus.FAILED.value,
                        "error": str(result)
                    })
                else:
                    success, delivery_info = result
                    if success:
                        results["sent"] += 1
                    else:
                        results["failed"] += 1
                    results["delivery_info"].append(delivery_info)
            
            # Small delay between batches to avoid rate limiting
            if i + batch_size < len(recipients):
                await asyncio.sleep(1)
        
        print(f"📊 Batch send complete: {results['sent']}/{results['total']} sent successfully")
        return results

    def _create_personalized_newsletter(
        self,
        newsletter_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None,
        subject_line: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """
        Create personalized newsletter content based on user preferences
        
        Returns:
            Tuple[str, str, str]: (html_content, plain_text, subject)
        """
        # Extract user preferences
        preferences = user_preferences or {}
        user_name = preferences.get("name", "")
        topics = preferences.get("topics", [])
        
        # Determine newsletter type
        newsletter_type = self._determine_newsletter_type(newsletter_data)
        
        # Create personalized HTML content using template manager
        html_content = template_manager.get_template(
            newsletter_type, newsletter_data, preferences
        )
        
        # Create plain text version
        plain_text = self._html_to_plain_text(html_content)
        
        # Create personalized subject line
        subject = self._create_personalized_subject(
            newsletter_data, preferences, subject_line
        )
        
        return html_content, plain_text, subject

    def _determine_newsletter_type(self, newsletter_data: Dict[str, Any]) -> NewsletterType:
        """Determine the appropriate newsletter type based on content"""
        title = newsletter_data.get("title", "").lower()
        custom_prompt = newsletter_data.get("custom_prompt", "")
        
        if custom_prompt:
            return NewsletterType.CUSTOM_PROMPT
        elif "breaking" in title or "urgent" in title:
            return NewsletterType.BREAKING_NEWS
        elif "weekly" in title or "roundup" in title:
            return NewsletterType.WEEKLY_ROUNDUP
        elif "research" in title or "analysis" in title:
            return NewsletterType.RESEARCH_SUMMARY
        else:
            return NewsletterType.DAILY_DIGEST

    def _create_personalized_subject(
        self,
        newsletter_data: Dict[str, Any],
        preferences: Dict[str, Any],
        subject_line: Optional[str] = None
    ) -> str:
        """Create personalized subject line"""
        if subject_line:
            return subject_line
            
        user_name = preferences.get("name", "")
        topics = preferences.get("topics", [])
        title = newsletter_data.get("title", "Your Newsletter")
        newsletter_type = self._determine_newsletter_type(newsletter_data)
        
        # Type-specific subject lines
        if newsletter_type == NewsletterType.BREAKING_NEWS:
            return f"🚨 BREAKING: {title}"
        elif newsletter_type == NewsletterType.WEEKLY_ROUNDUP:
            return f"📊 Weekly Roundup{f' for {user_name}' if user_name else ''}"
        elif newsletter_type == NewsletterType.CUSTOM_PROMPT:
            return f"✨ Your Custom Newsletter{f', {user_name}' if user_name else ''}"
        elif newsletter_type == NewsletterType.RESEARCH_SUMMARY:
            return f"🔬 Research Summary: {title}"
        else:
            # Daily digest
            if user_name:
                subject = f"📧 {user_name}, your daily digest"
            else:
                subject = f"📧 {title}"
        
        # Add topic-specific emoji if relevant
        if topics:
            topic_emojis = {
                "tech": "💻",
                "business": "💼", 
                "science": "🔬",
                "health": "🏥",
                "finance": "💰",
                "sports": "⚽",
                "entertainment": "🎬"
            }
            for topic in topics[:1]:  # Use first topic
                if topic.lower() in topic_emojis:
                    subject = f"{topic_emojis[topic.lower()]} {subject[2:]}"  # Replace default emoji
                    break
        
        return subject

    def _create_responsive_newsletter_template(
        self, 
        newsletter_data: Dict[str, Any], 
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create responsive HTML template for newsletter with personalization"""
        preferences = user_preferences or {}
        
        # Extract content
        title = newsletter_data.get("title", "Your Newsletter")
        introduction = newsletter_data.get("introduction", "")
        sections = newsletter_data.get("sections", [])
        conclusion = newsletter_data.get("conclusion", "")
        
        # Personalization
        user_name = preferences.get("name", "")
        tone = preferences.get("tone", "professional")
        topics = preferences.get("topics", [])
        
        # Tone-based styling
        tone_styles = self._get_tone_styles(tone)
        
        # Create greeting
        greeting = self._create_personalized_greeting(user_name, tone)
        
        # Topic-based colors
        primary_color = self._get_topic_color(topics)

        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <title>{title}</title>
            <style>
                /* Reset styles */
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                
                /* Base styles */
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #2d3748; 
                    background-color: #f7fafc;
                    margin: 0;
                    padding: 0;
                    -webkit-text-size-adjust: 100%;
                    -ms-text-size-adjust: 100%;
                }}
                
                /* Container */
                .email-container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background-color: #ffffff;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                }}
                
                /* Header */
                .header {{ 
                    background: linear-gradient(135deg, {primary_color} 0%, {self._darken_color(primary_color)} 100%); 
                    padding: 40px 30px; 
                    text-align: center; 
                    color: white;
                }}
                .header h1 {{ 
                    font-size: 28px; 
                    font-weight: 700; 
                    margin-bottom: 8px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header .date {{ 
                    font-size: 14px; 
                    opacity: 0.9;
                    font-weight: 300;
                }}
                
                /* Greeting */
                .greeting {{ 
                    padding: 25px 30px 15px; 
                    background-color: #f8f9fa;
                    border-left: 4px solid {primary_color};
                    {tone_styles['greeting']}
                }}
                
                /* Content */
                .content {{ 
                    padding: 30px; 
                }}
                
                /* Introduction */
                .intro {{ 
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 25px; 
                    border-radius: 12px; 
                    margin: 25px 0; 
                    border-left: 5px solid {primary_color};
                    {tone_styles['intro']}
                }}
                
                /* Sections */
                .section {{ 
                    margin: 35px 0; 
                    padding: 25px 0; 
                    border-bottom: 1px solid #e2e8f0;
                }}
                .section:last-child {{ 
                    border-bottom: none; 
                }}
                .section h2 {{ 
                    color: #1a202c; 
                    font-size: 22px; 
                    font-weight: 600;
                    margin-bottom: 20px;
                    padding-bottom: 8px;
                    border-bottom: 3px solid {primary_color};
                    display: inline-block;
                }}
                
                /* Articles */
                .article {{ 
                    margin: 20px 0; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    border-radius: 10px;
                    border-left: 4px solid {primary_color};
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    transition: transform 0.2s ease;
                }}
                .article:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                .article h3 {{ 
                    color: #2d3748; 
                    font-size: 18px; 
                    font-weight: 600;
                    margin-bottom: 12px;
                    line-height: 1.4;
                }}
                .article p {{ 
                    color: #4a5568; 
                    font-size: 15px;
                    line-height: 1.6;
                    margin-bottom: 10px;
                }}
                .article .read-more {{
                    color: {primary_color};
                    font-weight: 500;
                    text-decoration: none;
                    font-size: 14px;
                }}
                .article .read-more:hover {{
                    text-decoration: underline;
                }}
                
                /* Links */
                a {{ 
                    color: {primary_color}; 
                    text-decoration: none; 
                }}
                a:hover {{ 
                    text-decoration: underline; 
                }}
                
                /* Conclusion */
                .conclusion {{ 
                    background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%); 
                    padding: 25px; 
                    border-radius: 12px; 
                    margin: 30px 0;
                    border-left: 5px solid #38b2ac;
                    {tone_styles['conclusion']}
                }}
                
                /* Footer */
                .footer {{ 
                    background-color: #2d3748; 
                    color: #e2e8f0; 
                    padding: 30px; 
                    text-align: center; 
                }}
                .footer h3 {{
                    color: white;
                    font-size: 18px;
                    margin-bottom: 15px;
                }}
                .footer p {{
                    font-size: 14px;
                    margin-bottom: 10px;
                    opacity: 0.8;
                }}
                .footer .links {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #4a5568;
                }}
                .footer .links a {{ 
                    color: #63b3ed; 
                    margin: 0 10px;
                    font-size: 13px;
                }}
                
                /* Responsive design */
                @media only screen and (max-width: 600px) {{
                    .email-container {{ margin: 0 10px; }}
                    .header {{ padding: 30px 20px; }}
                    .header h1 {{ font-size: 24px; }}
                    .content {{ padding: 20px; }}
                    .greeting {{ padding: 20px; }}
                    .intro {{ padding: 20px; }}
                    .article {{ padding: 15px; }}
                    .conclusion {{ padding: 20px; }}
                    .footer {{ padding: 20px; }}
                }}
                
                /* Dark mode support */
                @media (prefers-color-scheme: dark) {{
                    .email-container {{ background-color: #1a202c; }}
                    .content {{ background-color: #1a202c; color: #e2e8f0; }}
                    .article {{ background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); }}
                    .article h3 {{ color: #f7fafc; }}
                    .article p {{ color: #cbd5e0; }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>📧 {title}</h1>
                    <div class="date">{datetime.now().strftime("%B %d, %Y")}</div>
                </div>
                
                {f'<div class="greeting">{greeting}</div>' if greeting else ""}
                
                <div class="content">
                    {f'<div class="intro">{introduction}</div>' if introduction else ""}
                    
                    {"".join([self._format_section_for_responsive_email(section, primary_color) for section in sections])}
                    
                    {f'<div class="conclusion">{conclusion}</div>' if conclusion else ""}
                </div>
                
                <div class="footer">
                    <h3>Newsletter AI</h3>
                    <p>Personalized content powered by AI, tailored just for you</p>
                    {f'<p>Topics: {", ".join(topics[:3])}</p>' if topics else ""}
                    <div class="links">
                        <a href="#">📊 Dashboard</a>
                        <a href="#">⚙️ Preferences</a>
                        <a href="#">🌐 View Online</a>
                        <a href="#">✉️ Unsubscribe</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """.strip()

        return html_template

    def _get_tone_styles(self, tone: str) -> Dict[str, str]:
        """Get CSS styles based on user's preferred tone"""
        styles = {
            "professional": {
                "greeting": "font-style: normal; font-weight: 500;",
                "intro": "font-style: normal;",
                "conclusion": "font-style: normal;"
            },
            "casual": {
                "greeting": "font-style: normal; font-weight: 400;",
                "intro": "font-style: normal;",
                "conclusion": "font-style: normal;"
            },
            "technical": {
                "greeting": "font-family: 'Monaco', 'Menlo', monospace; font-size: 14px;",
                "intro": "font-family: inherit;",
                "conclusion": "font-family: inherit;"
            }
        }
        return styles.get(tone, styles["professional"])

    def _get_topic_color(self, topics: List[str]) -> str:
        """Get primary color based on user's topics"""
        topic_colors = {
            "tech": "#667eea",
            "business": "#f093fb", 
            "science": "#4facfe",
            "health": "#43e97b",
            "finance": "#fa709a",
            "sports": "#ffecd2",
            "entertainment": "#a8edea"
        }
        
        if topics:
            return topic_colors.get(topics[0].lower(), "#667eea")
        return "#667eea"

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20%"""
        # Simple darkening - remove # and convert to RGB, then darken
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def _create_personalized_greeting(self, user_name: str, tone: str) -> str:
        """Create personalized greeting based on user name and tone"""
        if not user_name:
            return ""
            
        greetings = {
            "professional": f"Dear {user_name},<br><br>We hope you're having a productive day. Here's your personalized newsletter with the latest insights.",
            "casual": f"Hey {user_name}! 👋<br><br>Hope you're doing awesome! We've got some great content lined up for you today.",
            "technical": f"Hello {user_name},<br><br>System status: ✅ Ready to deliver your curated technical content and insights."
        }
        
        return greetings.get(tone, greetings["professional"])

    def _create_basic_newsletter_template(self, newsletter_data: Dict[str, Any]) -> str:
        """Create basic HTML template for newsletter (fallback)"""
        return self._create_responsive_newsletter_template(newsletter_data, {})

    def _format_section_for_responsive_email(self, section: Dict[str, Any], primary_color: str) -> str:
        """Format a newsletter section for responsive email"""
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
                article_summary = article.get("summary", "")

                # Use summary if available, otherwise truncate content
                display_content = article_summary or article_content[:250]
                if len(article_content) > 250 and not article_summary:
                    display_content += "..."

                section_html += f"""
                <div class="article">
                    <h3>{article_title}</h3>
                    <p>{display_content}</p>
                    {f'<a href="{article_url}" class="read-more">Read full article →</a>' if article_url else ""}
                </div>
                """
            else:
                # Handle string articles (from writing agent)
                section_html += f'<div class="article"><p>{str(article)}</p></div>'

        section_html += "</div>"
        return section_html

    def _format_section_for_email(self, section: Dict[str, Any]) -> str:
        """Format a newsletter section for email (legacy method)"""
        return self._format_section_for_responsive_email(section, "#667eea")

    def _html_to_plain_text(self, html_content: str) -> str:
        """Convert HTML content to plain text"""
        import re

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", html_content)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        # Add some basic formatting for readability
        text = re.sub(r"Newsletter AI", "\n\nNewsletter AI", text)
        text = re.sub(r"(\w+:)", r"\n\1", text)  # Add newlines before colons
        
        return text

    async def get_delivery_status(self, resend_id: str) -> Dict[str, Any]:
        """
        Get delivery status from Resend API
        
        Args:
            resend_id: The Resend email ID
            
        Returns:
            Dict with delivery status information
        """
        if not self.api_key or not resend_id:
            return {"status": "unknown", "error": "Missing API key or email ID"}

        try:
            import resend
            resend.api_key = self.api_key

            # Get email details from Resend
            email_details = resend.Emails.get(resend_id)
            
            return {
                "status": email_details.get("last_event", "unknown"),
                "created_at": email_details.get("created_at"),
                "from": email_details.get("from"),
                "to": email_details.get("to"),
                "subject": email_details.get("subject"),
                "resend_id": resend_id
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def handle_webhook_event(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Resend webhook events for delivery tracking
        
        Args:
            webhook_data: Webhook payload from Resend
            
        Returns:
            Dict with processed event information
        """
        event_type = webhook_data.get("type", "")
        email_data = webhook_data.get("data", {})
        
        processed_event = {
            "event_type": event_type,
            "email_id": email_data.get("email_id"),
            "timestamp": webhook_data.get("created_at"),
            "status": EmailStatus.PENDING.value
        }
        
        # Map Resend events to our status enum
        event_status_map = {
            "email.sent": EmailStatus.SENT.value,
            "email.delivered": EmailStatus.DELIVERED.value,
            "email.bounced": EmailStatus.BOUNCED.value,
            "email.complained": EmailStatus.FAILED.value,
            "email.delivery_delayed": EmailStatus.RETRY.value
        }
        
        processed_event["status"] = event_status_map.get(event_type, EmailStatus.PENDING.value)
        
        # Extract additional event data
        if event_type == "email.bounced":
            processed_event["bounce_reason"] = email_data.get("bounce", {}).get("reason")
        elif event_type == "email.complained":
            processed_event["complaint_type"] = email_data.get("complaint", {}).get("type")
        
        print(f"📧 Webhook event processed: {event_type} for email {processed_event['email_id']}")
        return processed_event

    async def validate_email_address(self, email: str) -> bool:
        """
        Validate email address format and deliverability
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if email is valid
        """
        import re
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
        
        # Check for common invalid domains
        invalid_domains = [
            'example.com', 'test.com', 'localhost', 
            'invalid.com', 'fake.com', 'dummy.com'
        ]
        
        domain = email.split('@')[1].lower()
        if domain in invalid_domains:
            return False
        
        return True

    def get_email_analytics(self, delivery_info_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate analytics from delivery information
        
        Args:
            delivery_info_list: List of delivery info dictionaries
            
        Returns:
            Dict with email analytics
        """
        total_emails = len(delivery_info_list)
        if total_emails == 0:
            return {"total": 0, "sent": 0, "failed": 0, "delivery_rate": 0.0}
        
        status_counts = {}
        for info in delivery_info_list:
            status = info.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        sent_count = status_counts.get(EmailStatus.SENT.value, 0) + status_counts.get(EmailStatus.DELIVERED.value, 0)
        failed_count = status_counts.get(EmailStatus.FAILED.value, 0) + status_counts.get(EmailStatus.BOUNCED.value, 0)
        
        delivery_rate = (sent_count / total_emails) * 100 if total_emails > 0 else 0.0
        
        return {
            "total": total_emails,
            "sent": sent_count,
            "failed": failed_count,
            "pending": status_counts.get(EmailStatus.PENDING.value, 0),
            "retry": status_counts.get(EmailStatus.RETRY.value, 0),
            "delivery_rate": round(delivery_rate, 2),
            "status_breakdown": status_counts
        }


# Global email service instance
email_service = EmailService()
