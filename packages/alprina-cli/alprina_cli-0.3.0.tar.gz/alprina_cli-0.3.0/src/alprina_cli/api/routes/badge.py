"""
Badge API routes for Alprina security badge system.
Handles badge configuration, generation, and verification.
"""

from fastapi import APIRouter, HTTPException, Header, Response, Request
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, timedelta
import logging

from ..services.neon_service import neon_service
from ...services.badge_generator import BadgeGenerator

logger = logging.getLogger(__name__)

router = APIRouter()
badge_generator = BadgeGenerator()


# Pydantic models
class BadgeConfig(BaseModel):
    enabled: bool = False
    style: Literal["standard", "minimal", "detailed"] = "standard"
    theme: Literal["light", "dark"] = "light"
    size: Literal["small", "medium", "large"] = "medium"
    custom_text: Optional[str] = None
    show_grade: bool = True
    show_date: bool = False


class BadgeConfigResponse(BaseModel):
    id: str
    user_id: str
    enabled: bool
    style: str
    theme: str
    size: str
    custom_text: Optional[str]
    show_grade: bool
    show_date: bool
    embed_code_iframe: str
    embed_code_static: str
    verification_url: str
    created_at: datetime
    updated_at: datetime


class BadgeAnalytics(BaseModel):
    total_impressions: int
    total_clicks: int
    total_verifications: int
    impressions_today: int
    clicks_today: int
    verifications_today: int


class VerificationData(BaseModel):
    user_id: str
    company_name: Optional[str]
    security_grade: str
    last_scan_date: Optional[datetime]
    total_scans: int
    status: str
    verified: bool


# Badge configuration endpoints
@router.get("/config")
async def get_badge_config(
    authorization: str = Header(None)
) -> BadgeConfigResponse:
    """Get user's badge configuration."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    user_id = authorization.replace("Bearer ", "")

    try:
        # Get or create badge config
        query = """
        SELECT
            id, user_id, enabled, style, theme, size,
            custom_text, show_grade, show_date,
            created_at, updated_at
        FROM badge_configs
        WHERE user_id = $1
        """
        result = await neon_service.execute(query, user_id)

        if not result:
            # Create default config
            insert_query = """
            INSERT INTO badge_configs (user_id, enabled, style, theme, size)
            VALUES ($1, false, 'standard', 'light', 'medium')
            RETURNING id, user_id, enabled, style, theme, size,
                      custom_text, show_grade, show_date,
                      created_at, updated_at
            """
            result = await neon_service.execute(insert_query, user_id)

        config = result[0]

        # Generate embed codes
        base_url = "https://alprina.com"  # TODO: Use environment variable
        verification_url = f"{base_url}/verify/{user_id}"

        iframe_code = f'<iframe src="{base_url}/badge/{user_id}" width="200" height="80" frameborder="0" style="border: none;"></iframe>'
        static_code = f'<a href="{verification_url}" target="_blank"><img src="{base_url}/api/v1/badge/{user_id}/svg" alt="Secured by Alprina" /></a>'

        return BadgeConfigResponse(
            id=str(config['id']),
            user_id=str(config['user_id']),
            enabled=config['enabled'],
            style=config['style'],
            theme=config['theme'],
            size=config['size'],
            custom_text=config['custom_text'],
            show_grade=config['show_grade'],
            show_date=config['show_date'],
            embed_code_iframe=iframe_code,
            embed_code_static=static_code,
            verification_url=verification_url,
            created_at=config['created_at'],
            updated_at=config['updated_at']
        )

    except Exception as e:
        logger.error(f"Error getting badge config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get badge configuration")


@router.put("/config")
async def update_badge_config(
    config: BadgeConfig,
    authorization: str = Header(None)
) -> dict:
    """Update user's badge configuration."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    user_id = authorization.replace("Bearer ", "")

    try:
        # Upsert badge config
        query = """
        INSERT INTO badge_configs (
            user_id, enabled, style, theme, size,
            custom_text, show_grade, show_date
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (user_id)
        DO UPDATE SET
            enabled = EXCLUDED.enabled,
            style = EXCLUDED.style,
            theme = EXCLUDED.theme,
            size = EXCLUDED.size,
            custom_text = EXCLUDED.custom_text,
            show_grade = EXCLUDED.show_grade,
            show_date = EXCLUDED.show_date,
            updated_at = NOW()
        RETURNING id
        """

        result = await neon_service.execute(
            query,
            user_id,
            config.enabled,
            config.style,
            config.theme,
            config.size,
            config.custom_text,
            config.show_grade,
            config.show_date
        )

        return {
            "success": True,
            "message": "Badge configuration updated successfully",
            "config_id": str(result[0]['id'])
        }

    except Exception as e:
        logger.error(f"Error updating badge config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update badge configuration")


# Badge generation endpoint
@router.get("/{user_id}/svg")
async def generate_badge_svg(
    user_id: str,
    style: Optional[str] = "standard",
    theme: Optional[str] = "light",
    size: Optional[str] = "medium"
) -> Response:
    """Generate SVG badge for a user."""
    try:
        # Get user's badge config
        config_query = """
        SELECT enabled, style, theme, size, custom_text, show_grade, show_date
        FROM badge_configs
        WHERE user_id = $1
        """
        config_result = await neon_service.execute(config_query, user_id)

        # Check if badge is enabled
        if not config_result or not config_result[0]['enabled']:
            raise HTTPException(status_code=404, detail="Badge not enabled for this user")

        config = config_result[0]

        # Get user's latest security data
        scan_query = """
        SELECT
            security_score,
            scan_date,
            critical_count,
            high_count,
            medium_count,
            low_count
        FROM scans
        WHERE user_id = $1
        ORDER BY scan_date DESC
        LIMIT 1
        """
        scan_result = await neon_service.execute(scan_query, user_id)

        # Calculate grade
        if scan_result:
            scan = scan_result[0]
            score = scan.get('security_score', 0)

            if score >= 90:
                grade = "A+"
            elif score >= 85:
                grade = "A"
            elif score >= 80:
                grade = "B+"
            elif score >= 75:
                grade = "B"
            elif score >= 70:
                grade = "C+"
            else:
                grade = "C"

            last_scan = scan.get('scan_date')
        else:
            grade = "N/A"
            last_scan = None

        # Use query params or config defaults
        final_style = style or config['style']
        final_theme = theme or config['theme']
        final_size = size or config['size']

        # Generate SVG
        svg_content = badge_generator.generate_svg(
            style=final_style,
            theme=final_theme,
            size=final_size,
            grade=grade if config['show_grade'] else None,
            last_scan=last_scan if config['show_date'] else None,
            custom_text=config['custom_text']
        )

        # Track impression (async, don't block)
        try:
            track_query = """
            INSERT INTO badge_analytics (badge_config_id, event_type)
            SELECT id, 'impression'
            FROM badge_configs
            WHERE user_id = $1
            """
            await neon_service.execute(track_query, user_id)
        except Exception as e:
            logger.warning(f"Failed to track impression: {str(e)}")

        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Cache-Control": "public, max-age=300",  # 5 minutes
                "X-Content-Type-Options": "nosniff"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating badge SVG: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate badge")


# Verification data endpoint
@router.get("/{user_id}/verify")
async def get_verification_data(
    user_id: str,
    request: Request
) -> VerificationData:
    """Get verification data for badge verification page."""
    try:
        # Get user info
        user_query = """
        SELECT email, full_name, tier, created_at
        FROM users
        WHERE id = $1
        """
        user_result = await neon_service.execute(user_query, user_id)

        if not user_result:
            raise HTTPException(status_code=404, detail="User not found")

        user = user_result[0]

        # Get latest scan data
        scan_query = """
        SELECT
            security_score,
            scan_date,
            critical_count,
            high_count,
            medium_count,
            low_count
        FROM scans
        WHERE user_id = $1
        ORDER BY scan_date DESC
        LIMIT 1
        """
        scan_result = await neon_service.execute(scan_query, user_id)

        # Get total scan count
        count_query = """
        SELECT COUNT(*) as total
        FROM scans
        WHERE user_id = $1
        """
        count_result = await neon_service.execute(count_query, user_id)
        total_scans = count_result[0]['total'] if count_result else 0

        # Determine status
        if scan_result:
            scan = scan_result[0]
            score = scan.get('security_score', 0)
            critical = scan.get('critical_count', 0)
            high = scan.get('high_count', 0)

            if score >= 90:
                grade = "A+"
            elif score >= 85:
                grade = "A"
            elif score >= 80:
                grade = "B+"
            elif score >= 75:
                grade = "B"
            elif score >= 70:
                grade = "C+"
            else:
                grade = "C"

            if critical == 0 and high == 0:
                status = "Excellent"
            elif critical == 0:
                status = "Good"
            else:
                status = "Needs Attention"

            last_scan = scan.get('scan_date')
        else:
            grade = "N/A"
            status = "No Scans"
            last_scan = None

        # Track verification view
        try:
            track_query = """
            INSERT INTO badge_verifications (
                user_id, ip_address, user_agent, referrer
            )
            VALUES ($1, $2, $3, $4)
            """
            client_ip = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            referrer = request.headers.get("referer")

            await neon_service.execute(
                track_query,
                user_id, client_ip, user_agent, referrer
            )
        except Exception as e:
            logger.warning(f"Failed to track verification: {str(e)}")

        # Extract company name from email or use full name
        company_name = user.get('full_name') or user.get('email', '').split('@')[0]

        return VerificationData(
            user_id=user_id,
            company_name=company_name,
            security_grade=grade,
            last_scan_date=last_scan,
            total_scans=total_scans,
            status=status,
            verified=total_scans > 0
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting verification data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get verification data")


# Analytics endpoint
@router.get("/analytics")
async def get_badge_analytics(
    authorization: str = Header(None)
) -> BadgeAnalytics:
    """Get badge analytics for the authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    user_id = authorization.replace("Bearer ", "")

    try:
        query = """
        SELECT
            COUNT(CASE WHEN event_type = 'impression' THEN 1 END) as total_impressions,
            COUNT(CASE WHEN event_type = 'click' THEN 1 END) as total_clicks,
            COUNT(CASE WHEN event_type = 'impression' AND created_at >= NOW() - INTERVAL '1 day' THEN 1 END) as impressions_today,
            COUNT(CASE WHEN event_type = 'click' AND created_at >= NOW() - INTERVAL '1 day' THEN 1 END) as clicks_today
        FROM badge_analytics ba
        JOIN badge_configs bc ON ba.badge_config_id = bc.id
        WHERE bc.user_id = $1
        """

        result = await neon_service.execute(query, user_id)

        if not result:
            return BadgeAnalytics(
                total_impressions=0,
                total_clicks=0,
                total_verifications=0,
                impressions_today=0,
                clicks_today=0,
                verifications_today=0
            )

        analytics = result[0]

        # Get verification counts
        verify_query = """
        SELECT
            COUNT(*) as total_verifications,
            COUNT(CASE WHEN verified_at >= NOW() - INTERVAL '1 day' THEN 1 END) as verifications_today
        FROM badge_verifications
        WHERE user_id = $1
        """

        verify_result = await neon_service.execute(verify_query, user_id)
        verify_data = verify_result[0] if verify_result else {}

        return BadgeAnalytics(
            total_impressions=analytics.get('total_impressions', 0),
            total_clicks=analytics.get('total_clicks', 0),
            total_verifications=verify_data.get('total_verifications', 0),
            impressions_today=analytics.get('impressions_today', 0),
            clicks_today=analytics.get('clicks_today', 0),
            verifications_today=verify_data.get('verifications_today', 0)
        )

    except Exception as e:
        logger.error(f"Error getting badge analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get badge analytics")
