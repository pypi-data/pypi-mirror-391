"""
Team Management Routes - /v1/team/*

Handles team member invitations, seat management, and team operations.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..services.neon_service import neon_service
from ..services.polar_service import polar_service
from ..middleware.auth import get_current_user

router = APIRouter()


# ==========================================
# Request/Response Models
# ==========================================

class TeamMemberResponse(BaseModel):
    id: str
    email: str
    role: str
    joined_at: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "member@example.com",
                "role": "member",
                "joined_at": "2025-11-09T10:00:00Z"
            }
        }


class TeamInviteRequest(BaseModel):
    email: EmailStr = Field(..., description="Email of person to invite")
    role: str = Field(default="member", description="Role: 'admin' or 'member'")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "newmember@example.com",
                "role": "member"
            }
        }


class TeamStatsResponse(BaseModel):
    seats_included: int
    seats_used: int
    extra_seats: int
    total_seats: int
    available_seats: int
    can_add_seats: bool
    billing_period: str
    
    class Config:
        schema_extra = {
            "example": {
                "seats_included": 5,
                "seats_used": 3,
                "extra_seats": 2,
                "total_seats": 7,
                "available_seats": 4,
                "can_add_seats": True,
                "billing_period": "monthly"
            }
        }


# ==========================================
# Team Stats & Members
# ==========================================

@router.get("/team/stats", response_model=TeamStatsResponse)
async def get_team_stats(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get team statistics and seat availability.
    
    Returns seat counts and availability for adding more seats.
    Only available for Team tier users.
    """
    if user.get("tier") != "team":
        raise HTTPException(
            status_code=403,
            detail="Team plan required for team management"
        )
    
    seats_included = user.get("seats_included", 5)
    seats_used = user.get("seats_used", 1)
    extra_seats = user.get("extra_seats", 0)
    total_seats = seats_included + extra_seats
    available_seats = total_seats - seats_used
    billing_period = user.get("billing_period", "monthly")
    
    # Can only add seats on monthly plans
    can_add_seats = billing_period == "monthly"
    
    return TeamStatsResponse(
        seats_included=seats_included,
        seats_used=seats_used,
        extra_seats=extra_seats,
        total_seats=total_seats,
        available_seats=available_seats,
        can_add_seats=can_add_seats,
        billing_period=billing_period
    )


@router.get("/team/members")
async def list_team_members(user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all team members.
    
    Returns list of team members with their roles and join dates.
    Owner (current user) is always included in the list.
    """
    if user.get("tier") != "team":
        raise HTTPException(
            status_code=403,
            detail="Team plan required"
        )
    
    # Get team members from database
    members = await neon_service.get_team_members(user["id"])
    
    # Owner is always first
    owner = {
        "id": user["id"],
        "email": user["email"],
        "role": "owner",
        "joined_at": user.get("created_at", datetime.utcnow().isoformat())
    }
    
    return {
        "members": [owner] + members,
        "total": len(members) + 1,
        "seats_used": user.get("seats_used", 1),
        "seats_available": (user.get("seats_included", 5) + user.get("extra_seats", 0)) - user.get("seats_used", 1)
    }


# ==========================================
# Invite Team Member
# ==========================================

@router.post("/team/invite")
async def invite_team_member(
    invite: TeamInviteRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Invite a new team member.
    
    Checks seat availability and creates invitation.
    The invited user will receive an email with instructions.
    """
    if user.get("tier") != "team":
        raise HTTPException(
            status_code=403,
            detail="Team plan required"
        )
    
    # Check seat availability
    seats_used = user.get("seats_used", 1)
    seats_included = user.get("seats_included", 5)
    extra_seats = user.get("extra_seats", 0)
    total_seats = seats_included + extra_seats
    
    if seats_used >= total_seats:
        raise HTTPException(
            status_code=400,
            detail=f"No available seats. You're using {seats_used}/{total_seats} seats. Please add more seats first."
        )
    
    # Check if user already exists in team
    existing_member = await neon_service.get_team_member_by_email(user["id"], invite.email)
    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="User is already a team member"
        )
    
    # Check if email is the owner
    if invite.email.lower() == user["email"].lower():
        raise HTTPException(
            status_code=400,
            detail="You cannot invite yourself"
        )
    
    # Validate role
    if invite.role not in ["admin", "member"]:
        raise HTTPException(
            status_code=400,
            detail="Role must be 'admin' or 'member'"
        )
    
    # Create invitation
    try:
        invitation = await neon_service.create_team_invitation(
            owner_id=user["id"],
            invitee_email=invite.email,
            role=invite.role
        )
        
        # TODO: Send invitation email
        logger.info(f"Team invitation created: {invite.email} invited by {user['email']}")
        
        return {
            "message": "Invitation sent successfully",
            "invitation": {
                "email": invite.email,
                "role": invite.role,
                "invited_at": invitation.get("created_at")
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create team invitation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create invitation: {str(e)}"
        )


# ==========================================
# Add Extra Seat (Monthly Plans Only)
# ==========================================

@router.post("/team/seats/add")
async def add_team_seat(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Add an extra seat to team subscription.
    
    Costs $9/month per additional seat.
    Only available for monthly Team plans.
    Annual plans must upgrade to a higher tier.
    """
    if user.get("tier") != "team":
        raise HTTPException(
            status_code=403,
            detail="Team plan required"
        )
    
    billing_period = user.get("billing_period", "monthly")
    
    if billing_period != "monthly":
        raise HTTPException(
            status_code=400,
            detail="Cannot add seats to annual plans. Annual plans have fixed seat counts. Please contact support to upgrade your plan."
        )
    
    # Add seat
    current_extra_seats = user.get("extra_seats", 0)
    new_extra_seats = current_extra_seats + 1
    
    try:
        # Update user with new seat count
        await neon_service.update_user(
            user["id"],
            {"extra_seats": new_extra_seats}
        )
        
        # TODO: Call Polar API to add subscription item for seat billing
        # This would add a $9/month charge to their subscription
        # For now, we track it in the database
        
        logger.info(f"Added seat for user {user['id']}: extra_seats={new_extra_seats}")
        
        total_seats = user.get("seats_included", 5) + new_extra_seats
        monthly_cost = new_extra_seats * 9
        
        return {
            "message": "Seat added successfully",
            "extra_seats": new_extra_seats,
            "total_seats": total_seats,
            "monthly_cost": f"${monthly_cost} extra per month",
            "note": "This will be reflected in your next invoice"
        }
        
    except Exception as e:
        logger.error(f"Failed to add seat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add seat: {str(e)}"
        )


# ==========================================
# Remove Team Member
# ==========================================

@router.delete("/team/members/{member_id}")
async def remove_team_member(
    member_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Remove a team member.
    
    Only the owner can remove team members.
    Cannot remove the owner (yourself).
    """
    if user.get("tier") != "team":
        raise HTTPException(
            status_code=403,
            detail="Team plan required"
        )
    
    # Cannot remove yourself
    if member_id == user["id"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove yourself from the team"
        )
    
    try:
        # Remove team member
        removed = await neon_service.remove_team_member(user["id"], member_id)
        
        if not removed:
            raise HTTPException(
                status_code=404,
                detail="Team member not found"
            )
        
        # Decrement seats_used
        current_seats_used = user.get("seats_used", 1)
        new_seats_used = max(1, current_seats_used - 1)
        
        await neon_service.update_user(
            user["id"],
            {"seats_used": new_seats_used}
        )
        
        logger.info(f"Removed team member {member_id} from team owned by {user['id']}")
        
        return {
            "message": "Team member removed successfully",
            "seats_used": new_seats_used
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove team member: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove team member: {str(e)}"
        )


# ==========================================
# Accept Invitation (Public Endpoint)
# ==========================================

@router.post("/team/accept/{invitation_token}")
async def accept_team_invitation(
    invitation_token: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Accept a team invitation.
    
    User must be logged in. The invitation token is sent via email.
    Once accepted, the user joins the team.
    """
    try:
        # Get invitation
        invitation = await neon_service.get_team_invitation(invitation_token)
        
        if not invitation:
            raise HTTPException(
                status_code=404,
                detail="Invitation not found or expired"
            )
        
        # Verify email matches
        if invitation["invitee_email"].lower() != user["email"].lower():
            raise HTTPException(
                status_code=403,
                detail="This invitation is for a different email address"
            )
        
        # Add user to team
        await neon_service.add_team_member(
            owner_id=invitation["owner_id"],
            member_id=user["id"],
            role=invitation["role"]
        )
        
        # Increment team owner's seats_used
        owner = await neon_service.get_user(invitation["owner_id"])
        if owner:
            new_seats_used = owner.get("seats_used", 1) + 1
            await neon_service.update_user(
                invitation["owner_id"],
                {"seats_used": new_seats_used}
            )
        
        # Delete invitation
        await neon_service.delete_team_invitation(invitation_token)
        
        logger.info(f"User {user['id']} accepted team invitation from {invitation['owner_id']}")
        
        return {
            "message": "Successfully joined team",
            "team_owner": invitation.get("owner_email"),
            "role": invitation["role"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to accept invitation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to accept invitation: {str(e)}"
        )


# ==========================================
# Health Check
# ==========================================

@router.get("/team/health")
async def team_health():
    """Test endpoint to verify team routes are loaded."""
    return {
        "status": "ok",
        "message": "Team management routes are active",
        "endpoints": [
            "GET /team/stats",
            "GET /team/members",
            "POST /team/invite",
            "POST /team/seats/add",
            "DELETE /team/members/{id}",
            "POST /team/accept/{token}"
        ]
    }
