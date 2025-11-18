"""
GitHub Webhooks Handler for Auto-Scan Integration
Handles PR events and triggers security scans automatically.
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Header
from typing import Optional
import hmac
import hashlib
import os
from loguru import logger
from datetime import datetime

from ..services.github_service import GitHubService
from ..services.github_scanner import GitHubScanner
from ..services.neon_service import neon_service

router = APIRouter()
github_service = GitHubService()
github_scanner = GitHubScanner()

# GitHub App credentials
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify that webhook came from GitHub."""
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET not set, skipping signature verification")
        return True  # Allow in development
    
    expected_signature = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
):
    """
    Handle GitHub webhooks for auto-scan integration.
    
    Supported events:
    - pull_request (opened, synchronize, reopened)
    - push (to main branch)
    - installation (created, deleted)
    - installation_repositories (added, removed)
    """
    try:
        # Read raw body for signature verification
        body = await request.body()
        
        # Verify signature
        if x_hub_signature_256:
            if not verify_github_signature(body, x_hub_signature_256):
                logger.warning(f"Invalid GitHub webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON payload
        payload = await request.json()
        
        logger.info(f"📥 GitHub webhook received: {x_github_event} (delivery: {x_github_delivery})")
        
        # Log webhook event to database
        if neon_service.is_enabled():
            await _log_webhook_event(
                event_type=x_github_event or "unknown",
                delivery_id=x_github_delivery or "",
                payload=payload
            )
        
        # Handle different event types
        if x_github_event == "pull_request":
            background_tasks.add_task(handle_pull_request, payload)
        elif x_github_event == "push":
            background_tasks.add_task(handle_push, payload)
        elif x_github_event == "installation":
            background_tasks.add_task(handle_installation, payload)
        elif x_github_event == "installation_repositories":
            background_tasks.add_task(handle_installation_repositories, payload)
        else:
            logger.info(f"Ignoring event type: {x_github_event}")
        
        return {"status": "accepted", "event": x_github_event}
    
    except Exception as e:
        logger.error(f"Error handling GitHub webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_pull_request(payload: dict):
    """Handle pull request events (opened, synchronize, reopened)."""
    try:
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        repository = payload.get("repository", {})
        installation = payload.get("installation", {})
        
        # Only scan on: opened, synchronize (new commits), reopened
        if action not in ["opened", "synchronize", "reopened"]:
            logger.info(f"Ignoring PR action: {action}")
            return
        
        installation_id = installation.get("id")
        repo_full_name = repository.get("full_name")
        pr_number = pr.get("number")
        pr_head_sha = pr.get("head", {}).get("sha")
        pr_base_sha = pr.get("base", {}).get("sha")
        
        logger.info(f"🔍 Scanning PR #{pr_number} in {repo_full_name} (action: {action})")
        
        # Get access token for installation
        access_token = await github_service.get_installation_token(installation_id)
        
        # Get list of changed files
        changed_files = await github_service.get_pr_changed_files(
            repo_full_name,
            pr_number,
            access_token
        )
        
        logger.info(f"📄 Found {len(changed_files)} changed files")
        
        # Scan changed files
        scan_results = await github_scanner.scan_pr_changes(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            changed_files=changed_files,
            base_sha=pr_base_sha,
            head_sha=pr_head_sha,
            access_token=access_token
        )
        
        # Post comment on PR with results
        await github_service.post_pr_comment(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            scan_results=scan_results,
            access_token=access_token
        )
        
        logger.info(f"✅ PR scan complete for #{pr_number}")
        
    except Exception as e:
        logger.error(f"Error handling pull_request webhook: {e}")
        raise


async def handle_push(payload: dict):
    """Handle push events to main branch."""
    try:
        ref = payload.get("ref")
        repository = payload.get("repository", {})
        installation = payload.get("installation", {})
        commits = payload.get("commits", [])
        
        # Only scan pushes to default branch (main/master)
        default_branch = repository.get("default_branch", "main")
        if ref != f"refs/heads/{default_branch}":
            logger.info(f"Ignoring push to non-default branch: {ref}")
            return
        
        installation_id = installation.get("id")
        repo_full_name = repository.get("full_name")
        
        logger.info(f"🔍 Scanning push to {repo_full_name}/{default_branch}")
        
        # Get access token
        access_token = await github_service.get_installation_token(installation_id)
        
        # Get changed files from commits
        changed_files = []
        for commit in commits:
            changed_files.extend(commit.get("added", []))
            changed_files.extend(commit.get("modified", []))
        
        # Remove duplicates
        changed_files = list(set(changed_files))
        
        logger.info(f"📄 Found {len(changed_files)} changed files across {len(commits)} commits")
        
        # Scan changed files
        scan_results = await github_scanner.scan_push_changes(
            repo_full_name=repo_full_name,
            changed_files=changed_files,
            access_token=access_token
        )
        
        # Create GitHub check run with results
        await github_service.create_check_run(
            repo_full_name=repo_full_name,
            head_sha=payload.get("after"),
            scan_results=scan_results,
            access_token=access_token
        )
        
        logger.info(f"✅ Push scan complete for {repo_full_name}")
        
    except Exception as e:
        logger.error(f"Error handling push webhook: {e}")
        raise


async def handle_installation(payload: dict):
    """Handle GitHub App installation events."""
    try:
        action = payload.get("action")
        installation = payload.get("installation", {})
        repositories = payload.get("repositories", [])
        
        installation_id = installation.get("id")
        account = installation.get("account", {})
        account_login = account.get("login")
        
        logger.info(f"🔧 Installation {action}: {account_login} (ID: {installation_id})")
        
        if action == "created":
            # Store installation in database
            if neon_service.is_enabled():
                await _save_installation(
                    installation_id=installation_id,
                    account_login=account_login,
                    account_type=account.get("type"),
                    repositories=[repo.get("full_name") for repo in repositories]
                )
            
            logger.info(f"✅ Installation saved for {account_login}")
            
        elif action == "deleted":
            # Remove installation from database
            if neon_service.is_enabled():
                await _delete_installation(installation_id)
            
            logger.info(f"✅ Installation removed for {account_login}")
            
    except Exception as e:
        logger.error(f"Error handling installation webhook: {e}")
        raise


async def handle_installation_repositories(payload: dict):
    """Handle repository access changes."""
    try:
        action = payload.get("action")
        installation = payload.get("installation", {})
        repositories_added = payload.get("repositories_added", [])
        repositories_removed = payload.get("repositories_removed", [])
        
        installation_id = installation.get("id")
        
        logger.info(f"📦 Repositories {action} for installation {installation_id}")
        
        if action == "added" and repositories_added:
            # Add repositories to database
            if neon_service.is_enabled():
                await _add_repositories(
                    installation_id=installation_id,
                    repositories=[repo.get("full_name") for repo in repositories_added]
                )
            
            logger.info(f"✅ Added {len(repositories_added)} repositories")
            
        elif action == "removed" and repositories_removed:
            # Remove repositories from database
            if neon_service.is_enabled():
                await _remove_repositories(
                    installation_id=installation_id,
                    repositories=[repo.get("full_name") for repo in repositories_removed]
                )
            
            logger.info(f"✅ Removed {len(repositories_removed)} repositories")
            
    except Exception as e:
        logger.error(f"Error handling installation_repositories webhook: {e}")
        raise


# Database helper functions
async def _log_webhook_event(event_type: str, delivery_id: str, payload: dict):
    """Log webhook event to database."""
    try:
        async with neon_service.get_pool() as pool:
            await pool.execute(
                """
                INSERT INTO github_webhook_events (event_type, delivery_id, payload, received_at)
                VALUES ($1, $2, $3, $4)
                """,
                event_type,
                delivery_id,
                payload,
                datetime.utcnow()
            )
    except Exception as e:
        logger.error(f"Error logging webhook event: {e}")


async def _save_installation(
    installation_id: int,
    account_login: str,
    account_type: str,
    repositories: list
):
    """Save GitHub installation to database."""
    try:
        async with neon_service.get_pool() as pool:
            # Insert installation
            await pool.execute(
                """
                INSERT INTO github_installations (
                    installation_id, account_login, account_type, installed_at
                )
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (installation_id) DO UPDATE
                SET account_login = $2, account_type = $3, installed_at = $4
                """,
                installation_id,
                account_login,
                account_type,
                datetime.utcnow()
            )
            
            # Insert repositories
            for repo_full_name in repositories:
                await pool.execute(
                    """
                    INSERT INTO github_repositories (
                        installation_id, full_name, added_at
                    )
                    VALUES ($1, $2, $3)
                    ON CONFLICT (installation_id, full_name) DO NOTHING
                    """,
                    installation_id,
                    repo_full_name,
                    datetime.utcnow()
                )
    except Exception as e:
        logger.error(f"Error saving installation: {e}")


async def _delete_installation(installation_id: int):
    """Remove installation from database."""
    try:
        async with neon_service.get_pool() as pool:
            await pool.execute(
                "DELETE FROM github_installations WHERE installation_id = $1",
                installation_id
            )
    except Exception as e:
        logger.error(f"Error deleting installation: {e}")


async def _add_repositories(installation_id: int, repositories: list):
    """Add repositories to installation."""
    try:
        async with neon_service.get_pool() as pool:
            for repo_full_name in repositories:
                await pool.execute(
                    """
                    INSERT INTO github_repositories (
                        installation_id, full_name, added_at
                    )
                    VALUES ($1, $2, $3)
                    ON CONFLICT (installation_id, full_name) DO NOTHING
                    """,
                    installation_id,
                    repo_full_name,
                    datetime.utcnow()
                )
    except Exception as e:
        logger.error(f"Error adding repositories: {e}")


async def _remove_repositories(installation_id: int, repositories: list):
    """Remove repositories from installation."""
    try:
        async with neon_service.get_pool() as pool:
            await pool.execute(
                """
                DELETE FROM github_repositories
                WHERE installation_id = $1 AND full_name = ANY($2)
                """,
                installation_id,
                repositories
            )
    except Exception as e:
        logger.error(f"Error removing repositories: {e}")
