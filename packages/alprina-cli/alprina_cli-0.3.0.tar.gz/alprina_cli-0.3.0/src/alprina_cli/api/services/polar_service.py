"""
Polar.sh Integration Service

Handles Polar API interactions and webhook processing.
"""

import os
import httpx
import hmac
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

# Polar API Configuration
POLAR_API_URL = "https://api.polar.sh/v1"
POLAR_API_TOKEN = os.getenv("POLAR_ACCESS_TOKEN") or os.getenv("POLAR_API_TOKEN")
POLAR_WEBHOOK_SECRET = os.getenv("POLAR_WEBHOOK_SECRET")


class PolarService:
    """Service for Polar.sh payment platform integration."""

    def __init__(self, api_token: str = POLAR_API_TOKEN):
        self.api_token = api_token
        self.api_url = POLAR_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    async def create_checkout_session(
        self,
        product_price_id: str,
        success_url: str,
        customer_email: Optional[str] = None,
        customer_metadata: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Create a Polar checkout session using the custom checkouts API.

        Args:
            product_price_id: Polar product price ID
            success_url: URL to redirect after success (use {CHECKOUT_ID} placeholder)
            customer_email: Customer email (optional)
            customer_metadata: Additional metadata
            max_retries: Maximum number of retries for rate limiting

        Returns:
            Checkout session data with URL
        """
        import asyncio
        
        # Build payload according to Polar API docs
        payload = {
            "product_price_id": product_price_id,
            "success_url": success_url,
        }
        
        if customer_email:
            payload["customer_email"] = customer_email
            
        if customer_metadata:
            payload["metadata"] = customer_metadata

        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.api_url}/checkouts/",  # Correct endpoint
                        headers=self.headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    # Handle rate limiting (429)
                    if response.status_code == 429:
                        retry_after = int(response.headers.get('retry-after', '2'))
                        if attempt < max_retries - 1:
                            logger.warning(f"Rate limited by Polar, retrying in {retry_after}s (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            logger.error("Max retries reached for rate limiting")
                            raise Exception(f"Polar API rate limit exceeded. Please try again in {retry_after} seconds.")
                    
                    # Log request and response for debugging
                    logger.info(f"Polar API request: POST {self.api_url}/checkouts/")
                    logger.info(f"Payload: {payload}")
                    logger.info(f"Response status: {response.status_code}")
                    
                    response.raise_for_status()
                    result = response.json()
                    logger.info(f"Checkout session created: {result.get('id')}")
                    return result

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code != 429:
                    error_body = e.response.text
                    logger.error(f"Polar API error: {e.response.status_code}")
                    logger.error(f"Response body: {error_body}")
                    logger.error(f"Request payload: {payload}")
                    raise Exception(f"Polar API error ({e.response.status_code}): {error_body}")
            except Exception as e:
                last_error = e
                logger.error(f"Failed to create Polar checkout (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
        
        raise last_error or Exception("Failed to create checkout session after retries")

    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get subscription details from Polar.

        Args:
            subscription_id: Polar subscription ID

        Returns:
            Subscription data
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/subscriptions/{subscription_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get subscription: {e}")
            raise

    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Cancel a subscription.

        Args:
            subscription_id: Polar subscription ID
            at_period_end: If True, cancel at end of period

        Returns:
            Updated subscription data
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/subscriptions/{subscription_id}/cancel",
                    headers=self.headers,
                    json={"at_period_end": at_period_end}
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise

    async def list_products(self) -> Dict[str, Any]:
        """
        List all available products.

        Returns:
            List of products
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/products",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to list products: {e}")
            raise

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        webhook_secret: Optional[str] = None
    ) -> bool:
        """
        Verify Polar webhook signature.

        Args:
            payload: Raw webhook payload
            signature: Signature from Polar-Signature header
            webhook_secret: Webhook secret (optional)

        Returns:
            True if signature is valid
        """
        if not webhook_secret:
            webhook_secret = POLAR_WEBHOOK_SECRET

        if not webhook_secret:
            logger.warning("Polar webhook secret not configured - skipping signature verification")
            return True  # Allow webhooks if secret not configured (dev mode)

        try:
            expected_signature = hmac.new(
                webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {e}")
            return False

    async def process_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Polar webhook event.

        Args:
            event_data: Webhook event data

        Returns:
            Processing result
        """
        event_type = event_data.get("type")
        logger.info(f"Processing Polar webhook event: {event_type}")

        try:
            if event_type == "subscription.created":
                return await self._handle_subscription_created(event_data)
            elif event_type == "subscription.updated":
                return await self._handle_subscription_updated(event_data)
            elif event_type == "subscription.cancelled":
                return await self._handle_subscription_cancelled(event_data)
            elif event_type == "payment.succeeded":
                return await self._handle_payment_succeeded(event_data)
            elif event_type == "payment.failed":
                return await self._handle_payment_failed(event_data)
            else:
                logger.warning(f"Unhandled webhook event type: {event_type}")
                return {"status": "ignored", "event_type": event_type}

        except Exception as e:
            logger.error(f"Failed to process webhook event: {e}")
            raise

    async def _handle_subscription_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.created event."""
        subscription = event_data.get("data", {})

        return {
            "status": "processed",
            "action": "subscription_created",
            "subscription_id": subscription.get("id"),
            "customer_id": subscription.get("customer_id"),
            "product_id": subscription.get("product_id")
        }

    async def _handle_subscription_updated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.updated event."""
        subscription = event_data.get("data", {})

        return {
            "status": "processed",
            "action": "subscription_updated",
            "subscription_id": subscription.get("id")
        }

    async def _handle_subscription_cancelled(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.cancelled event."""
        subscription = event_data.get("data", {})

        return {
            "status": "processed",
            "action": "subscription_cancelled",
            "subscription_id": subscription.get("id")
        }

    async def _handle_payment_succeeded(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment.succeeded event."""
        payment = event_data.get("data", {})

        return {
            "status": "processed",
            "action": "payment_succeeded",
            "payment_id": payment.get("id")
        }

    async def _handle_payment_failed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment.failed event."""
        payment = event_data.get("data", {})

        return {
            "status": "processed",
            "action": "payment_failed",
            "payment_id": payment.get("id")
        }

    def get_tier_from_product(self, product_name: str) -> str:
        """
        Map Polar product name to Alprina tier.

        Args:
            product_name: Product name from Polar

        Returns:
            Tier name (developer, pro, enterprise)
        """
        product_lower = product_name.lower()

        if "developer" in product_lower:
            return "developer"
        elif "pro" in product_lower:
            return "pro"
        elif "enterprise" in product_lower or "team" in product_lower:
            return "team"
        else:
            return "none"

    def get_tier_from_product_id(self, product_id: str) -> str:
        """
        Map Polar product ID to Alprina tier.

        Args:
            product_id: Product ID from Polar

        Returns:
            Tier name (developer, pro, team)
        """
        # Map of product IDs to tiers
        PRODUCT_ID_MAP = {
            # Monthly Plans (with metering)
            "68443920-6061-434f-880d-83d4efd50fde": "developer",  # Developer Monthly
            "fa25e85e-5295-4dd5-bdd9-5cb5cac15a0b": "pro",        # Pro Monthly
            "41768ba5-f37d-417d-a10e-fb240b702cb6": "team",       # Team Monthly
            
            # Annual Plans (fixed price, no metering)
            "e59df0ee-7287-4132-8edd-3b5fdf4a30f3": "developer",  # Developer Annual
            "eb0d9d5a-fceb-485d-aaae-36b50d8731f4": "pro",        # Pro Annual
            "2da941e8-450a-4498-a4a4-b3539456219e": "team",       # Team Annual
        }

        return PRODUCT_ID_MAP.get(product_id, "none")

    def get_tier_limits(self, tier: str) -> Dict[str, Any]:
        """
        Get usage limits for a tier.

        Args:
            tier: Tier name

        Returns:
            Dictionary with limits
        """
        limits = {
            "free": {
                "scans_per_month": 5,
                "files_per_scan": 100,
                "api_requests_per_hour": 10,
                "parallel_scans": False,
                "sequential_scans": False,
                "coordinated_chains": False,
                "advanced_reports": False
            },
            "developer": {
                "scans_per_month": 100,
                "files_per_scan": 500,
                "api_requests_per_hour": 60,
                "parallel_scans": False,
                "sequential_scans": False,
                "coordinated_chains": False,
                "advanced_reports": False
            },
            "pro": {
                "scans_per_month": None,  # Unlimited
                "files_per_scan": 5000,
                "api_requests_per_hour": 300,
                "parallel_scans": True,
                "sequential_scans": True,
                "coordinated_chains": True,
                "advanced_reports": True
            },
            "enterprise": {
                "scans_per_month": None,  # Custom
                "files_per_scan": None,  # Unlimited
                "api_requests_per_hour": None,  # Unlimited
                "parallel_scans": True,
                "sequential_scans": True,
                "coordinated_chains": True,
                "advanced_reports": True
            }
        }

        return limits.get(tier, limits["free"])

    async def ingest_usage_event(
        self,
        customer_id: str,
        event_name: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send usage event to Polar for billing.

        Args:
            customer_id: Polar customer ID or external user ID
            event_name: Event type (security_scan, ai_analysis, etc.)
            metadata: Additional event data

        Returns:
            API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/events/ingest",
                    headers=self.headers,
                    json={
                        "events": [{
                            "name": event_name,
                            "external_customer_id": customer_id,
                            "metadata": metadata
                        }]
                    },
                    timeout=10.0  # Don't block scan if Polar is slow
                )
                response.raise_for_status()
                logger.info(f"Successfully ingested {event_name} event for customer {customer_id}")
                return response.json()

        except Exception as e:
            logger.error(f"Failed to ingest usage event to Polar: {e}")
            # Don't fail the scan if billing API fails
            return {"status": "failed", "error": str(e)}

    async def ingest_scan_usage(
        self,
        user_id: str,
        scan_type: str,
        workflow_mode: str,
        files_scanned: int,
        findings_count: int,
        duration: float,
        agent: str
    ) -> None:
        """
        Track security scan usage.

        Args:
            user_id: User ID
            scan_type: Type of scan
            workflow_mode: Workflow mode used
            files_scanned: Number of files
            findings_count: Vulnerabilities found
            duration: Scan duration in seconds
            agent: Agent used
        """
        await self.ingest_usage_event(
            customer_id=user_id,
            event_name="security_scan",
            metadata={
                "scan_type": scan_type,
                "workflow_mode": workflow_mode,
                "files_scanned": files_scanned,
                "findings_count": findings_count,
                "duration_seconds": round(duration, 2),
                "agent": agent,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        logger.info(
            f"Tracked scan usage for user {user_id}: "
            f"{workflow_mode} {scan_type} scan with {agent}"
        )

    async def ingest_ai_usage(
        self,
        user_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        agent: str,
        analysis_type: str = "vulnerability_assessment"
    ) -> None:
        """
        Track AI token usage.

        Args:
            user_id: User ID
            model: LLM model used
            input_tokens: Input tokens
            output_tokens: Output tokens
            agent: Agent that used AI
            analysis_type: Type of analysis performed
        """
        total_tokens = input_tokens + output_tokens

        await self.ingest_usage_event(
            customer_id=user_id,
            event_name="ai_analysis",
            metadata={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "agent": agent,
                "analysis_type": analysis_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        logger.info(
            f"Tracked AI usage for user {user_id}: "
            f"{total_tokens} tokens on {model} via {agent}"
        )


# Create singleton instance
polar_service = PolarService()
