"""
Cron Job Routes
Endpoints for scheduled tasks (called by external cron services like Render Cron Jobs)
"""
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
from loguru import logger

from ..services.abandoned_checkout_service import abandoned_checkout_service

router = APIRouter()


class CronResponse(BaseModel):
    """Response model for cron jobs"""
    success: bool
    job_name: str
    results: Dict[str, Any]
    message: str


def verify_cron_secret(authorization: str = Header(None)) -> bool:
    """
    Verify cron job is authorized
    
    Checks for CRON_SECRET environment variable
    Authorization header should be: Bearer {CRON_SECRET}
    """
    cron_secret = os.getenv('CRON_SECRET')
    
    if not cron_secret:
        logger.warning("CRON_SECRET not set - cron jobs are unprotected!")
        return True  # Allow if secret not set (for development)
    
    if not authorization:
        return False
    
    if not authorization.startswith('Bearer '):
        return False
    
    provided_secret = authorization.replace('Bearer ', '')
    return provided_secret == cron_secret


@router.post("/cron/abandoned-checkout", response_model=CronResponse)
async def run_abandoned_checkout_cron(
    authorization: str = Header(None, alias="Authorization")
):
    """
    Process abandoned checkouts - send reminder emails
    
    This endpoint should be called by a cron job every hour.
    
    **Authorization**: Requires `CRON_SECRET` in Authorization header as Bearer token
    
    **Example**:
    ```bash
    curl -X POST https://api.alprina.com/v1/cron/abandoned-checkout \
      -H "Authorization: Bearer your-cron-secret"
    ```
    
    **Render Cron Job Setup**:
    1. Go to Render Dashboard → Create Cron Job
    2. Name: "Abandoned Checkout Emails"
    3. Schedule: `0 * * * *` (every hour)
    4. Command: `curl -X POST https://api.alprina.com/v1/cron/abandoned-checkout -H "Authorization: Bearer $CRON_SECRET"`
    5. Environment: Add CRON_SECRET variable
    
    **What it does**:
    - Finds users who signed up 1+ hours ago
    - Haven't completed checkout (tier: none)
    - Sends reminder email via Resend
    - Marks as sent to avoid duplicates
    """
    # Verify authorization
    if not verify_cron_secret(authorization):
        logger.warning("Unauthorized cron job attempt")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized - invalid or missing CRON_SECRET"
        )
    
    try:
        logger.info("🕐 Running abandoned checkout cron job")
        
        # Process abandoned checkouts (users who signed up 1+ hours ago)
        results = await abandoned_checkout_service.process_abandoned_checkouts(
            hours_since_signup=1
        )
        
        message = f"Processed {results['found']} users: {results['sent']} emails sent, {results['failed']} failed"
        logger.info(f"✅ {message}")
        
        return CronResponse(
            success=True,
            job_name="abandoned_checkout",
            results=results,
            message=message
        )
    
    except Exception as e:
        logger.error(f"❌ Abandoned checkout cron failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cron job failed: {str(e)}"
        )


@router.get("/cron/health")
async def cron_health_check():
    """
    Health check for cron jobs
    
    Returns status of cron job system
    """
    cron_secret_set = bool(os.getenv('CRON_SECRET'))
    resend_api_key_set = bool(os.getenv('RESEND_API_KEY'))
    
    return {
        "status": "healthy",
        "cron_secret_configured": cron_secret_set,
        "resend_configured": resend_api_key_set,
        "jobs_available": [
            {
                "name": "abandoned_checkout",
                "endpoint": "/v1/cron/abandoned-checkout",
                "method": "POST",
                "schedule": "Every hour (0 * * * *)",
                "description": "Send reminder emails to users who haven't completed checkout"
            }
        ]
    }


@router.post("/cron/test-email")
async def test_abandoned_email(
    authorization: str = Header(None, alias="Authorization"),
    test_email: str = "test@example.com"
):
    """
    Test abandoned checkout email (for development)
    
    Sends a test email without checking database
    """
    if not verify_cron_secret(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Create fake user data for testing
        from datetime import datetime
        test_user = {
            "id": "test-user-id",
            "email": test_email,
            "full_name": "Test User",
            "created_at": datetime.utcnow()
        }
        
        success = await abandoned_checkout_service.send_reminder_email(test_user)
        
        if success:
            return {
                "success": True,
                "message": f"Test email sent to {test_email}",
                "email": test_email
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send test email"
            )
    
    except Exception as e:
        logger.error(f"Test email failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )
