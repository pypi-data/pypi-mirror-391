"""
Test Public PPE (3PE) Detection - Week 1 Implementation

Tests for GHSL-2024-313 (tj-actions pattern) and OWASP CICD-SEC-04
"""

import pytest
import sys
from pathlib import Path

# Add CLI to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alprina_cli.agents.cicd_guardian.cicd_guardian import (
    PipelineGuardianAgent,
    VulnerabilityFinding,
    PipelineType
)


class TestPublicPPEDetection:
    """Test suite for Public PPE (3PE) detection"""

    def setup_method(self):
        """Set up test fixtures"""
        self.agent = PipelineGuardianAgent()

    def test_detects_pull_request_target_with_pr_code(self):
        """Test detection of pull_request_target executing PR code"""
        workflow = {
            'name': 'Vulnerable Workflow',
            'on': ['pull_request_target'],
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'name': 'Echo PR title',
                            'run': 'echo ${{ github.event.pull_request.title }}'
                        }
                    ]
                }
            }
        }

        vulns = self.agent._detect_public_ppe(workflow, 'test.yml')

        assert len(vulns) >= 1
        assert any(v.severity == "critical" for v in vulns)
        assert any("3PE" in v.title or "PPE" in v.title for v in vulns)
        assert any(v.cve_id == "GHSL-2024-313" for v in vulns)

    def test_detects_pull_request_target_with_unsafe_checkout(self):
        """Test detection of unsafe checkout in pull_request_target"""
        workflow = {
            'name': 'Unsafe Checkout',
            'on': {'pull_request_target': {'types': ['opened']}},
            'jobs': {
                'build': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'uses': 'actions/checkout@v4',
                            'with': {
                                'ref': '${{ github.event.pull_request.head.sha }}'
                            }
                        },
                        {
                            'run': 'npm install && npm test'
                        }
                    ]
                }
            }
        }

        vulns = self.agent._detect_public_ppe(workflow, 'test.yml')

        assert len(vulns) >= 1
        assert any(v.severity == "critical" for v in vulns)
        assert any("Unsafe PR Code Checkout" in v.title for v in vulns)

    def test_detects_workflow_run_with_secrets(self):
        """Test detection of workflow_run with secret access"""
        workflow = {
            'name': 'workflow_run with secrets',
            'on': {
                'workflow_run': {
                    'workflows': ['CI'],
                    'types': ['completed']
                }
            },
            'jobs': {
                'deploy': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'name': 'Deploy',
                            'run': 'deploy.sh',
                            'env': {
                                'API_KEY': '${{ secrets.DEPLOY_KEY }}'
                            }
                        }
                    ]
                }
            }
        }

        vulns = self.agent._detect_public_ppe(workflow, 'test.yml')

        assert len(vulns) >= 1
        assert any(v.severity == "critical" for v in vulns)
        assert any("workflow_run" in v.title for v in vulns)
        assert any(v.cve_id == "CICD-SEC-04" for v in vulns)

    def test_detects_pull_request_with_write_permissions(self):
        """Test detection of excessive permissions on pull_request"""
        workflow = {
            'name': 'PR with write perms',
            'on': ['pull_request'],
            'permissions': {
                'contents': 'write',
                'issues': 'write'
            },
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'run': 'echo "test"'}
                    ]
                }
            }
        }

        vulns = self.agent._detect_public_ppe(workflow, 'test.yml')

        assert len(vulns) >= 1
        assert any(v.severity == "high" for v in vulns)
        assert any("Excessive Permissions" in v.title for v in vulns)

    def test_no_false_positive_safe_pull_request(self):
        """Test that safe pull_request workflows don't trigger"""
        workflow = {
            'name': 'Safe Workflow',
            'on': ['pull_request'],
            'permissions': {
                'contents': 'read'
            },
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'run': 'npm test'
                        }
                    ]
                }
            }
        }

        vulns = self.agent._detect_public_ppe(workflow, 'test.yml')

        # Should not detect any critical PPE vulnerabilities
        critical_ppe = [v for v in vulns if v.severity == "critical" and "PPE" in v.title]
        assert len(critical_ppe) == 0

    def test_detects_github_head_ref_usage(self):
        """Test detection of github.head_ref in pull_request_target"""
        workflow = {
            'name': 'head_ref usage',
            'on': ['pull_request_target'],
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'name': 'Use branch name',
                            'run': 'git checkout ${{ github.head_ref }}'
                        }
                    ]
                }
            }
        }

        vulns = self.agent._detect_public_ppe(workflow, 'test.yml')

        assert len(vulns) >= 1
        assert any(v.severity == "critical" for v in vulns)
        assert any("github.head_ref" in v.description for v in vulns)

    def test_detects_comment_trigger_with_pr_data(self):
        """Test detection of issue_comment with PR data"""
        workflow = {
            'name': 'Comment trigger',
            'on': ['pull_request_target'],
            'jobs': {
                'comment': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'run': 'echo "${{ github.event.comment.body }}" | bash'
                        }
                    ]
                }
            }
        }

        vulns = self.agent._detect_public_ppe(workflow, 'test.yml')

        assert len(vulns) >= 1
        assert any(v.severity == "critical" for v in vulns)

    def test_tj_actions_pattern(self):
        """Test the exact tj-actions vulnerable pattern (GHSL-2024-313)"""
        workflow = {
            'name': 'tj-actions pattern',
            'on': {
                'pull_request_target': {
                    'types': ['opened', 'synchronize']
                }
            },
            'jobs': {
                'changed-files': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'uses': 'tj-actions/changed-files@v40',
                            'with': {
                                'files': '${{ github.event.pull_request.title }}'
                            }
                        }
                    ]
                }
            }
        }

        vulns = self.agent._detect_public_ppe(workflow, 'test.yml')

        # Should detect both unsafe checkout AND PR data usage
        assert len(vulns) >= 2
        critical_vulns = [v for v in vulns if v.severity == "critical"]
        assert len(critical_vulns) >= 1

    def test_remediation_includes_fix(self):
        """Test that remediation includes actionable fixes"""
        workflow = {
            'on': ['pull_request_target'],
            'jobs': {
                'test': {
                    'steps': [
                        {'run': 'echo ${{ github.event.pull_request.body }}'}
                    ]
                }
            }
        }

        vulns = self.agent._detect_public_ppe(workflow, 'test.yml')

        assert len(vulns) >= 1
        assert vulns[0].remediation is not None
        assert "pull_request" in vulns[0].remediation.lower()


class TestHelperMethods:
    """Test helper methods for PPE detection"""

    def setup_method(self):
        self.agent = PipelineGuardianAgent()

    def test_executes_pr_code_detects_event_usage(self):
        """Test _executes_pr_code detects github.event.pull_request"""
        step = {
            'run': 'echo "${{ github.event.pull_request.title }}"'
        }
        assert self.agent._executes_pr_code(step) is True

    def test_executes_pr_code_detects_head_ref(self):
        """Test _executes_pr_code detects github.head_ref"""
        step = {
            'run': 'git checkout ${{ github.head_ref }}'
        }
        assert self.agent._executes_pr_code(step) is True

    def test_executes_pr_code_detects_with_params(self):
        """Test _executes_pr_code detects PR data in with params"""
        step = {
            'uses': 'some/action@v1',
            'with': {
                'title': '${{ github.event.pull_request.title }}'
            }
        }
        assert self.agent._executes_pr_code(step) is True

    def test_executes_pr_code_safe_pattern(self):
        """Test _executes_pr_code doesn't flag safe patterns"""
        step = {
            'run': 'npm test'
        }
        assert self.agent._executes_pr_code(step) is False

    def test_unsafe_pr_checkout_detects_explicit_ref(self):
        """Test _unsafe_pr_checkout detects explicit PR ref"""
        step = {
            'uses': 'actions/checkout@v4',
            'with': {
                'ref': '${{ github.event.pull_request.head.sha }}'
            }
        }
        assert self.agent._unsafe_pr_checkout(step) is True

    def test_unsafe_pr_checkout_detects_missing_ref(self):
        """Test _unsafe_pr_checkout detects missing ref (unsafe default)"""
        step = {
            'uses': 'actions/checkout@v4',
            'with': {}
        }
        assert self.agent._unsafe_pr_checkout(step) is True

    def test_unsafe_pr_checkout_safe_explicit_ref(self):
        """Test _unsafe_pr_checkout allows safe explicit ref"""
        step = {
            'uses': 'actions/checkout@v4',
            'with': {
                'ref': 'main'
            }
        }
        assert self.agent._unsafe_pr_checkout(step) is False

    def test_accesses_secrets_detects_env(self):
        """Test _accesses_secrets detects secrets in env"""
        workflow = {
            'jobs': {
                'test': {
                    'steps': [
                        {
                            'env': {
                                'TOKEN': '${{ secrets.GITHUB_TOKEN }}'
                            }
                        }
                    ]
                }
            }
        }
        assert self.agent._accesses_secrets(workflow) is True

    def test_accesses_secrets_detects_run_script(self):
        """Test _accesses_secrets detects secrets in run scripts"""
        workflow = {
            'jobs': {
                'test': {
                    'steps': [
                        {
                            'run': 'echo ${{ secrets.API_KEY }}'
                        }
                    ]
                }
            }
        }
        assert self.agent._accesses_secrets(workflow) is True

    def test_accesses_secrets_safe_workflow(self):
        """Test _accesses_secrets doesn't flag workflows without secrets"""
        workflow = {
            'jobs': {
                'test': {
                    'steps': [
                        {
                            'run': 'npm test'
                        }
                    ]
                }
            }
        }
        assert self.agent._accesses_secrets(workflow) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
