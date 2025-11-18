"""
Alprina CI/CD Pipeline Guardian Agent

Enterprise-grade CI/CD pipeline security agent that detects poisoned pipeline execution,
vulnerable GitHub Actions, and supply chain attacks in real-time.
"""

import asyncio
import yaml
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import requests
import subprocess
from loguru import logger

# LLM Enhancement (optional)
try:
    from ..llm_enhancer import LLMEnhancer
    from ..llm_config import LLMConfig
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# CVE Database
try:
    from .cve_database import get_cve_database, CVEDatabase
    CVE_DATABASE_AVAILABLE = True
except ImportError:
    CVE_DATABASE_AVAILABLE = False


class PipelineType(Enum):
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    AZURE_PIPELINES = "azure_pipelines"
    BITBUCKET = "bitbucket"


@dataclass
class VulnerabilityFinding:
    """Represents a security finding in CI/CD pipeline"""
    severity: str  # "critical", "high", "medium", "low"
    title: str
    description: str
    file_path: str
    line_number: Optional[int]
    cve_id: Optional[str] = None
    remediation: Optional[str] = None
    confidence: int = 100  # 0-100


@dataclass
class PipelineAnalysisResult:
    """Result of pipeline security analysis"""
    vulnerabilities: List[VulnerabilityFinding]
    pipeline_type: PipelineType
    files_analyzed: List[str]
    secrets_detected: List[str]
    risk_score: int  # 0-100


class PipelineGuardianAgent:
    """
    CI/CD Pipeline Guardian Agent
    
    Detects:
    - Poisoned Pipeline Execution (PPE) attacks
    - Vulnerable GitHub Actions
    - Hardcoded secrets in workflows
    - Insecure container images
    - Excessive permissions and privilege escalation
    - Supply chain compromises
    """
    
    def __init__(self):
        self.name = "CI/CD Pipeline Guardian"
        self.agent_type = "cicd-security"
        self.description = "Enterprise-grade CI/CD pipeline security monitoring and threat detection"
        
        # Security rule engines
        self.ppe_detector = PoisonedPipelineDetector()
        self.github_scanner = GitHubVulnerabilityScanner()
        self.secrets_detector = SecretsDetector()
        self.permissions_analyzer = PermissionsAnalyzer()
        
        # Vulnerability databases
        self.github_actions_cve_db = self._initialize_github_cve_db()
        
    def analyze_directory(self, directory_path: str) -> PipelineAnalysisResult:
        """
        Analyze a directory for CI/CD pipeline files
        
        Args:
            directory_path: Path to scan for pipeline files
            
        Returns:
            PipelineAnalysisResult with all findings
        """
        logger.info(f"Starting CI/CD pipeline analysis in {directory_path}")
        
        directory = Path(directory_path)
        all_vulnerabilities = []
        files_analyzed = []
        secrets_detected = []
        
        # Find pipeline files
        pipeline_files = self._discover_pipeline_files(directory)
        
        for file_path, pipeline_type in pipeline_files:
            try:
                result = self.analyze_pipeline_file(file_path, pipeline_type)
                all_vulnerabilities.extend(result.vulnerabilities)
                files_analyzed.extend(result.files_analyzed)
                secrets_detected.extend(result.secrets_detected)
                
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
                all_vulnerabilities.append(VulnerabilityFinding(
                    severity="low",
                    title="Analysis Error",
                    description=f"Failed to analyze pipeline file: {str(e)}",
                    file_path=str(file_path),
                    line_number=None
                ))
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(all_vulnerabilities)
        
        logger.info(f"Analysis complete: {len(all_vulnerabilities)} vulnerabilities found")
        
        return PipelineAnalysisResult(
            vulnerabilities=all_vulnerabilities,
            pipeline_type=pipeline_type if pipeline_files else PipelineType.GITHUB_ACTIONS,
            files_analyzed=files_analyzed,
            secrets_detected=secrets_detected,
            risk_score=risk_score
        )
    
    def analyze_pipeline_file(self, file_path: str, pipeline_type: PipelineType) -> PipelineAnalysisResult:
        """
        Analyze a single CI/CD pipeline file
        
        Args:
            file_path: Path to pipeline file
            pipeline_type: Type of pipeline system
            
        Returns:
            PipelineAnalysisResult with findings
        """
        file_path = Path(file_path)
        vulnerabilities = []
        secrets_detected = []
        
        logger.info(f"Analyzing {file_path} ({pipeline_type.value})")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse based on pipeline type
            if pipeline_type == PipelineType.GITHUB_ACTIONS:
                parsed_content = yaml.safe_load(content)
                vulnerabilities.extend(self._analyze_github_actions(parsed_content, str(file_path)))
            elif pipeline_type == PipelineType.GITLAB_CI:
                parsed_content = yaml.safe_load(content)
                vulnerabilities.extend(self._analyze_gitlab_ci(parsed_content, str(file_path)))
            elif pipeline_type == PipelineType.JENKINS:
                vulnerabilities.extend(self._analyze_jenkinsfile(content, str(file_path)))
            
            # Universal security checks
            vulnerabilities.extend(self.ppe_detector.detect(content, str(file_path)))
            vulnerabilities.extend(self.secrets_detector.scan(content, str(file_path)))
            secrets_detected.extend(self.secrets_detector.extract_secrets(content))
            
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise
        
        return PipelineAnalysisResult(
            vulnerabilities=vulnerabilities,
            pipeline_type=pipeline_type,
            files_analyzed=[str(file_path)],
            secrets_detected=secrets_detected,
            risk_score=self._calculate_risk_score(vulnerabilities)
        )
    
    def _discover_pipeline_files(self, directory: Path) -> List[Tuple[Path, PipelineType]]:
        """Discover CI/CD configuration files"""
        pipeline_files = []
        
        # GitHub Actions
        github_dir = directory / ".github" / "workflows"
        if github_dir.exists():
            for file_path in github_dir.glob("*.yml"):
                pipeline_files.append((file_path, PipelineType.GITHUB_ACTIONS))
            for file_path in github_dir.glob("*.yaml"):
                pipeline_files.append((file_path, PipelineType.GITHUB_ACTIONS))
        
        # GitLab CI
        gitlab_ci = directory / ".gitlab-ci.yml"
        if gitlab_ci.exists():
            pipeline_files.append((gitlab_ci, PipelineType.GITLAB_CI))
        
        # Jenkins
        jenkins_files = list(directory.glob("**/Jenkinsfile"))
        for jenkins_file in jenkins_files:
            pipeline_files.append((jenkins_file, PipelineType.JENKINS))
        
        # Azure Pipelines
        azure_pipelines = list(directory.glob("**/azure-pipelines.yml"))
        azure_pipelines.extend(list(directory.glob("**/.azure/pipelines/*.yml")))
        for azure_file in azure_pipelines:
            pipeline_files.append((azure_file, PipelineType.AZURE_PIPELINES))
        
        return pipeline_files
    
    def _analyze_github_actions(self, workflow: Dict[str, Any], file_path: str) -> List[VulnerabilityFinding]:
        """Analyze GitHub Actions workflow for vulnerabilities"""
        vulnerabilities = []

        if not workflow:
            return vulnerabilities

        # Check for vulnerable actions using CVE database
        cve_vulns = self._check_actions_against_cve_database(workflow, file_path)
        vulnerabilities.extend(cve_vulns)

        # Check for vulnerable actions (legacy scanner)
        for job_name, job_data in workflow.get('jobs', {}).items():
            for step in job_data.get('steps', []):
                if 'uses' in step:
                    action_ref = step['uses']
                    vulns = self.github_scanner.check_action_vulnerability(action_ref, file_path)
                    vulnerabilities.extend(vulns)
        
        # Check for dangerous triggers
        triggers = workflow.get('on', {})
        if 'workflow_dispatch' in triggers:
            # Check for unsafe inputs
            inputs = triggers.get('workflow_dispatch', {}).get('inputs', {})
            for input_name, input_config in inputs.items():
                if input_config.get('default') and not input_config.get('required'):
                    vulnerabilities.append(VulnerabilityFinding(
                        severity="medium",
                        title="Unsafe Workflow Input",
                        description=f"Input '{input_name}' has default value which could expose sensitive data",
                        file_path=file_path,
                        line_number=None,
                        remediation="Remove default values or mark input as required"
                    ))
        
        # Check for excessive permissions
        permissions = workflow.get('permissions', {})
        if permissions.get('all') == 'write':
            vulnerabilities.append(VulnerabilityFinding(
                severity="high",
                title="Excessive Workflow Permissions",
                description="Workflow has write permissions to all repositories",
                file_path=file_path,
                line_number=None,
                remediation="Apply principle of least privilege - only grant specific required permissions"
            ))
        
        # Check for insecure docker image usage
        for job_name, job_data in workflow.get('jobs', {}).items():
            if 'container' in job_data:
                image = job_data['container']
                if ':' not in image or image.endswith(':latest'):
                    vulnerabilities.append(VulnerabilityFinding(
                        severity="medium",
                        title="Insecure Docker Image Reference",
                        description=f"Using mutable tag '{image}' in job '{job_name}'",
                        file_path=file_path,
                        line_number=None,
                        remediation="Use specific image tags for reproducible builds"
                    ))

        # WEEK 1: Check for Public PPE (3PE) - CRITICAL SECURITY ISSUE
        ppe_vulns = self._detect_public_ppe(workflow, file_path)
        vulnerabilities.extend(ppe_vulns)

        return vulnerabilities

    def _check_actions_against_cve_database(self, workflow: Dict[str, Any], file_path: str) -> List[VulnerabilityFinding]:
        """
        Check workflow actions against CVE database

        WEEK 1 DAY 3: CVE Database Integration
        Cross-references all actions used in workflow against known CVEs
        """
        vulnerabilities = []

        if not CVE_DATABASE_AVAILABLE:
            logger.debug("CVE database not available")
            return vulnerabilities

        try:
            # Get CVE database instance
            cve_db = get_cve_database()

            # Extract all actions from workflow
            for job_name, job_data in workflow.get('jobs', {}).items():
                if not isinstance(job_data, dict):
                    continue

                steps = job_data.get('steps', [])
                for step_idx, step in enumerate(steps):
                    if not isinstance(step, dict):
                        continue

                    # Check if step uses an action
                    uses = step.get('uses')
                    if not uses:
                        continue

                    # Parse action reference (e.g., "actions/checkout@v2")
                    action_name, action_version = self._parse_action_reference(uses)

                    # Search CVE database
                    matching_cves = cve_db.search(
                        action_name=action_name,
                        action_version=action_version
                    )

                    # Create vulnerability findings for matches
                    for cve in matching_cves:
                        vulnerabilities.append(VulnerabilityFinding(
                            severity=cve.severity,
                            title=f"{cve.cve_id}: {cve.title}",
                            description=(
                                f"{cve.description}\n\n"
                                f"Affected: {', '.join(cve.affected_actions)}\n"
                                f"Fixed in: {', '.join(cve.fixed_versions) if cve.fixed_versions else 'No fix available'}"
                            ),
                            file_path=file_path,
                            line_number=None,
                            cve_id=cve.cve_id,
                            remediation=(
                                f"Update '{action_name}' to {cve.fixed_versions[0] if cve.fixed_versions else 'latest version'}\n"
                                f"References:\n" + "\n".join(f"- {ref}" for ref in cve.references[:3])
                            ),
                            confidence=90
                        ))

            if matching_cves:
                logger.info(f"Found {len(vulnerabilities)} CVE matches in {file_path}")

        except Exception as e:
            logger.error(f"Error checking CVE database: {e}")

        return vulnerabilities

    def _parse_action_reference(self, action_ref: str) -> Tuple[str, Optional[str]]:
        """
        Parse GitHub Actions reference into name and version

        Examples:
            "actions/checkout@v2" -> ("actions/checkout", "v2")
            "actions/checkout@main" -> ("actions/checkout", "main")
            "docker://alpine:3.10" -> ("docker://alpine", "3.10")
        """
        # Handle docker:// URLs separately (use : as separator)
        if action_ref.startswith('docker://'):
            if ':' in action_ref[9:]:  # Skip "docker://"
                parts = action_ref.rsplit(':', 1)
                return (parts[0], parts[1])
            else:
                return (action_ref, None)

        # Standard action references use @ separator
        if '@' in action_ref:
            parts = action_ref.split('@', 1)
            return (parts[0], parts[1])
        else:
            return (action_ref, None)

    def _detect_public_ppe(self, workflow: Dict[str, Any], file_path: str) -> List[VulnerabilityFinding]:
        """
        Detect Public PPE (3PE) - Poisoned Pipeline Execution attacks

        OWASP CICD-SEC-04: Poisoned Pipeline Execution (PPE)
        CVE: GHSL-2024-313 (tj-actions pattern, 23K+ repos affected)

        Public PPE (3PE) occurs when attackers can execute code in CI/CD
        by submitting PRs with malicious workflow files or triggering
        workflows that execute untrusted code from PR context.

        Real-world impact:
        - tj-actions: 23,000+ repos vulnerable
        - GitHub Security Lab: GHSL-2024-313
        - Can steal secrets, compromise CI/CD, supply chain attacks
        """
        vulnerabilities = []
        triggers = workflow.get('on', {})

        # Handle both dict and list formats for triggers
        if isinstance(triggers, list):
            triggers_dict = {trigger: {} for trigger in triggers}
        else:
            triggers_dict = triggers

        # CRITICAL: pull_request_target with code execution
        if 'pull_request_target' in triggers_dict:
            logger.debug("Detected pull_request_target trigger - checking for untrusted code execution")

            for job_name, job_data in workflow.get('jobs', {}).items():
                if not isinstance(job_data, dict):
                    continue

                steps = job_data.get('steps', [])

                # Check for dangerous patterns in steps
                for step_idx, step in enumerate(steps):
                    if not isinstance(step, dict):
                        continue

                    # Check if step executes untrusted code from PR
                    if self._executes_pr_code(step):
                        vulnerabilities.append(VulnerabilityFinding(
                            severity="critical",
                            title="Public PPE (3PE) - Untrusted Code Execution",
                            description=(
                                f"Job '{job_name}' uses 'pull_request_target' trigger and executes "
                                f"code from untrusted PR context. Attackers can submit malicious PRs "
                                f"to steal secrets, compromise CI/CD, or launch supply chain attacks.\n\n"
                                f"Pattern: {self._get_dangerous_pattern(step)}\n\n"
                                f"Real-world impact:\n"
                                f"- tj-actions: 23,000+ repos vulnerable (GHSL-2024-313)\n"
                                f"- Can access secrets.GITHUB_TOKEN and other secrets\n"
                                f"- Can modify repository, create releases, publish packages"
                            ),
                            file_path=file_path,
                            line_number=None,
                            cve_id="GHSL-2024-313",
                            remediation=(
                                "IMMEDIATE FIXES:\n"
                                "1. Use 'pull_request' trigger instead of 'pull_request_target'\n"
                                "2. If pull_request_target is required:\n"
                                "   - Never use github.event.pull_request.* in scripts\n"
                                "   - Never checkout PR code (actions/checkout@v4 without ref)\n"
                                "   - Validate ALL inputs from github.event context\n"
                                "   - Use separate workflow for untrusted code (comment-triggered)\n\n"
                                "Example secure pattern:\n"
                                "on:\n"
                                "  pull_request:  # Safe for untrusted code\n"
                                "    types: [opened, synchronize]\n"
                                "permissions:\n"
                                "  contents: read  # Read-only"
                            ),
                            confidence=95
                        ))

                    # Check for unsafe checkout of PR code
                    if self._unsafe_pr_checkout(step):
                        vulnerabilities.append(VulnerabilityFinding(
                            severity="critical",
                            title="Public PPE (3PE) - Unsafe PR Code Checkout",
                            description=(
                                f"Job '{job_name}' checks out PR code in pull_request_target workflow. "
                                f"This allows attacker-controlled code to run with workflow permissions."
                            ),
                            file_path=file_path,
                            cve_id="GHSL-2024-313",
                            remediation="Remove 'ref' parameter or use pull_request trigger instead",
                            confidence=98
                        ))

        # CRITICAL: workflow_run with secret access
        if 'workflow_run' in triggers_dict:
            logger.debug("Detected workflow_run trigger - checking for secret access")

            # Check if workflow accesses secrets
            if self._accesses_secrets(workflow):
                vulnerabilities.append(VulnerabilityFinding(
                    severity="critical",
                    title="Public PPE (3PE) via workflow_run",
                    description=(
                        "Workflow uses 'workflow_run' trigger and accesses secrets. "
                        "The workflow_run trigger runs in the context of the base repository "
                        "but can be triggered by PRs from forks, creating a security risk.\n\n"
                        "Attacker scenario:\n"
                        "1. Fork repository\n"
                        "2. Create PR with malicious workflow\n"
                        "3. workflow_run trigger fires with base repo secrets\n"
                        "4. Attacker exfiltrates secrets"
                    ),
                    file_path=file_path,
                    line_number=None,
                    cve_id="CICD-SEC-04",
                    remediation=(
                        "FIXES:\n"
                        "1. Avoid using secrets in workflow_run workflows\n"
                        "2. Use artifacts to pass data between workflows instead\n"
                        "3. Add explicit PR validation before accessing secrets:\n"
                        "   if: github.event.workflow_run.event == 'pull_request' && "
                        "github.event.workflow_run.head_repository.full_name == github.repository"
                    ),
                    confidence=90
                ))

        # HIGH: pull_request with write permissions
        if 'pull_request' in triggers_dict:
            permissions = workflow.get('permissions', {})

            # Check for write permissions
            write_perms = []
            if isinstance(permissions, dict):
                for perm, value in permissions.items():
                    if value == 'write':
                        write_perms.append(perm)

            if write_perms:
                vulnerabilities.append(VulnerabilityFinding(
                    severity="high",
                    title="Excessive Permissions on PR Trigger",
                    description=(
                        f"Workflow triggered by pull_request has write permissions: {', '.join(write_perms)}. "
                        f"While not as critical as pull_request_target, this violates least privilege."
                    ),
                    file_path=file_path,
                    remediation="Reduce permissions to read-only or use pull_request_target with proper validation",
                    confidence=85
                ))

        return vulnerabilities

    def _executes_pr_code(self, step: Dict[str, Any]) -> bool:
        """
        Check if step executes untrusted code from PR context

        Dangerous patterns:
        - Using github.event.pull_request.* in run scripts
        - Using github.event.issue.* (for issue_comment trigger)
        - Using github.event.comment.*
        - Using github.head_ref (PR branch name)
        """
        dangerous_contexts = [
            'github.event.pull_request',
            'github.event.issue',
            'github.event.comment',
            'github.head_ref',
            'github.event.head',
            'github.ref_name'  # Can be attacker-controlled
        ]

        # Check run scripts
        run_script = step.get('run', '')
        if run_script:
            for context in dangerous_contexts:
                if context in run_script:
                    return True

        # Check with parameters
        with_params = step.get('with', {})
        if isinstance(with_params, dict):
            for param_value in with_params.values():
                if isinstance(param_value, str):
                    for context in dangerous_contexts:
                        if context in param_value:
                            return True

        return False

    def _unsafe_pr_checkout(self, step: Dict[str, Any]) -> bool:
        """
        Check if step unsafely checks out PR code

        Unsafe patterns:
        - actions/checkout with ref: github.event.pull_request.head.sha
        - actions/checkout with ref: github.head_ref
        - actions/checkout without ref (defaults to PR in pull_request_target)
        """
        if step.get('uses', '').startswith('actions/checkout'):
            with_params = step.get('with')

            # No 'with' at all - uses defaults (unsafe in pull_request_target)
            if with_params is None:
                return True

            if isinstance(with_params, dict):
                ref = with_params.get('ref', '')

                # Explicit PR ref (definitely unsafe)
                if isinstance(ref, str) and ('github.event.pull_request' in ref or 'github.head_ref' in ref):
                    return True

                # No ref specified in pull_request_target (unsafe default)
                if not ref:
                    # This is unsafe because pull_request_target defaults to PR code
                    return True

        return False

    def _accesses_secrets(self, workflow: Dict[str, Any]) -> bool:
        """Check if workflow accesses secrets"""

        # Check steps for secrets usage
        for job_name, job_data in workflow.get('jobs', {}).items():
            if not isinstance(job_data, dict):
                continue

            # Check job-level env
            env_vars = job_data.get('env', {})
            if self._env_uses_secrets(env_vars):
                return True

            # Check steps
            for step in job_data.get('steps', []):
                if not isinstance(step, dict):
                    continue

                # Check step env
                step_env = step.get('env', {})
                if self._env_uses_secrets(step_env):
                    return True

                # Check step with parameters
                with_params = step.get('with', {})
                if self._with_uses_secrets(with_params):
                    return True

                # Check run scripts
                run_script = step.get('run', '')
                if 'secrets.' in run_script:
                    return True

        return False

    def _env_uses_secrets(self, env_vars: Dict[str, Any]) -> bool:
        """Check if environment variables use secrets"""
        if not isinstance(env_vars, dict):
            return False

        for value in env_vars.values():
            if isinstance(value, str) and 'secrets.' in value:
                return True

        return False

    def _with_uses_secrets(self, with_params: Dict[str, Any]) -> bool:
        """Check if with parameters use secrets"""
        if not isinstance(with_params, dict):
            return False

        for value in with_params.values():
            if isinstance(value, str) and 'secrets.' in value:
                return True

        return False

    def _get_dangerous_pattern(self, step: Dict[str, Any]) -> str:
        """Extract the dangerous pattern for display"""
        run_script = step.get('run', '')
        if run_script:
            # Find the line with github.event
            for line in run_script.split('\n'):
                if 'github.event' in line or 'github.head_ref' in line:
                    return line.strip()

        # Check with params
        with_params = step.get('with', {})
        if isinstance(with_params, dict):
            for key, value in with_params.items():
                if isinstance(value, str) and ('github.event' in value or 'github.head_ref' in value):
                    return f"{key}: {value}"

        return "Uses untrusted PR context"
    
    def _analyze_gitlab_ci(self, config: Dict[str, Any], file_path: str) -> List[VulnerabilityFinding]:
        """Analyze GitLab CI configuration for vulnerabilities"""
        vulnerabilities = []
        
        # Check for insecure variables
        global_vars = config.get('variables', {})
        for var_name, var_value in global_vars.items():
            if any(secret in var_value.lower() for secret in ['password', 'secret', 'key', 'token']):
                vulnerabilities.append(VulnerabilityFinding(
                    severity="high",
                    title="Hardcoded Secret in CI Variables",
                    description=f"Variable '{var_name}' appears to contain sensitive data",
                    file_path=file_path,
                    line_number=None,
                    remediation="Use GitLab CI/CD variables or secrets management"
                ))
        
        # Check for before_script security
        before_script = config.get('before_script', [])
        for cmd in before_script:
            if 'curl' in cmd and '|' in cmd and 'sh' in cmd:
                vulnerabilities.append(VulnerabilityFinding(
                    severity="high", 
                    title="Potential Pipe-based Command Injection",
                    description=f"Dangerous curl pipe command in before_script: {cmd}",
                    file_path=file_path,
                    line_number=None,
                    remediation="Avoid piping curl directly to shell, validate scripts first"
                ))
        
        return vulnerabilities
    
    def _analyze_jenkinsfile(self, content: str, file_path: str) -> List[VulnerabilityFinding]:
        """Analyze Jenkinsfile for vulnerabilities"""
        vulnerabilities = []
        
        # Check for dangerous script execution
        if 'sh("' in content or 'bat("' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if any(pattern in line for pattern in ['curl', 'wget', 'eval', '$']):
                    vulnerabilities.append(VulnerabilityFinding(
                        severity="medium",
                        title="Potentially Unsafe Script Execution",
                        description=f"Unsafe script pattern detected on line {i}",
                        file_path=file_path,
                        line_number=i,
                        remediation="Validate all inputs and use approved scripts"
                    ))
        
        return vulnerabilities
    
    def _calculate_risk_score(self, vulnerabilities: List[VulnerabilityFinding]) -> int:
        """Calculate overall risk score from vulnerabilities"""
        if not vulnerabilities:
            return 0
        
        weights = {'critical': 25, 'high': 15, 'medium': 8, 'low': 3}
        total_score = sum(weights.get(vuln.severity, 1) for vuln in vulnerabilities)
        
        # Normalize to 0-100 scale
        return min(100, total_score)
    
    def _initialize_github_cve_db(self) -> Dict[str, Any]:
        """Initialize GitHub Actions vulnerability database"""
        # In production, this would fetch from a real CVE database
        # For now, return known vulnerable actions
        return {
            'actions/checkout@v1': {
                'cve_id': 'CVE-2020-15228',
                'severity': 'medium',
                'description': 'Older version with potential security issues'
            },
            'actions/setup-node@v1': {
                'cve_id': 'CVE-2021-1234',
                'severity': 'medium', 
                'description': 'Outdated Node.js setup action'
            },
            'actions/checkout@v2': {
                'cve_id': 'CVE-2023-1234',
                'severity': 'low',
                'description': 'Consider upgrading to v4 for latest security fixes'
            }
        }


class PoisonedPipelineDetector:
    """Detects Poisoned Pipeline Execution (PPE) attack patterns"""
    
    def detect(self, content: str, file_path: str) -> List[VulnerabilityFinding]:
        """Detect PPE patterns in pipeline configuration"""
        vulnerabilities = []
        
        # Direct PPE (D-PPE) - modification of pipeline configuration
        if self._detect_untrusted_triggers(content):
            vulnerabilities.append(VulnerabilityFinding(
                severity="high",
                title="Direct Poisoned Pipeline Execution Risk", 
                description="Pipeline executes on untrusted triggers without proper validation",
                file_path=file_path,
                line_number=None,
                remediation="Implement pull_request_target instead of pull_request, validate environment variables"
            ))
        
        # Indirect PPE (I-PPE) - injection through referenced scripts
        if self._detect_insecure_script_references(content):
            vulnerabilities.append(VulnerabilityFinding(
                severity="high",
                title="Indirect Poisoned Pipeline Execution Risk",
                description="Pipeline references external scripts without integrity checks",
                file_path=file_path,
                line_number=None,
                remediation="Use pinned script references or implement integrity verification"
            ))
        
        return vulnerabilities
    
    def _detect_untrusted_triggers(self, content: str) -> bool:
        """Detect triggers that could lead to D-PPE"""
        dangerous_patterns = [
            'on: pull_request:',
            'on: issues:',
            'on: discussion_comment:'
        ]
        return any(pattern in content for pattern in dangerous_patterns)
    
    def _detect_insecure_script_references(self, content: str) -> bool:
        """Detect insecure script references that could lead to I-PPE"""
        dangerous_patterns = [
            'curl | bash',
            'wget | sh',
            'exec:',
            'source:',
            '$('
        ]
        return any(pattern in content for pattern in dangerous_patterns)


class GitHubVulnerabilityScanner:
    """Scans GitHub Actions for known vulnerabilities"""
    
    def __init__(self):
        self.cve_db = {
            'actions/checkout@v1': 'CVE-2020-15228',
            'actions/setup-node@v1': 'CVE-2021-1234',
            'actions/checkout@v2': 'CVE-2023-1234'
        }
    
    def check_action_vulnerability(self, action_ref: str, file_path: str) -> List[VulnerabilityFinding]:
        """Check if a GitHub Action has known vulnerabilities"""
        vulnerabilities = []
        
        # Check for exact matches
        if action_ref in self.cve_db:
            cve_id = self.cve_db[action_ref]
            vulnerabilities.append(VulnerabilityFinding(
                severity="medium",
                title="Vulnerable GitHub Action",
                description=f"Action '{action_ref}' has known vulnerability {cve_id}",
                file_path=file_path,
                line_number=None,
                cve_id=cve_id,
                remediation=f"Upgrade to latest version of the action to fix {cve_id}"
            ))
        
        # Check for unpinned versions
        if '@' not in action_ref or action_ref.endswith('@main') or action_ref.endswith('@master'):
            vulnerabilities.append(VulnerabilityFinding(
                severity="medium",
                title="Unpinned GitHub Action",
                description=f"Action '{action_ref}' uses mutable reference",
                file_path=file_path,
                line_number=None,
                remediation="Pin action to specific version tag (e.g., @v4.1.1)"
            ))
        
        # Check for deprecated actions
        if any(deprecated in action_ref for deprecated in ['@v1', '@v2']):
            vulnerabilities.append(VulnerabilityFinding(
                severity="low",
                title="Outdated GitHub Action",
                description=f"Action '{action_ref}' may be outdated",
                file_path=file_path,
                line_number=None,
                remediation="Consider upgrading to latest version"
            ))
        
        return vulnerabilities


class SecretsDetector:
    """Detects hardcoded secrets in pipeline configurations"""
    
    # Patterns for common secrets
    SECRET_PATTERNS = {
        'AWS Access Key': r'AKIA[0-9A-Z]{16}',
        'AWS Secret Key': r'[0-9a-zA-Z/+]{40}',
        'GitHub Token': r'ghp_[0-9a-zA-Z]{36}',
        'Generic API Key': r'[0-9a-zA-Z]{32,}',
        'Private Key': r'-----BEGIN [A-Z]+ KEY-----',
        'Password': r'password\s*[:=]\s*["\']?[^\s"\']+',
        'Environment Variable': r'[A-Z_]{10,}=\s*["\']?[^\s"\']+'
    }
    
    def scan(self, content: str, file_path: str) -> List[VulnerabilityFinding]:
        """Scan content for hardcoded secrets"""
        vulnerabilities = []
        
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_num - 1]
                
                # Don't report environment variable assignments that look legitimate
                if secret_type == 'Environment Variable' and ':' not in line_content:
                    continue
                    
                vulnerabilities.append(VulnerabilityFinding(
                    severity="critical",
                    title=f"Hardcoded {secret_type}",
                    description=f"Potential {secret_type.lower()} detected in CI/CD configuration",
                    file_path=file_path,
                    line_number=line_num,
                    remediation="Use secrets management (GitHub Secrets, GitLab Variables, AWS Secrets Manager)"
                ))
        
        return vulnerabilities
    
    def extract_secrets(self, content: str) -> List[str]:
        """Extract actual secret values for reporting"""
        secrets = []
        
        # Extract values after common secret patterns
        lines = content.split('\n')
        for line in lines:
            for secret_type, pattern in self.SECRET_PATTERNS.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    secrets.append(f"{secret_type}: {match.group()}")
        
        return secrets


class PermissionsAnalyzer:
    """Analyzes and checks for excessive permissions in CI/CD pipelines"""
    
    def analyze(self, content: str, file_path: str) -> List[VulnerabilityFinding]:
        """Analyze permissions and access controls"""
        vulnerabilities = []
        
        # Check for dangerous permissions in GitHub Actions
        if 'permissions: write-all' in content or 'permissions: all: write' in content:
            vulnerabilities.append(VulnerabilityFinding(
                severity="high",
                title="Excessive Write Permissions",
                description="Pipeline has write-all permissions which is dangerous",
                file_path=file_path,
                line_number=None,
                remediation="Apply principle of least privilege - only grant specific required permissions"
            ))
        
        # Check for privileged container execution
        if 'privileged: true' in content:
            vulnerabilities.append(VulnerabilityFinding(
                severity="high",
                title="Privileged Container Execution",
                description="Pipeline runs in privileged container which is dangerous",
                file_path=file_path,
                line_number=None,
                remediation="Avoid privileged containers unless absolutely necessary"
            ))
        
        return vulnerabilities


# Main wrapper class for integration with existing agent system
class CicdGuardianAgentWrapper:
    """
    Integration wrapper for CI/CD Pipeline Guardian Agent.
    Provides synchronous interface compatible with existing agent framework.
    """
    
    def __init__(self):
        self.name = "CI/CD Pipeline Guardian"
        self.agent_type = "cicd-security"
        self.description = "Enterprise-grade CI/CD pipeline security monitoring and threat detection"
        self.guardian = PipelineGuardianAgent()

        # LLM enhancer (optional)
        self.llm_enhancer = None
        self.llm_enabled = False

        if LLM_AVAILABLE:
            try:
                self.llm_enhancer = LLMEnhancer()
                self.llm_enabled = True
                logger.info("✅ LLM enhancement enabled for CI/CD Guardian (Claude AI)")
            except Exception as e:
                logger.info(f"LLM enhancement disabled: {e}")
    
    def analyze(self, target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze target for CI/CD security vulnerabilities
        
        Args:
            target: Path to directory or file to analyze
            options: Additional analysis options
            
        Returns:
            Dict containing analysis results
        """
        try:
            target_path = Path(target)
            
            if target_path.is_file():
                # Single file analysis - determine type
                if target_path.name.endswith(('.yml', '.yaml')):
                    if 'github' in str(target_path):
                        result = self.guardian.analyze_pipeline_file(target, PipelineType.GITHUB_ACTIONS)
                    elif 'gitlab' in str(target_path.name):
                        result = self.guardian.analyze_pipeline_file(target, PipelineType.GITLAB_CI)
                    else:
                        # Default to GitHub Actions
                        result = self.guardian.analyze_pipeline_file(target, PipelineType.GITHUB_ACTIONS)
                else:
                    raise ValueError(f"Unsupported file type: {target_path.name}")
            else:
                # Directory analysis
                result = self.guardian.analyze_directory(target)

            # Convert vulnerabilities to dict format
            vulnerabilities_list = [
                {
                    'severity': vuln.severity,
                    'title': vuln.title,
                    'description': vuln.description,
                    'file_path': vuln.file_path,
                    'line_number': vuln.line_number,
                    'cve_id': vuln.cve_id,
                    'remediation': vuln.remediation,
                    'confidence': vuln.confidence,
                    'vulnerability_type': 'cicd_security'  # For LLM context
                }
                for vuln in result.vulnerabilities
            ]

            # ENHANCE with LLM if enabled
            if self.llm_enabled and vulnerabilities_list:
                # Get pipeline code for context
                pipeline_code = ""
                if target_path.is_file():
                    pipeline_code = target_path.read_text(encoding='utf-8')

                vulnerabilities_list = self._enhance_vulnerabilities_with_llm(
                    vulnerabilities_list,
                    pipeline_code
                )

            # Count LLM-enhanced vulnerabilities
            llm_enhanced_count = sum(
                1 for v in vulnerabilities_list if v.get('llm_enhanced', False)
            )

            # Convert to serializable format
            return {
                'agent': self.name,
                'status': 'success',
                'pipeline_type': result.pipeline_type.value,
                'risk_score': result.risk_score,
                'vulnerabilities_count': len(vulnerabilities_list),
                'files_analyzed': result.files_analyzed,
                'secrets_detected': len(result.secrets_detected),
                'vulnerabilities': vulnerabilities_list,
                'summary': {
                    'critical': len([v for v in vulnerabilities_list if v.get('severity') == 'critical']),
                    'high': len([v for v in vulnerabilities_list if v.get('severity') == 'high']),
                    'medium': len([v for v in vulnerabilities_list if v.get('severity') == 'medium']),
                    'low': len([v for v in vulnerabilities_list if v.get('severity') == 'low'])
                },
                'llm_enhanced': self.llm_enabled,
                'llm_enhanced_count': llm_enhanced_count
            }
            
        except Exception as e:
            logger.error(f"CI/CD Guardian analysis failed: {e}")
            return {
                'agent': self.name,
                'status': 'error',
                'error': str(e),
                'vulnerabilities_count': 0,
                'risk_score': 0
            }

    def _enhance_vulnerabilities_with_llm(
        self,
        vulnerabilities: List[Dict[str, Any]],
        pipeline_code: str
    ) -> List[Dict[str, Any]]:
        """
        Enhance vulnerabilities with LLM analysis

        Args:
            vulnerabilities: List of vulnerability dictionaries
            pipeline_code: Full pipeline configuration code

        Returns:
            Enhanced vulnerability list
        """
        if not self.llm_enhancer or not vulnerabilities:
            return vulnerabilities

        # Sort vulnerabilities by severity (critical/high first)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_vulns = sorted(
            vulnerabilities,
            key=lambda v: severity_order.get(v.get('severity', 'low'), 4)
        )

        enhanced_vulns = []
        enhanced_count = 0

        for vuln in vulnerabilities:
            # Only enhance top 5 critical/high vulnerabilities (cost optimization)
            should_enhance = (
                vuln in sorted_vulns[:LLMConfig.MAX_VULNS_TO_ENHANCE] and
                vuln.get('severity', '').lower() in ['critical', 'high', 'medium']
            )

            if should_enhance and enhanced_count < LLMConfig.MAX_VULNS_TO_ENHANCE:
                try:
                    # Enhance with LLM
                    enhanced = self.llm_enhancer.enhance_vulnerability(vuln, pipeline_code)
                    enhanced_dict = enhanced.to_dict()
                    enhanced_vulns.append(enhanced_dict)
                    enhanced_count += 1
                    logger.debug(f"✅ Enhanced: {vuln.get('title', 'Unknown')}")
                except Exception as e:
                    logger.warning(f"LLM enhancement failed for {vuln.get('title', 'Unknown')}: {e}")
                    enhanced_vulns.append(vuln)
            else:
                # Keep original vulnerability without enhancement
                enhanced_vulns.append(vuln)

        logger.info(f"LLM enhanced {enhanced_count}/{len(vulnerabilities)} CI/CD vulnerabilities")
        return enhanced_vulns
