"""
Abandoned Checkout Service
Sends reminder emails to users who signed up but haven't completed checkout
"""
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
import resend
from loguru import logger

from ..api.services.neon_service import neon_service


class AbandonedCheckoutService:
    """Service for handling abandoned checkout reminders"""

    def __init__(self):
        self.resend_api_key = os.getenv('RESEND_API_KEY')
        if self.resend_api_key:
            resend.api_key = self.resend_api_key
        else:
            logger.warning("RESEND_API_KEY not set - email notifications disabled")

    async def find_abandoned_users(self, hours_since_signup: int = 1) -> List[Dict[str, Any]]:
        """
        Find users who signed up but haven't paid yet
        
        Args:
            hours_since_signup: How many hours after signup to check (default: 1)
            
        Returns:
            List of users with abandoned checkouts
        """
        if not neon_service.is_enabled():
            logger.error("Database not enabled")
            return []

        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_since_signup)
            
            query = """
            SELECT 
                u.id,
                u.email,
                u.full_name,
                u.created_at,
                u.tier,
                u.abandoned_checkout_email_sent_at
            FROM users u
            WHERE 
                -- User has no paid tier
                (u.tier IS NULL OR u.tier = 'none')
                -- Signed up more than X hours ago
                AND u.created_at < $1
                -- Haven't sent reminder yet, or sent more than 7 days ago
                AND (
                    u.abandoned_checkout_email_sent_at IS NULL 
                    OR u.abandoned_checkout_email_sent_at < NOW() - INTERVAL '7 days'
                )
                -- Not a deleted/banned account
                AND u.subscription_status != 'cancelled'
            ORDER BY u.created_at DESC
            LIMIT 100
            """
            
            result = await neon_service.execute(query, cutoff_time)
            
            logger.info(f"Found {len(result)} users with abandoned checkouts")
            return result

        except Exception as e:
            logger.error(f"Error finding abandoned users: {e}")
            return []

    async def send_reminder_email(self, user: Dict[str, Any]) -> bool:
        """
        Send abandoned checkout reminder email
        
        Args:
            user: User data dictionary with id, email, full_name, created_at
            
        Returns:
            True if email sent successfully
        """
        if not self.resend_api_key:
            logger.warning(f"Cannot send email to {user['email']} - RESEND_API_KEY not set")
            return False

        try:
            # Calculate time since signup
            signup_date = user['created_at']
            if isinstance(signup_date, str):
                signup_date = datetime.fromisoformat(signup_date.replace('Z', '+00:00'))
            
            hours_ago = int((datetime.utcnow() - signup_date.replace(tzinfo=None)).total_seconds() / 3600)
            
            # Get user's first name or use email
            first_name = user.get('full_name', '').split()[0] if user.get('full_name') else user['email'].split('@')[0]
            
            # Send email via Resend
            email_html = self._generate_email_html(first_name, hours_ago)
            email_text = self._generate_email_text(first_name, hours_ago)
            
            params = {
                "from": "Alprina <noreply@alprina.com>",
                "to": [user['email']],
                "subject": "Complete your Alprina setup 🚀",
                "html": email_html,
                "text": email_text,
            }
            
            response = resend.Emails.send(params)
            
            logger.info(f"✅ Sent abandoned checkout email to {user['email']} (ID: {response.get('id')})")
            
            # Mark as sent in database
            await self._mark_email_sent(user['id'])
            
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {user['email']}: {e}")
            return False

    async def _mark_email_sent(self, user_id: str):
        """Mark that we sent the abandoned checkout email"""
        try:
            query = """
            UPDATE users 
            SET abandoned_checkout_email_sent_at = NOW()
            WHERE id = $1
            """
            await neon_service.execute(query, user_id)
        except Exception as e:
            logger.error(f"Failed to mark email sent for user {user_id}: {e}")

    def _generate_email_html(self, first_name: str, hours_ago: int) -> str:
        """Generate HTML email content"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Your Alprina Setup</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f6f8fa;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center;">
                            <h1 style="margin: 0; color: #1a1a1a; font-size: 24px; font-weight: 600;">
                                🛡️ Complete Your Alprina Setup
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 0 40px 40px;">
                            <p style="margin: 0 0 16px; color: #444; font-size: 16px; line-height: 1.5;">
                                Hi {first_name},
                            </p>
                            
                            <p style="margin: 0 0 16px; color: #444; font-size: 16px; line-height: 1.5;">
                                You created an Alprina account {hours_ago} hour{"s" if hours_ago != 1 else ""} ago, but you haven't chosen a plan yet.
                            </p>
                            
                            <p style="margin: 0 0 24px; color: #444; font-size: 16px; line-height: 1.5;">
                                Ready to start securing your code with AI-powered scanning?
                            </p>
                            
                            <!-- Benefits -->
                            <table role="presentation" style="width: 100%; margin-bottom: 24px;">
                                <tr>
                                    <td style="padding: 16px; background-color: #f6f8fa; border-radius: 6px;">
                                        <div style="margin-bottom: 12px;">
                                            <span style="color: #10b981; font-size: 18px;">✓</span>
                                            <span style="color: #444; margin-left: 8px; font-size: 14px;">18 AI security agents</span>
                                        </div>
                                        <div style="margin-bottom: 12px;">
                                            <span style="color: #10b981; font-size: 18px;">✓</span>
                                            <span style="color: #444; margin-left: 8px; font-size: 14px;">Find vulnerabilities others miss</span>
                                        </div>
                                        <div style="margin-bottom: 12px;">
                                            <span style="color: #10b981; font-size: 18px;">✓</span>
                                            <span style="color: #444; margin-left: 8px; font-size: 14px;">GitHub integration</span>
                                        </div>
                                        <div>
                                            <span style="color: #10b981; font-size: 18px;">✓</span>
                                            <span style="color: #444; margin-left: 8px; font-size: 14px;">7-day money-back guarantee</span>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- CTA Button -->
                            <table role="presentation" style="width: 100%; margin-bottom: 24px;">
                                <tr>
                                    <td style="text-align: center;">
                                        <a href="https://alprina.com/pricing?welcome=true" 
                                           style="display: inline-block; padding: 14px 32px; background-color: #3b82f6; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">
                                            Choose Your Plan →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Plans Preview -->
                            <p style="margin: 0 0 12px; color: #666; font-size: 14px; text-align: center;">
                                <strong>Starting at just €39/month</strong>
                            </p>
                            <p style="margin: 0 0 24px; color: #666; font-size: 14px; text-align: center;">
                                Developer • Pro • Team • Enterprise
                            </p>
                            
                            <!-- Social Proof -->
                            <table role="presentation" style="width: 100%; margin-bottom: 24px;">
                                <tr>
                                    <td style="padding: 16px; background-color: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 6px;">
                                        <p style="margin: 0; color: #1e40af; font-size: 14px; font-style: italic;">
                                            "Alprina found 12 critical vulnerabilities our other tools missed. Worth every penny."
                                        </p>
                                        <p style="margin: 8px 0 0; color: #60a5fa; font-size: 12px;">
                                            — Sarah K., Lead Security Engineer
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0 0 8px; color: #666; font-size: 14px; line-height: 1.5;">
                                Questions? Just reply to this email — we're here to help!
                            </p>
                            
                            <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.5;">
                                Best regards,<br>
                                The Alprina Team
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 24px 40px; border-top: 1px solid #e5e7eb; text-align: center;">
                            <p style="margin: 0 0 8px; color: #999; font-size: 12px;">
                                <a href="https://alprina.com" style="color: #3b82f6; text-decoration: none;">Alprina.com</a>
                                •
                                <a href="https://docs.alprina.com" style="color: #3b82f6; text-decoration: none;">Documentation</a>
                                •
                                <a href="mailto:support@alprina.com" style="color: #3b82f6; text-decoration: none;">Support</a>
                            </p>
                            <p style="margin: 0; color: #999; font-size: 11px;">
                                This email was sent to you because you created an Alprina account.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    def _generate_email_text(self, first_name: str, hours_ago: int) -> str:
        """Generate plain text email content"""
        return f"""
Hi {first_name},

You created an Alprina account {hours_ago} hour{"s" if hours_ago != 1 else ""} ago, but you haven't chosen a plan yet.

Ready to start securing your code with AI-powered scanning?

What you get with Alprina:
✓ 18 AI security agents
✓ Find vulnerabilities others miss
✓ GitHub integration
✓ 7-day money-back guarantee

Choose your plan: https://alprina.com/pricing?welcome=true

Starting at just €39/month
Plans: Developer • Pro • Team • Enterprise

"Alprina found 12 critical vulnerabilities our other tools missed. Worth every penny."
— Sarah K., Lead Security Engineer

Questions? Just reply to this email — we're here to help!

Best regards,
The Alprina Team

---
Alprina.com | Documentation: https://docs.alprina.com | Support: support@alprina.com
"""

    async def process_abandoned_checkouts(self, hours_since_signup: int = 1) -> Dict[str, int]:
        """
        Find and process all abandoned checkouts
        
        Args:
            hours_since_signup: Hours after signup to send reminder (default: 1)
            
        Returns:
            Dictionary with counts of found, sent, failed
        """
        users = await self.find_abandoned_users(hours_since_signup)
        
        sent = 0
        failed = 0
        
        for user in users:
            success = await self.send_reminder_email(user)
            if success:
                sent += 1
            else:
                failed += 1
        
        logger.info(f"Processed {len(users)} abandoned checkouts: {sent} sent, {failed} failed")
        
        return {
            "found": len(users),
            "sent": sent,
            "failed": failed
        }


# Singleton instance
abandoned_checkout_service = AbandonedCheckoutService()
