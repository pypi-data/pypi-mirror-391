"""
Billing and Subscription Routes

Handles Polar checkout creation, subscription management, and billing portal access.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from loguru import logger

from ..middleware.auth import get_current_user, get_current_user_no_rate_limit
from ..services.polar_service import polar_service

router = APIRouter(prefix="/v1/billing", tags=["billing"])

# Product IDs from Polar
POLAR_PRODUCT_IDS = {
    "free": "a1a52dd9-42ad-4c60-a87c-3cd99827f69e",
    "developer": "68443920-6061-434f-880d-83d4efd50fde",
    "pro": "fa25e85e-5295-4dd5-bdd9-5cb5cac15a0b"
}


class CheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    product_tier: str  # "developer", "pro", or "team"
    billing_period: str = "monthly"  # "monthly" or "annual"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    """Checkout session response."""
    checkout_url: str
    product_id: str
    tier: str


@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    user: Dict = Depends(get_current_user_no_rate_limit)  # No rate limits on checkout!
):
    """
    Create a Polar checkout session for subscription upgrade.

    Args:
        request: Checkout details (tier to upgrade to)
        user: Current authenticated user

    Returns:
        Checkout URL to redirect user to

    Example:
        POST /v1/billing/create-checkout
        {
            "product_tier": "developer",
            "success_url": "https://platform.alprina.com/billing/success"
        }
    """
    # Validate tier
    tier = request.product_tier.lower()
    billing = request.billing_period.lower()
    
    if tier not in ["developer", "pro", "team"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_tier",
                "message": f"Invalid tier '{tier}'. Must be 'developer', 'pro', or 'team'",
                "valid_tiers": ["developer", "pro", "team"]
            }
        )
    
    if billing not in ["monthly", "annual"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_billing",
                "message": f"Invalid billing period '{billing}'. Must be 'monthly' or 'annual'",
                "valid_periods": ["monthly", "annual"]
            }
        )

    # Get price ID (needed for new Polar API)
    from ..config.polar_products import get_price_id
    price_id = get_price_id(tier, billing)
    
    if not price_id:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "price_not_configured",
                "message": f"Price ID not configured for tier '{tier}' with '{billing}' billing"
            }
        )

    # Set default URLs if not provided
    base_url = "https://alprina.com"
    success_url = request.success_url or f"{base_url}/checkout/success?checkout_id={{CHECKOUT_ID}}&plan={tier}&billing={billing}"
    
    try:
        # Create checkout session with Polar (using new API format)
        checkout_data = await polar_service.create_checkout_session(
            product_price_id=price_id,
            success_url=success_url,
            customer_email=user.get("email"),
            customer_metadata={
                "user_id": str(user["id"]),  # Convert UUID to string for JSON
                "tier": tier,
                "billing": billing
            }
        )

        logger.info(
            f"Created checkout session for user {user['id']}: tier={tier}, billing={billing}"
        )

        return CheckoutResponse(
            checkout_url=checkout_data.get("url"),
            product_id=price_id,  # Return price_id for reference
            tier=tier
        )

    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "checkout_creation_failed",
                "message": "Failed to create checkout session. Please try again.",
                "details": str(e)
            }
        )


@router.get("/subscription")
async def get_subscription(user: Dict = Depends(get_current_user)):
    """
    Get current subscription details.

    Returns:
        Current subscription info including tier, status, and limits
    """
    subscription_id = user.get("polar_subscription_id")

    if not subscription_id:
        return {
            "tier": user.get("tier", "free"),
            "subscription_status": "inactive",
            "has_active_subscription": False,
            "limits": polar_service.get_tier_limits(user.get("tier", "free"))
        }

    try:
        # Get subscription from Polar
        subscription = await polar_service.get_subscription(subscription_id)

        return {
            "tier": user.get("tier"),
            "subscription_status": user.get("subscription_status"),
            "has_active_subscription": True,
            "subscription_id": subscription_id,
            "subscription_data": subscription,
            "limits": polar_service.get_tier_limits(user.get("tier", "free"))
        }

    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        return {
            "tier": user.get("tier", "free"),
            "subscription_status": user.get("subscription_status", "unknown"),
            "has_active_subscription": False,
            "error": str(e)
        }


@router.post("/cancel-subscription")
async def cancel_subscription(user: Dict = Depends(get_current_user)):
    """
    Cancel current subscription (at end of billing period).

    The subscription will remain active until the end of the current billing period.
    """
    subscription_id = user.get("polar_subscription_id")

    if not subscription_id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "no_active_subscription",
                "message": "No active subscription to cancel"
            }
        )

    try:
        # Cancel subscription with Polar (at period end)
        result = await polar_service.cancel_subscription(
            subscription_id=subscription_id,
            at_period_end=True
        )

        logger.info(f"User {user['id']} cancelled subscription {subscription_id}")

        return {
            "success": True,
            "message": "Subscription cancelled. Access will continue until end of billing period.",
            "subscription_id": subscription_id,
            "cancellation_data": result
        }

    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "cancellation_failed",
                "message": "Failed to cancel subscription. Please try again.",
                "details": str(e)
            }
        )


@router.post("/customer-portal")
async def create_customer_portal_session(user: Dict = Depends(get_current_user)):
    """
    Create a Polar customer portal session for subscription management.

    Returns:
        URL to redirect user to Polar's customer portal where they can:
        - Update payment method
        - View billing history
        - Manage subscription
        - Download invoices
    """
    try:
        # For now, return the Polar customer portal URL
        # In the future, we can create a session-specific URL with Polar API
        polar_customer_id = user.get("polar_customer_id")

        if polar_customer_id:
            # TODO: Use Polar API to create a customer portal session
            # portal_session = await polar_service.create_customer_portal_session(polar_customer_id)
            # return {"url": portal_session.url}
            pass

        # Fallback to general Polar dashboard
        return {
            "url": "https://polar.sh/dashboard",
            "message": "Redirecting to Polar billing dashboard"
        }

    except Exception as e:
        logger.error(f"Failed to create customer portal session: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "portal_creation_failed",
                "message": "Failed to create customer portal session",
                "details": str(e)
            }
        )


@router.get("/products")
async def list_products():
    """
    List all available subscription products.

    Returns:
        Available subscription tiers with pricing and features
    """
    try:
        # Get products from Polar
        products_response = await polar_service.list_products()

        return {
            "products": products_response.get("items", []),
            "product_ids": POLAR_PRODUCT_IDS
        }

    except Exception as e:
        logger.error(f"Failed to list products: {e}")
        # Return hardcoded product info as fallback
        return {
            "products": [
                {
                    "id": POLAR_PRODUCT_IDS["developer"],
                    "name": "Alprina Developer",
                    "price": "$29/month",
                    "features": [
                        "100 security scans per month",
                        "18 AI-powered security agents",
                        "Up to 500 files per scan",
                        "60 API requests per hour",
                        "HTML & PDF reports"
                    ]
                },
                {
                    "id": POLAR_PRODUCT_IDS["pro"],
                    "name": "Alprina Pro",
                    "price": "$99/month",
                    "features": [
                        "Unlimited security scans",
                        "All 18 AI-powered agents",
                        "Up to 5,000 files per scan",
                        "300 API requests per hour",
                        "Parallel agent execution",
                        "Sequential workflows",
                        "Coordinated agent chains",
                        "Advanced reports",
                        "Priority support"
                    ]
                }
            ],
            "product_ids": POLAR_PRODUCT_IDS,
            "error": "Could not fetch from Polar, using cached data"
        }
