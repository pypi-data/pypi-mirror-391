"""
Dashboard API Routes - Provides data for the dashboard overview
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..services.neon_service import neon_service
from ..middleware.auth import get_current_user
from ..services.ai_fix_service import ai_fix_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# Response Models
class VulnerabilityItem(BaseModel):
    """Individual vulnerability item"""
    id: str
    title: str
    severity: str  # critical, high, medium, low
    cvss: Optional[float] = None
    cve: Optional[str] = None
    package: Optional[str] = None
    version: Optional[str] = None
    fixed_version: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    scan_id: str
    created_at: str


class VulnerabilitiesResponse(BaseModel):
    """Response for vulnerabilities endpoint"""
    vulnerabilities: List[VulnerabilityItem]
    total_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class ScanActivityItem(BaseModel):
    """Recent scan activity item"""
    id: str
    type: str  # 'scan'
    title: str
    timestamp: str
    status: str  # completed, failed, running
    findings_count: int
    critical_count: int
    high_count: int
    scan_type: str
    workflow_mode: str


class RecentScansResponse(BaseModel):
    """Response for recent scans endpoint"""
    scans: List[ScanActivityItem]
    total_count: int


class TrendDataPoint(BaseModel):
    """Trend data point for a time period"""
    period: str
    critical: int
    high: int
    medium: int
    low: int
    total: int


class TrendsResponse(BaseModel):
    """Response for trends endpoint"""
    trends: List[TrendDataPoint]
    period_days: int


@router.get("/vulnerabilities", response_model=VulnerabilitiesResponse)
async def get_vulnerabilities(
    limit: int = Query(default=10, ge=1, le=100),
    severity: Optional[str] = Query(default=None, regex="^(critical|high|medium|low)$"),
    user: dict = Depends(get_current_user)
):
    """
    Get vulnerabilities for the dashboard
    
    - **limit**: Maximum number of vulnerabilities to return (1-100)
    - **severity**: Filter by severity (critical, high, medium, low)
    
    Returns the most recent vulnerabilities sorted by severity and date.
    """
    try:
        if not neon_service.is_enabled():
            raise HTTPException(status_code=503, detail="Database not configured")
        
        # Query to get vulnerabilities from scans
        # Since vulnerabilities are stored in the findings JSONB field, we need to extract them
        severity_filter = ""
        if severity:
            severity_filter = f"AND finding->>'severity' = '{severity.upper()}'"
        
        query = f"""
            WITH vulnerability_findings AS (
                SELECT 
                    s.id as scan_id,
                    s.created_at,
                    jsonb_array_elements(s.findings) as finding
                FROM scans s
                WHERE s.user_id = $1
                AND s.status = 'completed'
                AND s.findings IS NOT NULL
                AND jsonb_array_length(s.findings) > 0
            ),
            ranked_vulnerabilities AS (
                SELECT 
                    scan_id,
                    finding,
                    created_at,
                    CASE finding->>'severity'
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        WHEN 'LOW' THEN 4
                        ELSE 5
                    END as severity_rank
                FROM vulnerability_findings
                WHERE finding->>'type' IS NOT NULL
                {severity_filter}
            )
            SELECT 
                scan_id::text,
                finding,
                created_at
            FROM ranked_vulnerabilities
            ORDER BY severity_rank ASC, created_at DESC
            LIMIT $2
        """
        
        result = await neon_service.execute(query, user["id"], limit)
        
        vulnerabilities = []
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for row in result:
            finding = row["finding"]
            severity_val = finding.get("severity", "LOW").lower()
            
            vuln = VulnerabilityItem(
                id=f"{row['scan_id']}-{len(vulnerabilities)}",
                title=finding.get("title", finding.get("type", "Unknown Vulnerability")),
                severity=severity_val,
                cvss=finding.get("cvss"),
                cve=finding.get("cve"),
                package=finding.get("package"),
                version=finding.get("version"),
                fixed_version=finding.get("fixed_version"),
                description=finding.get("description", finding.get("message")),
                file_path=finding.get("file"),
                line_number=finding.get("line"),
                scan_id=row["scan_id"],
                created_at=row["created_at"].isoformat()
            )
            vulnerabilities.append(vuln)
            
            if severity_val in counts:
                counts[severity_val] += 1
        
        # Get total counts across all scans
        count_query = """
            WITH all_findings AS (
                SELECT jsonb_array_elements(findings) as finding
                FROM scans
                WHERE user_id = $1
                AND status = 'completed'
                AND findings IS NOT NULL
            )
            SELECT 
                COUNT(*) FILTER (WHERE finding->>'severity' = 'CRITICAL') as critical,
                COUNT(*) FILTER (WHERE finding->>'severity' = 'HIGH') as high,
                COUNT(*) FILTER (WHERE finding->>'severity' = 'MEDIUM') as medium,
                COUNT(*) FILTER (WHERE finding->>'severity' = 'LOW') as low,
                COUNT(*) as total
            FROM all_findings
        """
        
        count_result = await neon_service.execute(count_query, user["id"])
        total_counts = count_result[0] if count_result else {
            "critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0
        }
        
        return VulnerabilitiesResponse(
            vulnerabilities=vulnerabilities,
            total_count=total_counts.get("total", 0),
            critical_count=total_counts.get("critical", 0),
            high_count=total_counts.get("high", 0),
            medium_count=total_counts.get("medium", 0),
            low_count=total_counts.get("low", 0)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching vulnerabilities: {str(e)}"
        )


@router.get("/scans/recent", response_model=RecentScansResponse)
async def get_recent_scans(
    limit: int = Query(default=5, ge=1, le=50),
    user: dict = Depends(get_current_user)
):
    """
    Get recent scan activity for the dashboard
    
    - **limit**: Maximum number of scans to return (1-50)
    
    Returns recent scans with their finding counts.
    """
    try:
        if not neon_service.is_enabled():
            raise HTTPException(status_code=503, detail="Database not configured")
        
        query = """
            SELECT 
                id::text,
                scan_type,
                workflow_mode,
                status,
                findings_count,
                findings,
                created_at,
                completed_at
            FROM scans
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """
        
        result = await neon_service.execute(query, user["id"], limit)
        
        scans = []
        for row in result:
            # Count severities from findings
            critical_count = 0
            high_count = 0
            
            if row["findings"]:
                for finding in row["findings"]:
                    severity = finding.get("severity", "").upper()
                    if severity == "CRITICAL":
                        critical_count += 1
                    elif severity == "HIGH":
                        high_count += 1
            
            scan = ScanActivityItem(
                id=row["id"],
                type="scan",
                title=f"{row['scan_type'].title()} Scan",
                timestamp=row["created_at"].isoformat(),
                status=row["status"],
                findings_count=row["findings_count"] or 0,
                critical_count=critical_count,
                high_count=high_count,
                scan_type=row["scan_type"],
                workflow_mode=row["workflow_mode"]
            )
            scans.append(scan)
        
        return RecentScansResponse(
            scans=scans,
            total_count=len(scans)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching recent scans: {str(e)}"
        )


@router.get("/analytics/trends", response_model=TrendsResponse)
async def get_vulnerability_trends(
    days: int = Query(default=30, ge=7, le=90),
    user: dict = Depends(get_current_user)
):
    """
    Get vulnerability trends over time
    
    - **days**: Number of days to include in trends (7-90)
    
    Returns vulnerability counts grouped by week.
    """
    try:
        if not neon_service.is_enabled():
            raise HTTPException(status_code=503, detail="Database not configured")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query to get weekly vulnerability trends
        query = """
            WITH weekly_findings AS (
                SELECT 
                    date_trunc('week', s.created_at) as week_start,
                    jsonb_array_elements(s.findings) as finding
                FROM scans s
                WHERE s.user_id = $1
                AND s.status = 'completed'
                AND s.created_at >= $2
                AND s.created_at <= $3
                AND s.findings IS NOT NULL
            )
            SELECT 
                week_start,
                COUNT(*) FILTER (WHERE finding->>'severity' = 'CRITICAL') as critical,
                COUNT(*) FILTER (WHERE finding->>'severity' = 'HIGH') as high,
                COUNT(*) FILTER (WHERE finding->>'severity' = 'MEDIUM') as medium,
                COUNT(*) FILTER (WHERE finding->>'severity' = 'LOW') as low,
                COUNT(*) as total
            FROM weekly_findings
            GROUP BY week_start
            ORDER BY week_start ASC
        """
        
        result = await neon_service.execute(query, user["id"], start_date, end_date)
        
        trends = []
        for row in result:
            trend = TrendDataPoint(
                period=row["week_start"].strftime("Week of %b %d"),
                critical=row.get("critical", 0),
                high=row.get("high", 0),
                medium=row.get("medium", 0),
                low=row.get("low", 0),
                total=row.get("total", 0)
            )
            trends.append(trend)
        
        # If no data, return empty trends for the requested period
        if not trends:
            # Create empty data points for each week
            weeks = days // 7
            for i in range(weeks):
                week_start = start_date + timedelta(weeks=i)
                trends.append(TrendDataPoint(
                    period=week_start.strftime("Week of %b %d"),
                    critical=0,
                    high=0,
                    medium=0,
                    low=0,
                    total=0
                ))
        
        return TrendsResponse(
            trends=trends,
            period_days=days
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching trends: {str(e)}"
        )


# AI Fix Endpoint
class AIFixRequest(BaseModel):
    """Request model for AI fix generation"""
    vulnerability_id: str = Field(..., description="Vulnerability ID (scan_id-index)")
    scan_id: str = Field(..., description="Scan ID containing the vulnerability")
    code_context: Optional[str] = Field(None, description="Code context (auto-fetched if not provided)")


class AIFixResponse(BaseModel):
    """Response model for AI fix generation"""
    fixed_code: str
    explanation: str
    diff: Optional[str] = None
    confidence: float
    provider: str  # "kimi" or "openai"
    is_security_fix: bool
    security_principle: Optional[str] = None


@router.post("/ai-fix", response_model=AIFixResponse)
async def generate_ai_fix(
    request: AIFixRequest = Body(...),
    user: dict = Depends(get_current_user)
):
    """
    Generate an AI-powered security fix for a vulnerability.
    
    - **vulnerability_id**: ID of the vulnerability (format: scan_id-index)
    - **scan_id**: ID of the scan containing the vulnerability
    - **code_context**: Optional code context (will be fetched from scan if not provided)
    
    **IMPORTANT**: This endpoint ONLY generates fixes for security vulnerabilities.
    It does NOT:
    - Generate new features
    - Refactor non-security code  
    - Act as a general code assistant
    
    Token limits are enforced to control costs.
    """
    try:
        if not neon_service.is_enabled():
            raise HTTPException(status_code=503, detail="Database not configured")
        
        # Fetch vulnerability details from database
        query = """
            SELECT 
                s.findings,
                s.metadata
            FROM scans s
            WHERE s.id = $1
            AND s.user_id = $2
        """
        
        result = await neon_service.execute(query, request.scan_id, user["id"])
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Scan not found or you don't have permission to access it"
            )
        
        # Extract the specific vulnerability
        findings = result[0].get("findings", [])
        
        # Parse vulnerability_id to get index
        try:
            vuln_index = int(request.vulnerability_id.split("-")[-1])
        except:
            raise HTTPException(status_code=400, detail="Invalid vulnerability_id format")
        
        if vuln_index >= len(findings):
            raise HTTPException(status_code=404, detail="Vulnerability not found in scan")
        
        vulnerability = findings[vuln_index]
        
        # Get code context (use provided or fetch from vulnerability)
        code_context = request.code_context
        if not code_context:
            # Try to get context from vulnerability
            file_content = vulnerability.get("file_content")
            if file_content:
                code_context = file_content
            else:
                # Get snippet around the vulnerable line
                code_context = vulnerability.get("code", "")
                if not code_context:
                    raise HTTPException(
                        status_code=400,
                        detail="No code context available. Please provide code_context in the request."
                    )
        
        file_path = vulnerability.get("file", "unknown")
        
        # Generate fix using AI service
        fix_result = await ai_fix_service.generate_security_fix(
            vulnerability=vulnerability,
            code_context=code_context,
            file_path=file_path
        )
        
        # Check if fix was successful
        if "error" in fix_result:
            raise HTTPException(
                status_code=400,
                detail=fix_result.get("message", fix_result["error"])
            )
        
        if not fix_result.get("is_security_fix"):
            raise HTTPException(
                status_code=400,
                detail="This service only generates fixes for security vulnerabilities"
            )
        
        return AIFixResponse(
            fixed_code=fix_result["fixed_code"],
            explanation=fix_result.get("explanation", "No explanation provided"),
            diff=fix_result.get("diff"),
            confidence=fix_result.get("confidence", 0.0),
            provider=fix_result.get("provider", "unknown"),
            is_security_fix=True,
            security_principle=fix_result.get("security_principle")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating AI fix: {str(e)}"
        )
